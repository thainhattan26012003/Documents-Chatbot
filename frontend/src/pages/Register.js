import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const Register = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [role, setRole] = useState('base');
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch('http://ec2-54-86-234-1.compute-1.amazonaws.com:912/api/users/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password, role }),
      });
      if (response.ok) {
        alert('Đăng ký thành công');
        navigate('/login');
      } else {
        alert('Đăng ký thất bại');
      }
    } catch (error) {
      alert('Có lỗi xảy ra. Vui lòng thử lại.');
    }
  };

  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <h2 style={styles.header}>Đăng ký Chatbot</h2>
        <form onSubmit={handleSubmit} style={styles.form}>
          <input
            type="text"
            placeholder="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            style={styles.input}
            required
          />
          <input
            type="password"
            placeholder="Mật khẩu"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            style={styles.input}
            required
          />
          <select
            value={role}
            onChange={(e) => setRole(e.target.value)}
            style={styles.input}
          >
            <option value="base">User Base (Chỉ xem & hỏi đáp)</option>
            <option value="manager">User Manager (Có quyền upload PDF)</option>
          </select>
          <button type="submit" style={styles.button}>
            Đăng ký
          </button>
        </form>
        <p style={styles.text}>
          Đã có tài khoản?{' '}
          <span style={styles.link} onClick={() => navigate('/login')}>
            Đăng nhập ngay
          </span>
        </p>
      </div>
    </div>
  );
};

const styles = {
  container: {
    display: 'flex',
    height: '100vh',
    alignItems: 'center',
    justifyContent: 'center',
    background: 'linear-gradient(135deg, #71b7e6, #9b59b6)',
  },
  card: {
    background: '#ffffff',
    padding: '40px',
    borderRadius: '8px',
    boxShadow: '0 4px 20px rgba(0,0,0,0.1)',
    width: '350px',
    textAlign: 'center',
  },
  header: {
    marginBottom: '20px',
    color: '#333',
  },
  form: {
    display: 'flex',
    flexDirection: 'column',
  },
  input: {
    padding: '12px 16px',
    marginBottom: '15px',
    border: '1px solid #ccc',
    borderRadius: '4px',
    fontSize: '16px',
  },
  button: {
    padding: '12px 16px',
    backgroundColor: '#9b59b6',
    color: '#fff',
    border: 'none',
    borderRadius: '4px',
    fontSize: '16px',
    cursor: 'pointer',
    transition: 'background-color 0.3s',
  },
  text: {
    marginTop: '20px',
    fontSize: '14px',
    color: '#666',
  },
  link: {
    color: '#9b59b6',
    fontWeight: 'bold',
    cursor: 'pointer',
  },
};

export default Register;
