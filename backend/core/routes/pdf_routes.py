from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from auth import get_current_user
from pdf_processing import check_and_upload_minio, process_pdf_and_store, extract_all_pages_images_cached, normalize_filename
from minio.error import S3Error
from format import MINIO_BUCKET, QDRANT_COLLECTION, minio_client, vectordb_provider
from typing import Optional, List
import base64
import cv2 as cv

router = APIRouter()

@router.post("/upload")
def upload_pdf(files: List[UploadFile] = File(...), user=Depends(get_current_user)):
    if user["role"] != "manager":
        raise HTTPException(status_code=403, detail="Permission denied. Only managers can upload PDF files.")
    for file in files:
        file_bytes, is_new, normalized_filename = check_and_upload_minio(file)
        if file_bytes is None:
            raise HTTPException(status_code=400, detail=f"Upload failed for {normalized_filename}.")
        if is_new:
            result = process_pdf_and_store(file_bytes, normalized_filename)
            if result.get("status") != "success":
                raise HTTPException(status_code=500, detail=f"Processing failed for {normalized_filename}: {result.get('message')}")
    return {"msg": "All files uploaded and processed successfully."}

@router.post("/delete_files")
def delete_files(file: UploadFile = File(...), user=Depends(get_current_user)):
    if user["role"] != "manager":
        raise HTTPException(status_code=403, detail="Permission denied. Only managers can delete PDF files.")
    
    try:
        normalized_filename = normalize_filename(file.filename)
        minio_client.remove_object(MINIO_BUCKET, normalized_filename)
        vectordb_provider.delete_vectors(QDRANT_COLLECTION, normalized_filename)
    except S3Error as err:
        if err.code == "NoSuchKey":
            raise HTTPException(status_code=404, detail=f"File not found: {normalized_filename}")
        else:
            raise HTTPException(status_code=500, detail=f"Error occurred while deleting file: {err}")
    
    return {"msg": "Files deleted successfully."}

@router.get("/pdf")
def list_pdfs(current_user=Depends(get_current_user)):
    objects = minio_client.list_objects(MINIO_BUCKET)
    files = [obj.object_name for obj in objects]
    return {"files": files}


@router.get("/pdf/view/{filename}")
def view_pdf(filename: str, page: Optional[int] = None, dpi: int = 150, user=Depends(get_current_user)):
    try:
        response = minio_client.get_object(MINIO_BUCKET, filename)
        file_bytes = response.read()
        images = extract_all_pages_images_cached(file_bytes, dpi=dpi)
        
        # Lazy loading
        if page is not None:
            if page < 0 or page >= len(images):
                raise HTTPException(status_code=400, detail="Invalid page number")
            images = [images[page]]
        
        images_base64 = []
        for img in images:
            success, buffer = cv.imencode('.jpg', img)
            if not success:
                continue
            img_base64 = base64.b64encode(buffer).decode('utf-8')
            images_base64.append(img_base64)
            
        return {"filename": filename, "images": images_base64}
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"File not found: {filename}")
