import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Login from './Login';
import Signup from './Signup';
import './App.css';
import './Dashboard.css';
import './Analytics.css';
import './Categories.css';
import './Responsive.css';

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function App() {
  const [secrets, setSecrets] = useState([]);
  const [newSecret, setNewSecret] = useState({ name: '', value: '', description: '', category: 'general' });
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [sidebarOpen, setSidebarOpen] = useState(false);
  
  const categories = [
    { id: 'all', name: 'All Secrets', icon: '📁', color: '#ff6b6b' },
    { id: 'general', name: 'General', icon: '📄', color: '#6b7280' },
    { id: 'api-key', name: 'API Keys', icon: '🔑', color: '#f59e0b' },
    { id: 'password', name: 'Passwords', icon: '🔒', color: '#ef4444' },
    { id: 'database', name: 'Database', icon: '🗄️', color: '#10b981' },
    { id: 'certificate', name: 'Certificates', icon: '📜', color: '#ff9500' },
    { id: 'token', name: 'Tokens', icon: '🎫', color: '#f97316' }
  ];
  const [selectedSecret, setSelectedSecret] = useState(null);
  const [showForm, setShowForm] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [notification, setNotification] = useState('');
  const [showValue, setShowValue] = useState({});
  const [refreshKey, setRefreshKey] = useState(0);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [token, setToken] = useState('');
  const [user, setUser] = useState(null);
  const [showSignup, setShowSignup] = useState(false);
  const [activeTab, setActiveTab] = useState('secrets');
  const [showPasswordModal, setShowPasswordModal] = useState(false);
  const [passwordForm, setPasswordForm] = useState({ currentPassword: '', newPassword: '', confirmPassword: '' });
  const [passwordError, setPasswordError] = useState('');

  const headers = token ? { Authorization: `Bearer ${token}` } : {};

  useEffect(() => {
    const savedToken = localStorage.getItem('safevault_token');
    const savedUser = localStorage.getItem('safevault_user');
    if (savedToken && savedUser) {
      setToken(savedToken);
      setUser(JSON.parse(savedUser));
      setIsLoggedIn(true);
    }
  }, []);

  useEffect(() => {
    if (isLoggedIn) {
      fetchSecrets();
    }
  }, [isLoggedIn]);

  const showNotification = (message) => {
    setNotification(message);
    setTimeout(() => setNotification(''), 3000);
  };

  const fetchSecrets = async () => {
    try {
      const response = await axios.get(`${API_BASE}/secrets?t=${Date.now()}`, { headers });
      setSecrets(response.data);
      setRefreshKey(prev => prev + 1);
    } catch (error) {
      showNotification('❌ Failed to fetch secrets');
    }
  };

  const createSecret = async (e) => {
    e.preventDefault();
    if (!newSecret.name.trim() || !newSecret.value.trim()) {
      showNotification('⚠️ Name and value are required');
      return;
    }
    try {
      const response = await axios.post(`${API_BASE}/secrets`, newSecret, { headers });
      
      // Add small delay to ensure AWS sync completes
      setTimeout(async () => {
        await fetchSecrets();
      }, 1000);
      
      setNewSecret({ name: '', value: '', description: '', category: 'general' });
      setShowForm(false);
      showNotification('✅ Secret created successfully');
    } catch (error) {
      showNotification('❌ Failed to create secret');
      console.error(error);
    }
  };

  const viewSecret = async (name) => {
    try {
      const response = await axios.get(`${API_BASE}/secrets/${name}`, { headers });
      setSelectedSecret(response.data);
    } catch (error) {
      showNotification('❌ Failed to view secret');
    }
  };

  const deleteSecret = async (name) => {
    if (!window.confirm(`Delete secret "${name}"? This cannot be undone.`)) return;
    try {
      await axios.delete(`${API_BASE}/secrets/${name}`, { headers });
      
      // Add small delay to ensure AWS sync completes
      setTimeout(async () => {
        await fetchSecrets();
      }, 1000);
      
      setSelectedSecret(null);
      showNotification('🗑️ Secret deleted successfully');
    } catch (error) {
      showNotification('❌ Failed to delete secret');
      console.error(error);
    }
  };

  const toggleValueVisibility = (name) => {
    setShowValue(prev => ({ ...prev, [name]: !prev[name] }));
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    showNotification('📋 Copied to clipboard');
  };

  const handleLogin = (newToken, userData) => {
    setToken(newToken);
    setUser(userData);
    setIsLoggedIn(true);
  };

  const logout = () => {
    setToken('');
    setUser(null);
    setIsLoggedIn(false);
    setSecrets([]);
    setSelectedCategory('all');
    setNewSecret({ name: '', value: '', description: '', category: 'general' });
    
    localStorage.removeItem('safevault_token');
    localStorage.removeItem('safevault_user');
    
    showNotification('👋 Logged out successfully');
  };

  const updatePassword = async (e) => {
    e.preventDefault();
    setPasswordError('');
    
    // Validate password match
    if (passwordForm.newPassword !== passwordForm.confirmPassword) {
      setPasswordError('New passwords do not match');
      return;
    }
    
    // Validate password length
    if (passwordForm.newPassword.length < 6) {
      setPasswordError('New password must be at least 6 characters');
      return;
    }
    
    try {
      await axios.put(`${API_BASE}/change-password`, {
        current_password: passwordForm.currentPassword,
        new_password: passwordForm.newPassword
      }, { headers });
      
      setPasswordForm({ currentPassword: '', newPassword: '', confirmPassword: '' });
      setPasswordError('');
      setShowPasswordModal(false);
      showNotification('✅ Password updated successfully! Please login again.');
      
      // Auto logout after password change for security
      setTimeout(() => {
        logout();
      }, 2000);
      
    } catch (error) {
      const errorMsg = error.response?.data?.detail || 'Failed to update password';
      setPasswordError(errorMsg);
    }
  };

  const filteredSecrets = secrets.filter(secret => {
    const matchesSearch = secret.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         secret.description.toLowerCase().includes(searchTerm.toLowerCase());
    const secretCategory = secret.category || 'general'; // Default to general if no category
    // Handle both 'api-key' and 'api_key' formats
    const normalizedSecretCategory = secretCategory.replace('_', '-');
    const matchesCategory = selectedCategory === 'all' || normalizedSecretCategory === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  if (!isLoggedIn) {
    return showSignup ? (
      <Signup 
        onSignup={handleLogin} 
        onSwitchToLogin={() => setShowSignup(false)} 
      />
    ) : (
      <Login 
        onLogin={handleLogin} 
        onSwitchToSignup={() => setShowSignup(true)} 
      />
    );
  }

  return (
    <div className="dashboard">
      <button 
        className="mobile-menu-toggle"
        onClick={() => setSidebarOpen(!sidebarOpen)}
      >
        ☰
      </button>
      
      <div 
        className={`mobile-overlay ${sidebarOpen ? 'show' : ''}`}
        onClick={() => setSidebarOpen(false)}
      ></div>
      
      <aside className={`sidebar ${sidebarOpen ? 'open' : ''}`}>
        <div className="sidebar-header">
          <h2>🔐 SafeVault</h2>
        </div>
        
        <div className="user-profile">
          <div className="avatar">
            {user?.username?.charAt(0).toUpperCase()}
          </div>
          <div className="user-info">
            <h3>{user?.username}</h3>
            <span className="role-badge">{user?.role}</span>
          </div>
        </div>
        
        <nav className="sidebar-nav">
          <button 
            className={`nav-item ${activeTab === 'secrets' ? 'active' : ''}`}
            onClick={() => {
              setActiveTab('secrets');
              setSidebarOpen(false);
            }}
          >
            🔑 My Secrets
          </button>
          <button 
            className={`nav-item ${activeTab === 'analytics' ? 'active' : ''}`}
            onClick={() => {
              setActiveTab('analytics');
              setSidebarOpen(false);
            }}
          >
            📈 Analytics
          </button>
          <button 
            className={`nav-item ${activeTab === 'settings' ? 'active' : ''}`}
            onClick={() => {
              setActiveTab('settings');
              setSidebarOpen(false);
            }}
          >
            ⚙️ Settings
          </button>
        </nav>
        
        <div className="sidebar-footer">
          <button className="logout-button" onClick={logout}>
            <span className="logout-icon">🚪</span>
            <span>Logout</span>
          </button>
        </div>
      </aside>
      
      <main className="main-content">
        <header className="content-header">
          <div className="header-left">
            <h1>
              {activeTab === 'secrets' && 'My Secrets'}
              {activeTab === 'analytics' && 'Analytics Dashboard'}
              {activeTab === 'settings' && 'Account Settings'}
            </h1>
            <p>
              {activeTab === 'secrets' && 'Manage your secure credentials'}
              {activeTab === 'analytics' && 'Monitor your vault activity'}
              {activeTab === 'settings' && 'Configure your account preferences'}
            </p>
          </div>
          {activeTab === 'secrets' && (
            <button 
              className="add-secret-btn"
              onClick={() => {
                if (!showForm) {
                  // Set category to current filter when opening form
                  const defaultCategory = selectedCategory === 'all' ? 'general' : selectedCategory;
                  setNewSecret({ name: '', value: '', description: '', category: defaultCategory });
                }
                setShowForm(!showForm);
              }}
            >
              {showForm ? '✕ Cancel' : '+ Add Secret'}
            </button>
          )}
        </header>

        {notification && (
          <div className="notification">{notification}</div>
        )}

        <div className="content-body">
        {activeTab === 'secrets' && (
          <>
            <div className="filters-section">
              <div className="search-bar">
                <input
                  type="text"
                  placeholder="🔍 Search secrets..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>
              
              <div className="category-filters">
                {categories.map(category => (
                  <button
                    key={category.id}
                    className={`category-btn ${selectedCategory === category.id ? 'active' : ''}`}
                    onClick={() => setSelectedCategory(category.id)}
                    style={{
                      backgroundColor: selectedCategory === category.id ? category.color : 'transparent',
                      borderColor: category.color,
                      color: selectedCategory === category.id ? 'white' : category.color
                    }}
                  >
                    <span className="category-icon">{category.icon}</span>
                    <span>{category.name}</span>
                    <span className="category-count">
                      {category.id === 'all' 
                        ? secrets.length 
                        : secrets.filter(s => {
                            const secretCat = s.category || 'general';
                            return secretCat.replace('_', '-') === category.id;
                          }).length
                      }
                    </span>
                  </button>
                ))}
              </div>
            </div>

        {showForm && (
          <div className="form-modal">
            <div className="form-content">
              <h2>Add New Secret</h2>
              <form onSubmit={createSecret}>
                <input
                  type="text"
                  placeholder="Secret name (e.g., api-key)"
                  value={newSecret.name}
                  onChange={(e) => setNewSecret({...newSecret, name: e.target.value})}
                  required
                />
                <textarea
                  placeholder="Secret value"
                  value={newSecret.value}
                  onChange={(e) => setNewSecret({...newSecret, value: e.target.value})}
                  required
                  rows="3"
                />
                <input
                  type="text"
                  placeholder="Description (optional)"
                  value={newSecret.description}
                  onChange={(e) => setNewSecret({...newSecret, description: e.target.value})}
                />
                <select
                  value={newSecret.category}
                  onChange={(e) => setNewSecret({...newSecret, category: e.target.value})}
                >
                  {categories.filter(c => c.id !== 'all').map(category => (
                    <option key={category.id} value={category.id}>
                      {category.icon} {category.name}
                    </option>
                  ))}
                </select>
                <div className="form-actions">
                  <button type="button" onClick={() => setShowForm(false)}>Cancel</button>
                  <button type="submit">Create Secret</button>
                </div>
              </form>
            </div>
          </div>
        )}

        <div className="secrets-grid">
          {filteredSecrets.length === 0 ? (
            <div className="empty-state">
              <h3>No secrets found</h3>
              <p>{searchTerm ? 'Try a different search term' : 'Add your first secret to get started'}</p>
            </div>
          ) : (
            filteredSecrets.map(secret => (
              <div key={secret.name} className="secret-card">
                <div className="secret-header">
                  <div className="secret-title">
                    <span className="secret-category-icon">
                      {categories.find(c => c.id === (secret.category || 'general').replace('_', '-'))?.icon || '📄'}
                    </span>
                    <h3>{secret.name}</h3>
                  </div>
                  <div className="secret-actions">
                    <button 
                      className="view-btn"
                      onClick={() => viewSecret(secret.name)}
                      title="View secret"
                    >
                      👁️
                    </button>
                    <button 
                      className="delete-btn"
                      onClick={() => deleteSecret(secret.name)}
                      title="Delete secret"
                    >
                      🗑️
                    </button>
                  </div>
                </div>
                <p className="secret-description">{secret.description || 'No description'}</p>
                <div className="secret-meta">
                  <span className="secret-category-badge" style={{backgroundColor: categories.find(c => c.id === (secret.category || 'general').replace('_', '-'))?.color || '#6b7280'}}>
                    {categories.find(c => c.id === (secret.category || 'general').replace('_', '-'))?.name || 'General'}
                  </span>
                  <small className="secret-date">Created: {new Date(secret.created_date + 'Z').toLocaleDateString('en-IN', {timeZone: 'Asia/Kolkata'})} at {new Date(secret.created_date + 'Z').toLocaleTimeString('en-IN', {timeZone: 'Asia/Kolkata', hour12: true})}</small>
                </div>
              </div>
            ))
          )}
        </div>

        {selectedSecret && (
          <div className="modal">
            <div className="modal-content">
              <div className="modal-header">
                <h2>🔑 {selectedSecret.name}</h2>
                <button 
                  className="close-btn"
                  onClick={() => setSelectedSecret(null)}
                >
                  ✕
                </button>
              </div>
              <div className="secret-value">
                <label>Secret Value:</label>
                <div className="value-container">
                  <input
                    type={showValue[selectedSecret.name] ? 'text' : 'password'}
                    value={selectedSecret.value}
                    readOnly
                  />
                  <button 
                    type="button"
                    onClick={() => toggleValueVisibility(selectedSecret.name)}
                    title={showValue[selectedSecret.name] ? 'Hide' : 'Show'}
                  >
                    {showValue[selectedSecret.name] ? '🙈' : '👁️'}
                  </button>
                  <button 
                    type="button"
                    onClick={() => copyToClipboard(selectedSecret.value)}
                    title="Copy to clipboard"
                  >
                    📋
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
          </>
        )}
        
        {activeTab === 'analytics' && (
          <div className="analytics-dashboard">
            <div className="stats-grid">
              <div className="stat-card">
                <h3>🔑 Total Secrets</h3>
                <div className="stat-number">{secrets.length}</div>
                <p>Active secrets in your vault</p>
              </div>
              <div className="stat-card">
                <h3>📈 This Month</h3>
                <div className="stat-number">{secrets.filter(s => new Date(s.created_date).getMonth() === new Date().getMonth()).length}</div>
                <p>Secrets created this month</p>
              </div>
              <div className="stat-card">
                <h3>⚙️ Most Used</h3>
                <div className="stat-text">{secrets[0]?.name || 'None'}</div>
                <p>Most accessed secret</p>
              </div>
              <div className="stat-card">
                <h3>🔒 Security Score</h3>
                <div className="stat-number">95%</div>
                <p>Overall security rating</p>
              </div>
            </div>
            
            <div className="activity-section">
              <h3>Recent Activity</h3>
              <div className="activity-list">
                {secrets.slice(0, 5).map(secret => (
                  <div key={secret.name} className="activity-item">
                    <span className="activity-icon">🔑</span>
                    <div className="activity-details">
                      <p><strong>{secret.name}</strong> was created</p>
                      <small>{new Date(secret.created_date + 'Z').toLocaleDateString('en-IN', {timeZone: 'Asia/Kolkata'})} at {new Date(secret.created_date + 'Z').toLocaleTimeString('en-IN', {timeZone: 'Asia/Kolkata', hour12: true})}</small>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
        
        {activeTab === 'settings' && (
          <div className="settings-panel">
            <div className="settings-section">
              <h3>👤 Profile Settings</h3>
              <div className="setting-item">
                <label>Username</label>
                <input type="text" value={user?.username} readOnly />
              </div>
              <div className="setting-item">
                <label>Email</label>
                <input type="email" value={user?.email} readOnly />
              </div>
              <div className="setting-item">
                <label>Role</label>
                <input type="text" value={user?.role} readOnly />
              </div>
            </div>
            
            <div className="settings-section">
              <h3>🔒 Security Settings</h3>
              <div className="setting-item">
                <label>Two-Factor Authentication</label>
                <button className="toggle-btn">Enable 2FA</button>
              </div>
              <div className="setting-item">
                <label>Session Timeout</label>
                <select>
                  <option>30 minutes</option>
                  <option>1 hour</option>
                  <option>4 hours</option>
                </select>
              </div>
              <div className="setting-item">
                <label>Change Password</label>
                <button className="action-btn" onClick={() => setShowPasswordModal(true)}>Update Password</button>
              </div>
            </div>
            
            <div className="settings-section">
              <h3>🔔 Notifications</h3>
              <div className="setting-item">
                <label>Email Notifications</label>
                <input type="checkbox" defaultChecked />
              </div>
              <div className="setting-item">
                <label>Security Alerts</label>
                <input type="checkbox" defaultChecked />
              </div>
              <div className="setting-item">
                <label>Weekly Reports</label>
                <input type="checkbox" />
              </div>
            </div>
          </div>
        )}
        
        {showPasswordModal && (
          <div className="modal">
            <div className="modal-content">
              <div className="modal-header">
                <h2>🔑 Change Password</h2>
                <button 
                  className="close-btn"
                  onClick={() => {
                    setShowPasswordModal(false);
                    setPasswordError('');
                    setPasswordForm({ currentPassword: '', newPassword: '', confirmPassword: '' });
                  }}
                >
                  ✕
                </button>
              </div>
              <form onSubmit={updatePassword}>
                <div className="password-form">
                  {passwordError && (
                    <div className="error-message">
                      ❌ {passwordError}
                    </div>
                  )}
                  <div className="form-group">
                    <label>Current Password</label>
                    <input
                      type="password"
                      value={passwordForm.currentPassword}
                      onChange={(e) => {
                        setPasswordForm({...passwordForm, currentPassword: e.target.value});
                        setPasswordError(''); // Clear error when typing
                      }}
                      required
                    />
                  </div>
                  <div className="form-group">
                    <label>New Password</label>
                    <input
                      type="password"
                      value={passwordForm.newPassword}
                      onChange={(e) => {
                        setPasswordForm({...passwordForm, newPassword: e.target.value});
                        setPasswordError(''); // Clear error when typing
                      }}
                      required
                    />
                  </div>
                  <div className="form-group">
                    <label>Confirm New Password</label>
                    <input
                      type="password"
                      value={passwordForm.confirmPassword}
                      onChange={(e) => {
                        setPasswordForm({...passwordForm, confirmPassword: e.target.value});
                        setPasswordError(''); // Clear error when typing
                      }}
                      required
                      style={{
                        borderColor: passwordForm.confirmPassword && passwordForm.newPassword !== passwordForm.confirmPassword ? '#ff6b6b' : '#eee'
                      }}
                    />
                    {passwordForm.confirmPassword && passwordForm.newPassword !== passwordForm.confirmPassword && (
                      <small style={{color: '#ff6b6b', fontSize: '0.8rem', marginTop: '0.25rem', display: 'block'}}>
                        ❌ Passwords do not match
                      </small>
                    )}
                  </div>
                  <div className="form-actions">
                    <button type="button" onClick={() => setShowPasswordModal(false)}>Cancel</button>
                    <button type="submit">Update Password</button>
                  </div>
                </div>
              </form>
            </div>
          </div>
        )}
        </div>
      </main>
    </div>
  );
}

export default App;