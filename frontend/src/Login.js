import React, { useState } from 'react';
import axios from 'axios';
import './Login.css';

const API_BASE = 'http://localhost:8000';

function Login({ onLogin, onSwitchToSignup }) {
  const [loginForm, setLoginForm] = useState({ username: '', password: '' });
  const [notification, setNotification] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showUnlock, setShowUnlock] = useState(false);

  const showNotification = (message) => {
    setNotification(message);
    setTimeout(() => setNotification(''), 3000);
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    
    try {
      const response = await axios.post(`${API_BASE}/login`, loginForm);
      const { access_token, user } = response.data;
      
      // Show unlock animation
      setShowUnlock(true);
      
      setTimeout(() => {
        localStorage.setItem('safevault_token', access_token);
        localStorage.setItem('safevault_user', JSON.stringify(user));
        onLogin(access_token, user);
      }, 2000);
      
    } catch (error) {
      setIsLoading(false);
      showNotification('❌ Invalid credentials');
    }
  };

  return (
    <div className="app">
      <div className="login-container">
        <div className="particles"></div>
        <div className="particles"></div>
        <div className="particles"></div>
        
        <div className={`login-form ${isLoading ? 'loading' : ''}`}>
          <div className="lock-container">
            <div className={`lock ${showUnlock ? 'unlock' : ''}`}>
              <div className="lock-body">
                <div className="lock-hole"></div>
              </div>
              <div className="lock-shackle"></div>
            </div>
          </div>
          
          <h1>🔐 SafeVault</h1>
          <p className="tagline">Your secrets, secured forever</p>
          
          {showUnlock ? (
            <div className="unlock-animation">
              <div className="success-icon">✓</div>
              <p>Vault Unlocked!</p>
              <div className="loading-dots">
                <span></span><span></span><span></span>
              </div>
            </div>
          ) : (
            <form onSubmit={handleLogin}>
              <div className="input-group">
                <input
                  type="text"
                  placeholder="Username"
                  value={loginForm.username}
                  onChange={(e) => setLoginForm({...loginForm, username: e.target.value})}
                  required
                  disabled={isLoading}
                />
                <span className="input-icon">👤</span>
              </div>
              
              <div className="input-group">
                <input
                  type="password"
                  placeholder="Password"
                  value={loginForm.password}
                  onChange={(e) => setLoginForm({...loginForm, password: e.target.value})}
                  required
                  disabled={isLoading}
                />
                <span className="input-icon">🔑</span>
              </div>
              
              <button type="submit" disabled={isLoading} className={isLoading ? 'loading' : ''}>
                {isLoading ? (
                  <>
                    <span className="spinner"></span>
                    Authenticating...
                  </>
                ) : (
                  'Unlock Vault'
                )}
              </button>
            </form>
          )}
          
          <div className="demo-creds">
            <small>Don't have an account? 
              <button 
                type="button" 
                onClick={onSwitchToSignup}
                style={{background: 'none', border: 'none', color: '#667eea', textDecoration: 'underline', cursor: 'pointer', marginLeft: '5px'}}
              >
                Sign up here
              </button>
            </small>
          </div>
        </div>
      </div>
      
      {notification && (
        <div className="notification error">{notification}</div>
      )}
    </div>
  );
}

export default Login;