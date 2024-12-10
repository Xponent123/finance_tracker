import React, { useState } from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom'; // Import Routes instead of Switch
import Login from './components/Auth/Login';
import Register from './components/Auth/Register';
import Expenses from './components/Dashboard/Expenses';
import Summary from './components/Dashboard/Summary'; // Import the Summary component
import './App.css';
// import './ImageStyles.css'; // Import the new CSS file

function App() {
  const [token, setToken] = useState(localStorage.getItem('token'));

  return (
    <Router>
      <div className="app-container">
        <Routes> {/* Use Routes instead of Switch */}
          <Route path="/summary" element={<Summary token={token} setToken={setToken} />} /> {/* Update Route */}
          <Route path="/" element={
            !token ? (
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
            )
          } />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
