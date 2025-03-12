from fastapi import FastAPI, UploadFile, File
import cv2
import numpy as np
import pytesseract
from fastapi.responses import JSONResponse

pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'

app = FastAPI()

@app.post("/extract_texts")
async def perform_ocr(image: UploadFile = File(...)):
    contents = await image.read()
    nparr = np.frombuffer(contents, dtype=np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    desired_width = 1000
    desired_height = 1000
    height, width = img.shape[:2]
    if width < desired_width or height < desired_height:
        scale_factor = max(desired_width / width, desired_height / height)
        img = cv2.resize(img, None, fx=scale_factor, fy=scale_factor, interpolation=cv2.INTER_CUBIC)
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    _, binary = cv2.threshold(blur, 150, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    clean = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel, iterations=1)

    custom_config = r'--oem 3 --psm 6 -l vie'
    text = pytesseract.image_to_string(clean, config=custom_config)
    
    return JSONResponse(status_code=200, content={"data": text})