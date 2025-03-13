import React, { useEffect, useState } from 'react';

const PDFViewer = () => {
  const [pdfList, setPdfList] = useState([]);
  const [selectedFile, setSelectedFile] = useState(null);
  const [currentPage, setCurrentPage] = useState(0);
  const [image, setImage] = useState(null);
  const [error, setError] = useState(null);
  const token = localStorage.getItem('token');
  const dpi = 200;

  // Fetch danh sách PDF từ backend
  useEffect(() => {
    if (!token) {
      setError("Missing token. Please login.");
      return;
    }
    fetch('http://localhost:912/api/pdf/pdf', {
      headers: { 'Authorization': `Bearer ${token}` },
    })
      .then((res) => {
        if (!res.ok) {
          throw new Error(`Error ${res.status}: ${res.statusText}`);
        }
        return res.json();
      })
      .then((data) => {
        if (data && Array.isArray(data.files)) {
          setPdfList(data.files);
          if (data.files.length > 0) {
            setSelectedFile(data.files[0]);
          }
        } else {
          setPdfList([]);
        }
      })
      .catch((err) => {
        console.error("Fetch PDF list error:", err);
        setError(err.message);
      });
  }, [token]);

  // Reset trang khi file thay đổi
  useEffect(() => {
    setCurrentPage(0);
  }, [selectedFile]);

  // Lazy loading: fetch trang hiện tại
  useEffect(() => {
    if (!selectedFile || !token) return;
    fetch(`http://localhost:912/api/pdf/pdf/view/${selectedFile}?page=${currentPage}&dpi=${dpi}`, {
      headers: { 'Authorization': `Bearer ${token}` },
    })
      .then((res) => {
        if (!res.ok) {
          throw new Error(`Error ${res.status}: ${res.statusText}`);
        }
        return res.json();
      })
      .then((data) => {
        if (data && Array.isArray(data.images) && data.images.length > 0) {
          setImage(data.images[0]);
        } else {
          setImage(null);
        }
      })
      .catch((err) => {
        console.error("Fetch PDF page error:", err);
        setError(err.message);
      });
  }, [selectedFile, currentPage, token, dpi]);

  const handlePrevious = () => {
    if (currentPage > 0) {
      setCurrentPage(prev => prev - 1);
    }
  };

  const handleNext = () => {
    setCurrentPage(prev => prev + 1);
  };

  return (
    <div style={styles.container}>
      {error && <div style={styles.error}>Error: {error}</div>}
      {pdfList.length === 0 ? (
        <p>No PDF file available.</p>
      ) : (
        <>
          <div style={styles.topControls}>
            <select
              value={selectedFile}
              onChange={(e) => setSelectedFile(e.target.value)}
              style={styles.select}
            >
              {pdfList.map((file, index) => (
                <option key={index} value={file}>
                  {file}
                </option>
              ))}
            </select>
            <div style={styles.pagination}>
              <button onClick={handlePrevious} disabled={currentPage === 0}>
                Previous
              </button>
              <span>Page {currentPage + 1}</span>
              <button onClick={handleNext}>Next</button>
            </div>
          </div>
          <div style={styles.imageContainer}>
            {image ? (
              <img
                src={`data:image/jpeg;base64,${image}`}
                alt={`Page ${currentPage + 1}`}
                style={styles.image}
              />
            ) : (
              <p>No page available to display.</p>
            )}
          </div>
        </>
      )}
    </div>
  );
};

const styles = {
  container: {
    padding: '20px',
    fontFamily: 'Arial, sans-serif',
  },
  error: {
    color: 'red',
    marginBottom: '10px',
  },
  topControls: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: '15px',
  },
  select: {
    padding: '8px',
    marginRight: '15px',
    borderRadius: '4px',
    border: '1px solid #ccc',
    fontSize: '16px',
    maxWidth: '300px',
  },
  pagination: {
    display: 'flex',
    alignItems: 'center',
    gap: '10px',
  },
  imageContainer: {
    display: 'flex',
    flexDirection: 'column',
    gap: '15px',
  },
  image: {
    maxWidth: '100%',
    borderRadius: '4px',
  },
};

export default PDFViewer;