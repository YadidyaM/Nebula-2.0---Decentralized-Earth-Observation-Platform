#!/bin/bash

# Nebula Protocol Setup Script
# Proof of Future Global Youth Web3 IdeaLab Hackathon

set -e

echo "🌌 Nebula Protocol Setup Script"
echo "================================"
echo "Built for Proof of Future Global Youth Web3 IdeaLab Hackathon"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_info() {
    echo -e "${BLUE}[i]${NC} $1"
}

print_header() {
    echo -e "${PURPLE}$1${NC}"
}

# Check if running on Windows
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    IS_WINDOWS=true
else
    IS_WINDOWS=false
fi

print_header "🔍 Checking Prerequisites..."

# Check Node.js
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    print_status "Node.js found: $NODE_VERSION"
else
    print_error "Node.js not found. Please install Node.js 18+ from https://nodejs.org/"
    exit 1
fi

# Check Python
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    print_status "Python found: $PYTHON_VERSION"
else
    print_error "Python 3.9+ not found. Please install Python from https://python.org/"
    exit 1
fi

# Check MongoDB
if command -v mongod &> /dev/null; then
    print_status "MongoDB found"
else
    print_warning "MongoDB not found. Please install MongoDB 5.0+ from https://mongodb.com/"
fi

# Check Git
if command -v git &> /dev/null; then
    print_status "Git found"
else
    print_error "Git not found. Please install Git from https://git-scm.com/"
    exit 1
fi

print_header "📦 Installing Dependencies..."

# Install backend dependencies
print_info "Installing Python dependencies..."
cd backend
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    print_status "Backend dependencies installed"
else
    print_error "requirements.txt not found in backend directory"
    exit 1
fi
cd ..

# Install frontend dependencies
print_info "Installing Node.js dependencies..."
cd frontend
if [ -f "package.json" ]; then
    npm install
    print_status "Frontend dependencies installed"
else
    print_error "package.json not found in frontend directory"
    exit 1
fi
cd ..

print_header "🔑 Setting up Environment Variables..."

# Create backend .env file
if [ ! -f "backend/.env" ]; then
    print_info "Creating backend .env file..."
    cat > backend/.env << EOF
# Database
MONGODB_URL=mongodb://localhost:27017/nebula_protocol

# Solana Configuration
SOLANA_RPC_URL=https://api.devnet.solana.com
SOLANA_PRIVATE_KEY=your_solana_private_key_here
SOLANA_PROGRAM_ID=your_program_id_here

# Swarms AI Configuration
SWARMS_API_KEY=your_swarms_api_key_here
SWARMS_BASE_URL=https://api.swarms.ai

# External APIs
NASA_API_KEY=your_nasa_api_key_here
NOAA_API_KEY=your_noaa_api_key_here
USGS_API_KEY=your_usgs_api_key_here
MAPBOX_TOKEN=your_mapbox_token_here

# Security
JWT_SECRET_KEY=your_jwt_secret_here
ENCRYPTION_KEY=your_encryption_key_here

# Redis (for caching)
REDIS_URL=redis://localhost:6379
EOF
    print_status "Backend .env file created"
else
    print_warning "Backend .env file already exists"
fi

# Create frontend .env.local file
if [ ! -f "frontend/.env.local" ]; then
    print_info "Creating frontend .env.local file..."
    cat > frontend/.env.local << EOF
# API Configuration
VITE_API_URL=http://localhost:8000/api/v1
VITE_WS_URL=ws://localhost:8000/ws

# Solana Configuration
VITE_SOLANA_RPC_URL=https://api.devnet.solana.com
VITE_SOLANA_NETWORK=devnet

# External Services
VITE_MAPBOX_TOKEN=your_mapbox_token_here
VITE_GEMINI_API_KEY=your_gemini_api_key_here

# Feature Flags
VITE_ENABLE_VOICE_COMMANDS=true
VITE_ENABLE_3D_VISUALIZATION=true
EOF
    print_status "Frontend .env.local file created"
else
    print_warning "Frontend .env.local file already exists"
fi

print_header "🗄️ Setting up Database..."

# Start MongoDB if not running
if ! pgrep -x "mongod" > /dev/null; then
    print_info "Starting MongoDB..."
    if [ "$IS_WINDOWS" = true ]; then
        start mongod
    else
        mongod --fork --logpath /tmp/mongod.log
    fi
    sleep 3
    print_status "MongoDB started"
else
    print_status "MongoDB is already running"
fi

print_header "🚀 Starting Services..."

# Function to start backend
start_backend() {
    print_info "Starting backend server..."
    cd backend
    if [ "$IS_WINDOWS" = true ]; then
        start "Backend Server" cmd /k "uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
    else
        uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
        BACKEND_PID=$!
    fi
    cd ..
    print_status "Backend server starting on http://localhost:8000"
}

# Function to start frontend
start_frontend() {
    print_info "Starting frontend development server..."
    cd frontend
    if [ "$IS_WINDOWS" = true ]; then
        start "Frontend Server" cmd /k "npm run dev"
    else
        npm run dev &
        FRONTEND_PID=$!
    fi
    cd ..
    print_status "Frontend server starting on http://localhost:3000"
}

# Start services
start_backend
sleep 2
start_frontend

print_header "✅ Setup Complete!"

echo ""
echo -e "${CYAN}🌌 Nebula Protocol is now running!${NC}"
echo ""
echo -e "${GREEN}Frontend:${NC} http://localhost:3000"
echo -e "${GREEN}Backend API:${NC} http://localhost:8000"
echo -e "${GREEN}API Documentation:${NC} http://localhost:8000/docs"
echo ""
echo -e "${YELLOW}⚠️  Important:${NC} Please update the API keys in the .env files:"
echo ""
echo -e "${BLUE}Required API Keys:${NC}"
echo "• Solana RPC URL (free devnet available)"
echo "• Swarms AI API Key (get from https://swarms.ai)"
echo "• NASA API Key (get from https://api.nasa.gov)"
echo "• NOAA API Key (get from https://www.weather.gov/documentation/services-web-api)"
echo "• USGS API Key (get from https://earthquake.usgs.gov/fdsnws/event/1/)"
echo "• Mapbox Token (get from https://www.mapbox.com)"
echo "• Google Gemini API Key (get from https://makersuite.google.com)"
echo ""
echo -e "${BLUE}🛰️  Satellite Physics Features:${NC}"
echo "• SGP4 orbital mechanics library for real physics simulation"
echo "• Three.js 3D visualization with accurate satellite positioning"
echo "• Real-time orbital pass predictions and ground track calculations"
echo ""
echo -e "${PURPLE}📚 Documentation:${NC}"
echo "• README.md - Complete setup guide"
echo "• Architecture.md - Technical architecture"
echo "• API Documentation - http://localhost:8000/docs"
echo ""
echo -e "${GREEN}🎉 Happy coding for Proof of Future!${NC}"

# Keep script running if not Windows
if [ "$IS_WINDOWS" = false ]; then
    echo ""
    echo "Press Ctrl+C to stop all services"
    wait
fi
