import React, { useEffect, useState, useRef } from 'react';

const PDFViewer = () => {
  const [pdfList, setPdfList] = useState([]);
  const [selectedFile, setSelectedFile] = useState(null);
  const [currentPage, setCurrentPage] = useState(0);
  const [totalPages, setTotalPages] = useState(null);
  const [image, setImage] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const token = localStorage.getItem('token');
  const dpi = 300;

  // Sử dụng useRef để lưu cache các trang đã tải
  const imageCache = useRef({});

  // Fetch danh sách PDF từ backend
  useEffect(() => {
    if (!token) {
      setError("Missing token. Please login.");
      return;
    }
    const fetchPdfList = async () => {
      try {
        const res = await fetch('http://localhost:912/api/pdf/pdf', {
          headers: { 'Authorization': `Bearer ${token}` },
        });
        if (!res.ok) {
          throw new Error(`Error ${res.status}: ${res.statusText}`);
        }
        const data = await res.json();
        if (data && Array.isArray(data.files)) {
          setPdfList(data.files);
          if (data.files.length > 0) {
            setSelectedFile(data.files[0]);
          }
        } else {
          setPdfList([]);
        }
      } catch (err) {
        console.error("Fetch PDF list error:", err);
        setError(err.message);
      }
    };
    fetchPdfList();
  }, [token]);

  // Reset trang và totalPages khi file thay đổi
  useEffect(() => {
    setCurrentPage(0);
    setTotalPages(null);
    setError(null);
    setImage(null);
  }, [selectedFile]);

  // Fetch trang hiện tại với caching, sử dụng async/await và AbortController
  useEffect(() => {
    if (!selectedFile || !token) return;

    const cacheKey = `${selectedFile}-${currentPage}-${dpi}`;
    // Nếu trang đã có trong cache, dùng luôn
    if (imageCache.current[cacheKey]) {
      setImage(imageCache.current[cacheKey].image);
      setTotalPages(imageCache.current[cacheKey].totalPages);
      return;
    }

    const controller = new AbortController();

    const fetchPage = async () => {
      setLoading(true);
      try {
        const res = await fetch(
          `http://localhost:912/api/pdf/pdf/view/${selectedFile}?page=${currentPage}&dpi=${dpi}`,
          {
            headers: { 'Authorization': `Bearer ${token}` },
            signal: controller.signal,
          }
        );
        if (!res.ok) {
          throw new Error(`Error ${res.status}: ${res.statusText}`);
        }
        const data = await res.json();
        if (data && data.image) {
          setImage(data.image);
          setTotalPages(data.total_pages);
          setError(null);
          // Lưu cache cho trang hiện tại
          imageCache.current[cacheKey] = {
            image: data.image,
            totalPages: data.total_pages,
          };

          // Prefetch trang kế tiếp nếu có
          if (data.total_pages && currentPage < data.total_pages - 1) {
            const nextCacheKey = `${selectedFile}-${currentPage + 1}-${dpi}`;
            if (!imageCache.current[nextCacheKey]) {
              fetch(
                `http://localhost:912/api/pdf/pdf/view/${selectedFile}?page=${currentPage + 1}&dpi=${dpi}`,
                {
                  headers: { 'Authorization': `Bearer ${token}` },
                }
              )
                .then(r => {
                  if (!r.ok) throw new Error(`Error ${r.status}`);
                  return r.json();
                })
                .then(d => {
                  if (d && d.image) {
                    imageCache.current[nextCacheKey] = {
                      image: d.image,
                      totalPages: d.total_pages,
                    };
                  }
                })
                .catch(err => {
                  console.error("Prefetch error:", err);
                });
            }
          }
        } else {
          setImage(null);
        }
      } catch (err) {
        if (err.name !== 'AbortError') {
          console.error("Fetch PDF page error:", err);
          setError(err.message);
        }
      } finally {
        setLoading(false);
      }
    };

    fetchPage();

    return () => {
      controller.abort();
    };
  }, [selectedFile, currentPage, token, dpi]);

  const handlePrevious = () => {
    if (currentPage > 0) {
      setCurrentPage(prev => prev - 1);
    }
  };

  const handleNext = () => {
    if (totalPages !== null && currentPage < totalPages - 1) {
      setCurrentPage(prev => prev + 1);
    }
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
              <span>
                Page {currentPage + 1}
                {totalPages ? ` of ${totalPages}` : ''}
              </span>
              <button
                onClick={handleNext}
                disabled={totalPages !== null ? currentPage >= totalPages - 1 : false}
              >
                Next
              </button>
            </div>
          </div>
          <div style={styles.imageContainer}>
            {loading ? (
              <p>Loading page...</p>
            ) : image ? (
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
