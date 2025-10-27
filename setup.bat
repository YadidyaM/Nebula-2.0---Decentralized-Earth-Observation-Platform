@echo off
setlocal enabledelayedexpansion

echo 🌌 Nebula Protocol Setup Script
echo ================================
echo Built for Proof of Future Global Youth Web3 IdeaLab Hackathon
echo.

echo 🔍 Checking Prerequisites...

:: Check Node.js
node --version >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=*" %%i in ('node --version') do set NODE_VERSION=%%i
    echo [✓] Node.js found: !NODE_VERSION!
) else (
    echo [✗] Node.js not found. Please install Node.js 18+ from https://nodejs.org/
    pause
    exit /b 1
)

:: Check Python
python --version >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=*" %%i in ('python --version') do set PYTHON_VERSION=%%i
    echo [✓] Python found: !PYTHON_VERSION!
) else (
    echo [✗] Python 3.9+ not found. Please install Python from https://python.org/
    pause
    exit /b 1
)

:: Check MongoDB
mongod --version >nul 2>&1
if %errorlevel% equ 0 (
    echo [✓] MongoDB found
) else (
    echo [!] MongoDB not found. Please install MongoDB 5.0+ from https://mongodb.com/
)

:: Check Git
git --version >nul 2>&1
if %errorlevel% equ 0 (
    echo [✓] Git found
) else (
    echo [✗] Git not found. Please install Git from https://git-scm.com/
    pause
    exit /b 1
)

echo.
echo 📦 Installing Dependencies...

:: Install backend dependencies
echo [i] Installing Python dependencies...
cd backend
if exist requirements.txt (
    pip install -r requirements.txt
    echo [✓] Backend dependencies installed
) else (
    echo [✗] requirements.txt not found in backend directory
    pause
    exit /b 1
)
cd ..

:: Install frontend dependencies
echo [i] Installing Node.js dependencies...
cd frontend
if exist package.json (
    npm install
    echo [✓] Frontend dependencies installed
) else (
    echo [✗] package.json not found in frontend directory
    pause
    exit /b 1
)
cd ..

echo.
echo 🔑 Setting up Environment Variables...

:: Create backend .env file
if not exist "backend\.env" (
    echo [i] Creating backend .env file...
    (
        echo # Database
        echo MONGODB_URL=mongodb://localhost:27017/nebula_protocol
        echo.
        echo # Solana Configuration
        echo SOLANA_RPC_URL=https://api.devnet.solana.com
        echo SOLANA_PRIVATE_KEY=your_solana_private_key_here
        echo SOLANA_PROGRAM_ID=your_program_id_here
        echo.
        echo # Swarms AI Configuration
        echo SWARMS_API_KEY=your_swarms_api_key_here
        echo SWARMS_BASE_URL=https://api.swarms.ai
        echo.
        echo # External APIs
        echo NASA_API_KEY=your_nasa_api_key_here
        echo NOAA_API_KEY=your_noaa_api_key_here
        echo USGS_API_KEY=your_usgs_api_key_here
        echo MAPBOX_TOKEN=your_mapbox_token_here
        echo.
        echo # Security
        echo JWT_SECRET_KEY=your_jwt_secret_here
        echo ENCRYPTION_KEY=your_encryption_key_here
        echo.
        echo # Redis ^(for caching^)
        echo REDIS_URL=redis://localhost:6379
    ) > backend\.env
    echo [✓] Backend .env file created
) else (
    echo [!] Backend .env file already exists
)

:: Create frontend .env.local file
if not exist "frontend\.env.local" (
    echo [i] Creating frontend .env.local file...
    (
        echo # API Configuration
        echo VITE_API_URL=http://localhost:8000/api/v1
        echo VITE_WS_URL=ws://localhost:8000/ws
        echo.
        echo # Solana Configuration
        echo VITE_SOLANA_RPC_URL=https://api.devnet.solana.com
        echo VITE_SOLANA_NETWORK=devnet
        echo.
        echo # External Services
        echo VITE_MAPBOX_TOKEN=your_mapbox_token_here
        echo VITE_GEMINI_API_KEY=your_gemini_api_key_here
        echo.
        echo # Feature Flags
        echo VITE_ENABLE_VOICE_COMMANDS=true
        echo VITE_ENABLE_3D_VISUALIZATION=true
    ) > frontend\.env.local
    echo [✓] Frontend .env.local file created
) else (
    echo [!] Frontend .env.local file already exists
)

echo.
echo 🗄️ Setting up Database...

:: Start MongoDB if not running
tasklist /FI "IMAGENAME eq mongod.exe" 2>NUL | find /I /N "mongod.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo [✓] MongoDB is already running
) else (
    echo [i] Starting MongoDB...
    start mongod
    timeout /t 3 /nobreak >nul
    echo [✓] MongoDB started
)

echo.
echo 🚀 Starting Services...

:: Start backend
echo [i] Starting backend server...
cd backend
start "Backend Server" cmd /k "uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
cd ..
echo [✓] Backend server starting on http://localhost:8000

:: Wait a moment
timeout /t 2 /nobreak >nul

:: Start frontend
echo [i] Starting frontend development server...
cd frontend
start "Frontend Server" cmd /k "npm run dev"
cd ..
echo [✓] Frontend server starting on http://localhost:3000

echo.
echo ✅ Setup Complete!
echo.
echo 🌌 Nebula Protocol is now running!
echo.
echo Frontend: http://localhost:3000
echo Backend API: http://localhost:8000
echo API Documentation: http://localhost:8000/docs
echo.
echo ⚠️  Important: Please update the API keys in the .env files:
echo.
echo Required API Keys:
echo • Solana RPC URL ^(free devnet available^)
echo • Swarms AI API Key ^(get from https://swarms.ai^)
echo • NASA API Key ^(get from https://api.nasa.gov^)
echo • NOAA API Key ^(get from https://www.weather.gov/documentation/services-web-api^)
echo • USGS API Key ^(get from https://earthquake.usgs.gov/fdsnws/event/1/^)
echo • Mapbox Token ^(get from https://www.mapbox.com^)
echo • Google Gemini API Key ^(get from https://makersuite.google.com^)
echo.
echo 🛰️  Satellite Physics Features:
echo • SGP4 orbital mechanics library for real physics simulation
echo • Three.js 3D visualization with accurate satellite positioning
echo • Real-time orbital pass predictions and ground track calculations
echo.
echo 📚 Documentation:
echo • README.md - Complete setup guide
echo • Architecture.md - Technical architecture
echo • API Documentation - http://localhost:8000/docs
echo.
echo 🎉 Happy coding for Proof of Future!
echo.
pause
