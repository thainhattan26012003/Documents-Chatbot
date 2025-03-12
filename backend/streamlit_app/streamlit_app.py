import streamlit as st
from utils import rag_flow, process_pdf_and_store, check_and_upload_minio, extract_all_pages_images

st.set_page_config(
    page_title="Demo AI Extract Documents App",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

if "uploaded_files" not in st.session_state:
    st.session_state["uploaded_files"] = {}

with st.sidebar:
    st.subheader("Ask a question:")
    question = st.text_input("Enter your question here")
    if st.button("Submit question"):
        if question.strip():
            with st.spinner("Thinking..."):
                answer = rag_flow(question)
                st.write("**Answer:**", answer)
        else:
            st.warning("Please enter a question before submitting.")
            
    st.subheader("Upload PDF(s)")
    
    if "uploaded_files" not in st.session_state:
        st.session_state["uploaded_files"] = {}

    # If file is already uploaded, show success message and do not show the file uploader
    if st.session_state["uploaded_files"]:
        st.success("Các file PDF đã được upload lên MinIO!")
    else:
        uploaded_files = st.file_uploader(
            label="Upload one or more PDF files",
            type=["pdf"],
            accept_multiple_files=True
        )

        if st.button("Upload file(s)"):
            if uploaded_files:
                for uploaded_file in uploaded_files:
                    filename = uploaded_file.name
                    if filename not in st.session_state["uploaded_files"]:
                        file_bytes, new_upload, pdf_file_name = check_and_upload_minio(uploaded_file)
                        if file_bytes is not None:
                            if new_upload:
                                # If the file is new, process it
                                result = process_pdf_and_store(file_bytes, pdf_file_name)
                                if result["status"] == "success":
                                    st.session_state["uploaded_files"][filename] = file_bytes
                                    st.success(f"Processed '{filename}' successfully!")
                                else:
                                    st.error(f"Failed to process '{filename}': {result['message']}")
                            else:
                                # If the file already exists, just store the bytes
                                st.info(f"File '{filename}' already exists and has been processed.")
                                st.session_state["uploaded_files"][filename] = file_bytes
            else:
                st.warning("Please select at least one PDF file before clicking 'Upload file(s)'.")


st.subheader("PDF Viewer")

if st.session_state["uploaded_files"]:
    pdf_names = list(st.session_state["uploaded_files"].keys())
    selected_pdf = st.selectbox("Select a PDF to view", pdf_names)

    if selected_pdf:
        file_bytes = st.session_state["uploaded_files"][selected_pdf]
        pdf_pages = extract_all_pages_images(file_bytes)

        st.write(f"Showing pages for: **{selected_pdf}**")
        
        with st.expander("View PDF Pages", expanded=True):
            for idx, page_img in enumerate(pdf_pages, start=1):
                st.image(page_img, caption=f"Page {idx}", use_container_width=True)
else:
    st.info("No PDFs have been uploaded yet. Please upload using the left panel.")
