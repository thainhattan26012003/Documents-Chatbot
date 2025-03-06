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
    fetch('http://ec2-54-86-234-1.compute-1.amazonaws.com:912/api/pdf/pdf', {
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
    fetch(`http://ec2-54-86-234-1.compute-1.amazonaws.com:912/api/pdf/pdf/view/${selectedFile}?page=${currentPage}&dpi=${dpi}`, {
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

// import React, { useEffect, useState } from 'react';

// const PDFViewer = () => {
//   const [pdfList, setPdfList] = useState([]);
//   const [selectedFile, setSelectedFile] = useState(null);
//   const [currentPage, setCurrentPage] = useState(0);
//   const [image, setImage] = useState(null);
//   const [error, setError] = useState(null);
//   const token = localStorage.getItem('token');
//   const dpi = 200;

//   // Lấy danh sách PDF từ backend
//   useEffect(() => {
//     if (!token) {
//       setError("Missing token. Please login.");
//       return;
//     }
//     fetch('http://ec2-54-86-234-1.compute-1.amazonaws.com:912/pdf', {
//       headers: { 'Authorization': `Bearer ${token}` },
//     })
//       .then((res) => {
//         if (!res.ok) {
//           throw new Error(`Error ${res.status}: ${res.statusText}`);
//         }
//         return res.json();
//       })
//       .then((data) => {
//         if (data && Array.isArray(data.files)) {
//           setPdfList(data.files);
//           if (data.files.length > 0) {
//             setSelectedFile(data.files[0]);
//           }
//         } else {
//           setPdfList([]);
//         }
//       })
//       .catch((err) => {
//         console.error("Fetch PDF list error:", err);
//         setError(err.message);
//       });
//   }, [token]);

//   // Reset trang khi file được chọn thay đổi
//   useEffect(() => {
//     setCurrentPage(0);
//   }, [selectedFile]);

//   // Lazy loading: fetch trang hiện tại của file PDF đã chọn
//   useEffect(() => {
//     if (!selectedFile || !token) return;
//     fetch(`http://ec2-54-86-234-1.compute-1.amazonaws.com:912/pdf/view/${selectedFile}?page=${currentPage}&dpi=${dpi}`, {
//       headers: { 'Authorization': `Bearer ${token}` },
//     })
//       .then((res) => {
//         if (!res.ok) {
//           throw new Error(`Error ${res.status}: ${res.statusText}`);
//         }
//         return res.json();
//       })
//       .then((data) => {
//         if (data && Array.isArray(data.images) && data.images.length > 0) {
//           setImage(data.images[0]);
//         } else {
//           setImage(null);
//         }
//       })
//       .catch((err) => {
//         console.error("Fetch PDF page error:", err);
//         setError(err.message);
//       });
//   }, [selectedFile, currentPage, token, dpi]);

//   // Hàm chuyển trang
//   const handlePrevious = () => {
//     if (currentPage > 0) setCurrentPage(prev => prev - 1);
//   };

//   const handleNext = () => {
//     setCurrentPage(prev => prev + 1);
//   };

//   // Hàm xóa file PDF
//   const handleDelete = async (filename) => {
//     if (!window.confirm(`Bạn có chắc chắn muốn xóa file ${filename}?`)) return;
//     try {
//       // Tạo file giả (empty Blob) với tên filename, vì backend yêu cầu UploadFile
//       const blob = new Blob([], { type: 'application/pdf' });
//       const fakeFile = new File([blob], filename, { type: 'application/pdf' });
//       const formData = new FormData();
//       formData.append('file', fakeFile);
//       const response = await fetch('http://ec2-54-86-234-1.compute-1.amazonaws.com:912/delete_files', {
//         method: 'POST',
//         headers: { 'Authorization': `Bearer ${token}` },
//         body: formData,
//       });
//       if (!response.ok) {
//         throw new Error(`Error ${response.status}: ${response.statusText}`);
//       }
//       // Cập nhật lại danh sách file sau khi xóa thành công
//       setPdfList(prevList => prevList.filter(file => file !== filename));
//       // Nếu file đã chọn bị xóa, chọn file mới nếu còn
//       if (selectedFile === filename) {
//         setSelectedFile(prevList => {
//           const updatedList = pdfList.filter(file => file !== filename);
//           return updatedList.length > 0 ? updatedList[0] : null;
//         });
//       }
//     } catch (err) {
//       console.error("Delete error:", err);
//       setError(err.message);
//     }
//   };

//   return (
//     <div style={styles.container}>
//       {error && <div style={styles.error}>Error: {error}</div>}
//       {pdfList.length === 0 ? (
//         <p>No PDF file available.</p>
//       ) : (
//         <>
//           {/* Danh sách file PDF với nút xóa */}
//           <ul style={styles.list}>
//             {pdfList.map((file, index) => (
//               <li key={index} style={styles.listItem}>
//                 <span style={styles.fileName} onClick={() => setSelectedFile(file)}>
//                   {file}
//                 </span>
//                 <button onClick={() => handleDelete(file)} style={styles.deleteButton}>
//                   &#10005;
//                 </button>
//               </li>
//             ))}
//           </ul>
//           {/* Thanh điều hướng trang và hiển thị nội dung file PDF đã chọn */}
//           {selectedFile && (
//             <>
//               <div style={styles.pagination}>
//                 <button onClick={handlePrevious} disabled={currentPage === 0}>
//                   Previous
//                 </button>
//                 <span>Page {currentPage + 1}</span>
//                 <button onClick={handleNext}>Next</button>
//               </div>
//               <div style={styles.imageContainer}>
//                 {image ? (
//                   <img
//                     src={`data:image/jpeg;base64,${image}`}
//                     alt={`Page ${currentPage + 1}`}
//                     style={styles.image}
//                   />
//                 ) : (
//                   <p>No page available to display.</p>
//                 )}
//               </div>
//             </>
//           )}
//         </>
//       )}
//     </div>
//   );
// };

// const styles = {
//   container: {
//     padding: '20px',
//     fontFamily: 'Arial, sans-serif',
//   },
//   error: {
//     color: 'red',
//     marginBottom: '10px',
//   },
//   list: {
//     listStyle: 'none',
//     padding: 0,
//     marginBottom: '20px',
//   },
//   listItem: {
//     display: 'flex',
//     alignItems: 'center',
//     justifyContent: 'space-between',
//     backgroundColor: '#f5f5f5',
//     marginBottom: '10px',
//     padding: '10px',
//     borderRadius: '4px',
//   },
//   fileName: {
//     cursor: 'pointer',
//   },
//   deleteButton: {
//     backgroundColor: 'red',
//     color: '#fff',
//     border: 'none',
//     borderRadius: '50%',
//     width: '30px',
//     height: '30px',
//     cursor: 'pointer',
//     fontSize: '16px',
//     lineHeight: '30px',
//     textAlign: 'center',
//   },
//   pagination: {
//     display: 'flex',
//     alignItems: 'center',
//     gap: '10px',
//     marginBottom: '15px',
//   },
//   imageContainer: {
//     display: 'flex',
//     flexDirection: 'column',
//     gap: '15px',
//   },
//   image: {
//     maxWidth: '100%',
//     borderRadius: '4px',
//   },
// };

// export default PDFViewer;
