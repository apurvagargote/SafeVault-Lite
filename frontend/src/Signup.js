import React, { useState } from 'react';
import axios from 'axios';
import './Login.css';

const API_BASE = 'http://localhost:8000';

function Signup({ onSignup, onSwitchToLogin }) {
  const [signupForm, setSignupForm] = useState({ 
    username: '', 
    email: '', 
    password: '', 
    confirmPassword: '',
    role: 'user' 
  });
  const [notification, setNotification] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const showNotification = (message) => {
    setNotification(message);
    setTimeout(() => setNotification(''), 3000);
  };

  const handleSignup = async (e) => {
    e.preventDefault();
    
    if (signupForm.password !== signupForm.confirmPassword) {
      showNotification('❌ Passwords do not match');
      return;
    }

    setIsLoading(true);
    
    try {
      await axios.post(`${API_BASE}/signup`, {
        username: signupForm.username,
        email: signupForm.email,
        password: signupForm.password,
        role: signupForm.role
      });
      
      showNotification('✅ Account created! Please login.');
      setTimeout(() => onSwitchToLogin(), 2000);
      
    } catch (error) {
      setIsLoading(false);
      const message = error.response?.data?.detail || 'Signup failed';
      showNotification(`❌ ${message}`);
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
            <div className="lock">
              <div className="lock-body">
                <div className="lock-hole"></div>
              </div>
              <div className="lock-shackle"></div>
            </div>
          </div>
          
          <h1>🔐 Join SafeVault</h1>
          <p className="tagline">Create your secure account</p>
          
          <form onSubmit={handleSignup}>
            <div className="input-group">
              <input
                type="text"
                placeholder="Username"
                value={signupForm.username}
                onChange={(e) => setSignupForm({...signupForm, username: e.target.value})}
                required
                disabled={isLoading}
              />
              <span className="input-icon">👤</span>
            </div>
            
            <div className="input-group">
              <input
                type="email"
                placeholder="Email"
                value={signupForm.email}
                onChange={(e) => setSignupForm({...signupForm, email: e.target.value})}
                required
                disabled={isLoading}
              />
              <span className="input-icon">📧</span>
            </div>
            
            <div className="input-group">
              <input
                type="password"
                placeholder="Password"
                value={signupForm.password}
                onChange={(e) => setSignupForm({...signupForm, password: e.target.value})}
                required
                disabled={isLoading}
              />
              <span className="input-icon">🔑</span>
            </div>
            
            <div className="input-group">
              <input
                type="password"
                placeholder="Confirm Password"
                value={signupForm.confirmPassword}
                onChange={(e) => setSignupForm({...signupForm, confirmPassword: e.target.value})}
                required
                disabled={isLoading}
              />
              <span className="input-icon">🔒</span>
            </div>
            
            <div className="input-group">
              <select
                value={signupForm.role}
                onChange={(e) => setSignupForm({...signupForm, role: e.target.value})}
                disabled={isLoading}
              >
                <option value="user">User</option>
                <option value="admin">Admin</option>
              </select>
              <span className="input-icon">👥</span>
            </div>
            
            <button type="submit" disabled={isLoading} className={isLoading ? 'loading' : ''}>
              {isLoading ? (
                <>
                  <span className="spinner"></span>
                  Creating Account...
                </>
              ) : (
                'Create Account'
              )}
            </button>
          </form>
          
          <div className="demo-creds">
            <small>Already have an account? 
              <button 
                type="button" 
                onClick={onSwitchToLogin}
                style={{background: 'none', border: 'none', color: '#667eea', textDecoration: 'underline', cursor: 'pointer', marginLeft: '5px'}}
              >
                Login here
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

export default Signup;