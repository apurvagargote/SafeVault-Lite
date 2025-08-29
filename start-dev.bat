@echo off
echo Starting SafeVault Development Environment...

echo Starting Backend...
start cmd /k "cd backend && python -m pip install -r requirements.txt && python app.py"

timeout /t 3

echo Starting Frontend...
start cmd /k "cd frontend && npm install && npm start"

echo Both services starting...
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000