import React, { useState } from 'react';

const Chatbot = () => {
  const [question, setQuestion] = useState('');
  const [chatLog, setChatLog] = useState([]);
  const token = localStorage.getItem('token');

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch('http://localhost:912/api/chat/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ question }),
      });
      const data = await response.json();
      setChatLog([{ question, answer: data.answer }, ...chatLog]);
      setQuestion('');
    } catch (error) {
      alert('Có lỗi xảy ra khi gửi câu hỏi');
    }
  };

  return (
    <div style={styles.container}>
      <form onSubmit={handleSubmit} style={styles.form}>
        <input
          type="text"
          placeholder="Nhập câu hỏi..."
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          style={styles.input}
          required
        />
        <button type="submit" style={styles.button}>Gửi</button>
      </form>
      <div style={styles.chatLog}>
        {chatLog.map((chat, index) => (
          <div key={index} style={styles.chatEntry}>
            <p style={styles.userText}><strong>Bạn:</strong> {chat.question}</p>
            <p style={styles.botText}><strong>Chatbot:</strong> {chat.answer}</p>
            <hr style={styles.separator} />
          </div>
        ))}
      </div>
    </div>
  );
};

const styles = {
  container: {
    height: '100%',
    display: 'flex',
    flexDirection: 'column',
  },
  form: {
    display: 'flex',
    marginBottom: '10px',
  },
  input: {
    flex: 1,
    padding: '10px',
    fontSize: '16px',
    border: '1px solid #ccc',
    borderRadius: '4px 0 0 4px',
  },
  button: {
    padding: '10px 20px',
    fontSize: '16px',
    backgroundColor: '#9b59b6',
    color: '#fff',
    border: 'none',
    borderRadius: '0 4px 4px 0',
    cursor: 'pointer',
  },
  chatLog: {
    flex: 1,
    overflowY: 'auto',
    padding: '10px',
    border: '1px solid #ccc',
    borderRadius: '4px',
    marginTop: '10px',
  },
  chatEntry: {
    marginBottom: '10px',
  },
  userText: {
    color: '#333',
    margin: '5px 0',
  },
  botText: {
    color: '#9b59b6',
    margin: '5px 0',
  },
  separator: {
    border: 'none',
    borderTop: '1px solid #eee',
    margin: '10px 0',
  },
};

export default Chatbot;
