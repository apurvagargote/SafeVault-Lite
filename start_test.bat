@echo off
echo 🔐 SafeVault System Test
echo ========================

echo.
echo 📋 Test Checklist:
echo [ ] 1. Start Backend Server
echo [ ] 2. Run System Tests
echo [ ] 3. Test Frontend UI
echo.

echo 🚀 Starting Backend Server...
start "SafeVault Backend" cmd /k "cd backend && python app.py"

echo.
echo ⏳ Waiting for backend to start...
timeout /t 5

echo.
echo 🧪 Running System Tests...
python test_system.py

echo.
echo 🌐 Frontend Testing:
echo 1. Open http://localhost:3000 in your browser
echo 2. Test signup with new account
echo 3. Test login with created account
echo 4. Test creating/viewing/deleting secrets
echo.

echo 🎯 Manual Test Steps:
echo ✓ Signup: Create account with username/email/password
echo ✓ Login: Login with created credentials
echo ✓ Create Secret: Add a new secret (API key, password, etc.)
echo ✓ View Secret: Click on secret to view value
echo ✓ Copy Secret: Use copy button to copy to clipboard
echo ✓ Delete Secret: Delete a secret (admin only)
echo ✓ Logout: Test logout functionality
echo.

pause