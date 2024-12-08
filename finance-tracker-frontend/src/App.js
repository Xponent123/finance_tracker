import React, { useState } from 'react';
import Login from './components/Auth/Login';
import Register from './components/Auth/Register';
import Expenses from './components/Dashboard/Expenses';
import './App.css';
// import './ImageStyles.css'; // Import the new CSS file

function App() {
  const [token, setToken] = useState(localStorage.getItem('token'));

  return (
    <div className="app-container">
      {!token ? (
        <div style={{ display: 'flex', alignItems: 'center', gap: '0px' }}>
          <div>
            <Login setToken={setToken} />
            <Register />
          </div>
          <img
            src="/f1.jpg"
            alt="Description"
            className="styled-image" // Apply the CSS class
          />
        </div>
      ) : (
        <Expenses token={token} setToken={setToken} />
      )}
    </div>
  );
}

export default App;
