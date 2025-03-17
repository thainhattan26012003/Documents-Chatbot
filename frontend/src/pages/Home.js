import React from 'react';
import Chatbot from '../components/Chatbot';
import PDFUploader from '../components/PDFUploader';
import PDFViewer from '../components/PDFViewer';

const Home = () => {
  const role = localStorage.getItem('role');
  return (
    <div style={styles.container}>
      <header style={styles.header}>
        <h1 style={styles.title}>Chatbot Document Assistant</h1>
      </header>
      <div style={styles.content}>
        <div style={styles.leftPanel}>
          <div style={styles.section}>
            <h2 style={styles.sectionTitle}>PDF Viewer</h2>
            <PDFViewer />
          </div>
        </div>
        <div style={styles.rightPanel}>
          {role === 'manager' && (
            <div style={styles.pdfSection}>
              <h2 style={styles.sectionTitle}>Upload PDF</h2>
              <PDFUploader />
            </div>
          )}
          <div style={styles.chatSection}>
            <h2 style={styles.sectionTitle}>Chatbot Hỏi Đáp</h2>
            <Chatbot />
          </div>
        </div>
      </div>
    </div>
  );
};

const styles = {
  container: {
    height: '100vh',
    display: 'flex',
    flexDirection: 'column',
    fontFamily: 'Arial, sans-serif',
  },
  header: {
    background: '#9b59b6',
    padding: '20px',
    textAlign: 'center',
    color: '#fff',
  },
  title: {
    margin: 0,
    fontSize: '28px',
  },
  content: {
    flex: 1,
    display: 'flex',
    overflow: 'hidden',
  },
  leftPanel: {
    flex: 1,
    padding: '20px',
    borderRight: '1px solid #ccc',
    overflowY: 'auto',
  },
  rightPanel: {
    flex: 1,
    padding: '20px',
    display: 'flex',
    flexDirection: 'column',
    overflow: 'hidden',
  },
  section: {
    marginBottom: '30px',
  },
  sectionTitle: {
    fontSize: '20px',
    marginBottom: '15px',
    color: '#333',
  },
  pdfSection: {
    marginBottom: '30px',
  },
  chatSection: {
    flex: 1,
    overflowY: 'auto',
  },
};

export default Home;
