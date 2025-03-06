// import React, { useState } from 'react';
// import { useNavigate } from 'react-router-dom';

// const Login = () => {
//   const [username, setUsername] = useState('');
//   const [password, setPassword] = useState('');
//   const navigate = useNavigate();

//   const handleSubmit = async (e) => {
//     e.preventDefault();
//     try {
//       const response = await fetch('http://ec2-54-86-234-1.compute-1.amazonaws.com:912/login', {
//         method: 'POST',
//         headers: { 'Content-Type': 'application/json' },
//         body: JSON.stringify({ username, password }),
//       });
//       if (response.ok) {
//         const data = await response.json();
//         localStorage.setItem('token', data.access_token);
//         localStorage.setItem('role', data.role);
//         navigate('/home');
//       } else {
//         alert('Đăng nhập thất bại');
//       }
//     } catch (error) {
//       alert('Có lỗi xảy ra. Vui lòng thử lại.');
//     }
//   };

//   return (
//     <div style={styles.container}>
//       <div style={styles.card}>
//         <h2 style={styles.header}>Đăng nhập Chatbot</h2>
//         <form onSubmit={handleSubmit} style={styles.form}>
//           <input
//             type="text"
//             placeholder="Username"
//             value={username}
//             onChange={(e) => setUsername(e.target.value)}
//             style={styles.input}
//             required
//           />
//           <input
//             type="password"
//             placeholder="Mật khẩu"
//             value={password}
//             onChange={(e) => setPassword(e.target.value)}
//             style={styles.input}
//             required
//           />
//           <button type="submit" style={styles.button}>
//             Đăng nhập
//           </button>
//         </form>
//         <p style={styles.text}>
//           Chưa có tài khoản?{' '}
//           <span style={styles.link} onClick={() => navigate('/register')}>
//             Đăng ký ngay
//           </span>
//         </p>
//       </div>
//     </div>
//   );
// };

// const styles = {
//   container: {
//     display: 'flex',
//     height: '100vh',
//     alignItems: 'center',
//     justifyContent: 'center',
//     background: 'linear-gradient(135deg, #71b7e6, #9b59b6)',
//   },
//   card: {
//     background: '#ffffff',
//     padding: '40px',
//     borderRadius: '8px',
//     boxShadow: '0 4px 20px rgba(0,0,0,0.1)',
//     width: '350px',
//     textAlign: 'center',
//   },
//   header: {
//     marginBottom: '20px',
//     color: '#333',
//   },
//   form: {
//     display: 'flex',
//     flexDirection: 'column',
//   },
//   input: {
//     padding: '12px 16px',
//     marginBottom: '15px',
//     border: '1px solid #ccc',
//     borderRadius: '4px',
//     fontSize: '16px',
//   },
//   button: {
//     padding: '12px 16px',
//     backgroundColor: '#9b59b6',
//     color: '#fff',
//     border: 'none',
//     borderRadius: '4px',
//     fontSize: '16px',
//     cursor: 'pointer',
//     transition: 'background-color 0.3s',
//   },
//   text: {
//     marginTop: '20px',
//     fontSize: '14px',
//     color: '#666',
//   },
//   link: {
//     color: '#9b59b6',
//     fontWeight: 'bold',
//     cursor: 'pointer',
//   },
// };

// export default Login;


import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const Login = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch('http://ec2-54-86-234-1.compute-1.amazonaws.com:912/api/users/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
      });
      if (!response.ok) {
        alert('Đăng nhập thất bại');
        return;
      }
      const data = await response.json();
      // Lưu token và role từ response vào localStorage
      localStorage.setItem('token', data.access_token);
      localStorage.setItem('role', data.role);
      navigate('/home');
    } catch (error) {
      alert('Có lỗi xảy ra. Vui lòng thử lại.');
      console.error(error);
    }
  };

  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <h2 style={styles.header}>Đăng nhập Chatbot</h2>
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
          <button type="submit" style={styles.button}>Đăng nhập</button>
        </form>
        <p style={styles.text}>
          Chưa có tài khoản?{' '}
          <span style={styles.link} onClick={() => navigate('/register')}>
            Đăng ký ngay
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

export default Login;
