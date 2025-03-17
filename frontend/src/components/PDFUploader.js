import React, { useState, useCallback } from 'react';

const PDFUploader = () => {
  const [files, setFiles] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadMessage, setUploadMessage] = useState('');
  const token = localStorage.getItem('token');

  const handleFileChange = useCallback((e) => {
    setFiles(e.target.files);
    setUploadMessage('');
  }, []);

  const handleUpload = useCallback(async () => {
    if (!files || files.length === 0) {
      alert('Please choose at least one PDF file!');
      return;
    }

    const formData = new FormData();
    for (let i = 0; i < files.length; i++) {
      formData.append('files', files[i]);
    }
  
    setUploading(true);
    setUploadMessage('');
    try {
      const response = await fetch('http://localhost:912/api/pdf/upload', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData,  
      });
      if (response.ok) {
        const data = await response.json();
        setUploadMessage('Upload successful!');
        // Reset file input sau khi upload thành công
        setFiles(null);
        // Nếu bạn muốn reset value của input, bạn có thể dùng ref (ở đây chỉ cập nhật state)
      } else {
        const err = await response.json();
        setUploadMessage('Upload failed: ' + err.detail);
      }
    } catch (error) {
      setUploadMessage('Error when uploading: ' + error.message);
    } finally {
      setUploading(false);
    }
  }, [files, token]);

  return (
    <div style={styles.container}>
      <input
        type="file"
        accept="application/pdf"
        multiple
        onChange={handleFileChange}
        style={styles.input}
      />
      <button onClick={handleUpload} style={styles.button} disabled={uploading}>
        {uploading ? 'Uploading...' : 'Upload PDF'}
      </button>
      {uploadMessage && <div style={styles.message}>{uploadMessage}</div>}
    </div>
  );
};

const styles = {
  container: {
    display: 'flex',
    alignItems: 'center',
    gap: '10px',
    flexDirection: 'column',
    maxWidth: '400px',
    margin: '20px auto',
  },
  input: {
    width: '100%',
  },
  button: {
    padding: '10px 15px',
    backgroundColor: '#9b59b6',
    color: '#fff',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
    width: '100%',
  },
  message: {
    marginTop: '10px',
    fontSize: '14px',
    color: '#333',
  },
};

export default PDFUploader;
