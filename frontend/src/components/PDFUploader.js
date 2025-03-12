import React, { useState } from 'react';

const PDFUploader = () => {
  const [files, setFiles] = useState(null);
  const token = localStorage.getItem('token');

  const handleFileChange = (e) => {
    setFiles(e.target.files);
  };

  const handleUpload = async () => {
    if (!files || files.length === 0) {
      alert('Please choose at least one PDF file!');
      return;
    }
    const formData = new FormData();
    for (let i = 0; i < files.length; i++) {
      formData.append('files', files[i]);
    }
  
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
        alert("Upload successful: " + JSON.stringify(data.results, null, 2));
      } else {
        const err = await response.json();
        alert('Upload failed: ' + err.detail);
      }
    } catch (error) {
      alert('Error when uploading: ' + error.message);
    }
  };

  return (
    <div style={styles.container}>
      <input
        type="file"
        accept="application/pdf"
        multiple
        onChange={handleFileChange}
        style={styles.input}
      />
      <button onClick={handleUpload} style={styles.button}>
        Upload PDF
      </button>
    </div>
  );
};

const styles = {
  container: {
    display: 'flex',
    alignItems: 'center',
    gap: '10px',
  },
  input: {
    flex: 1,
  },
  button: {
    padding: '10px 15px',
    backgroundColor: '#9b59b6',
    color: '#fff',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
  },
};

export default PDFUploader;
