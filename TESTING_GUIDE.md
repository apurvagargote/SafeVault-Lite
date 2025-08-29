# 🧪 SafeVault Testing Guide

## Prerequisites
1. **Backend Server Running**: `cd backend && python app.py`
2. **Frontend Server Running**: `cd frontend && npm start`

## Manual Testing Steps

### 🔐 Authentication Tests

#### 1. Test Signup
- Open http://localhost:3000
- Click "Sign up here"
- Fill form:
  - Username: `testuser`
  - Email: `test@example.com`
  - Password: `testpass123`
  - Role: `User`
- Click "Create Account"
- **Expected**: Success message + redirect to login

#### 2. Test Login
- Enter credentials:
  - Username: `testuser`
  - Password: `testpass123`
- Click "Unlock Vault"
- **Expected**: Lock animation + successful login

### 🗝️ Secrets Management Tests

#### 3. Test Create Secret
- Click "+ Add Secret"
- Fill form:
  - Name: `test-api-key`
  - Value: `sk-1234567890abcdef`
  - Description: `Test API key`
- Click "Create Secret"
- **Expected**: Secret appears in list immediately

#### 4. Test View Secret
- Click "👁️" on the secret
- **Expected**: Modal opens showing secret details
- Click "👁️" to show/hide value
- Click "📋" to copy to clipboard

#### 5. Test Search
- Type "test" in search bar
- **Expected**: Only matching secrets shown

#### 6. Test Delete (Admin Only)
- Create admin account with role "Admin"
- Login as admin
- Click "🗑️" on a secret
- Confirm deletion
- **Expected**: Secret removed from list

#### 7. Test Logout
- Click "🚪 Logout"
- **Expected**: Redirect to login page

## API Testing (Using Browser DevTools or Postman)

### 1. Signup API
```
POST http://localhost:8000/signup
Content-Type: application/json

{
  "username": "apitest",
  "email": "api@test.com", 
  "password": "password123",
  "role": "user"
}
```

### 2. Login API
```
POST http://localhost:8000/login
Content-Type: application/json

{
  "username": "apitest",
  "password": "password123"
}
```

### 3. Create Secret API
```
POST http://localhost:8000/secrets
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json

{
  "name": "api-secret",
  "value": "secret-value-123",
  "description": "API test secret"
}
```

### 4. List Secrets API
```
GET http://localhost:8000/secrets
Authorization: Bearer <JWT_TOKEN>
```

### 5. Get Secret API
```
GET http://localhost:8000/secrets/api-secret
Authorization: Bearer <JWT_TOKEN>
```

### 6. Delete Secret API (Admin only)
```
DELETE http://localhost:8000/secrets/api-secret
Authorization: Bearer <JWT_TOKEN>
```

## Expected Results ✅

- **Signup**: User created in database
- **Login**: JWT token returned
- **Create Secret**: Secret stored (AWS/Local)
- **List Secrets**: All user secrets returned
- **View Secret**: Secret value displayed
- **Delete Secret**: Secret removed (admin only)
- **UI Animations**: Lock opens, smooth transitions
- **Persistence**: Login state maintained on refresh

## Troubleshooting 🔧

### Backend Issues
- Check if backend is running on port 8000
- Verify database connection (SQLite file created)
- Check console for errors

### Frontend Issues  
- Check if frontend is running on port 3000
- Open browser DevTools for JavaScript errors
- Verify API calls in Network tab

### Database Issues
- Check if `safevault.db` file is created in backend folder
- Verify SQLAlchemy tables are created

## Test Checklist ✓

- [ ] Signup with new user
- [ ] Login with created user  
- [ ] JWT token stored in localStorage
- [ ] Create new secret
- [ ] View secret in list
- [ ] Open secret details modal
- [ ] Copy secret to clipboard
- [ ] Search/filter secrets
- [ ] Logout functionality
- [ ] Login persistence on refresh
- [ ] Admin role can delete secrets
- [ ] User role cannot delete secrets
- [ ] Lock animation on login
- [ ] Responsive design on mobile

## Success Criteria 🎯

All tests pass = **SafeVault is ready for production deployment!**