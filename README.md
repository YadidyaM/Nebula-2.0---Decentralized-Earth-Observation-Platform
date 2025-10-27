# 🌌 Nebula Protocol - Proof of Future

> **A Decentralized Environmental Monitoring Network powered by Solana Blockchain & Swarms AI**

[![Built for Proof of Future](https://img.shields.io/badge/Built%20for-Proof%20of%20Future-blue?style=for-the-badge&logo=ethereum)](https://proofoffuture.dev)
[![Solana](https://img.shields.io/badge/Solana-Web3-orange?style=for-the-badge&logo=solana)](https://solana.com)
[![Swarms AI](https://img.shields.io/badge/Swarms-AI-purple?style=for-the-badge&logo=openai)](https://swarms.ai)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

<p align="center">
  <img src="https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExenRsZ3Q0eDNyNXFjaGtsemN3NHc3ZTBocXM4MDQ2NXpocTMxdGt0YSZlcD12MV9naWZzX3NlYXJjaCZjdD1n/8Am0UlfiwZcgEDOy4h/giphy.gif" height="140" />
</p>

🔗 **Live Demo:** https://nebulav2.netlify.app/

## 🎯 **Overview**

### **Situation**
Climate change poses an existential threat to our planet. Traditional environmental monitoring systems are centralized, expensive, and lack transparency. We need a decentralized solution that empowers communities to monitor and protect their environment while providing verifiable data on-chain.

### **Task**
Build a comprehensive environmental monitoring platform that combines:
- **Solana Blockchain** for transparent, immutable environmental data storage
- **Swarms AI** for intelligent agent coordination and environmental analysis
- **Real-time monitoring** of environmental threats and conditions
- **Community-driven** environmental protection initiatives

### **Action**
We created Nebula Protocol - a decentralized environmental monitoring network featuring our own satellite that follows real physics:

#### **🔗 Solana Integration**
- **Smart Contracts** for mission deployment and reward distribution
- **NFT Agents** representing environmental monitoring satellites
- **Token Economics** with $NEBULA tokens for ecosystem participation
- **On-chain Verification** of environmental data and mission completion
- **Multi-wallet Support** with Phantom, Solflare, and other Solana wallets

#### **🤖 Swarms AI Orchestration**
- **8 Specialized AI Agents** for different environmental monitoring tasks:
- 🌲 **Forest Guardian** - Deforestation and wildfire detection
- 🧊 **Ice Sentinel** - Arctic ice monitoring and climate tracking
- ⛈️ **Storm Tracker** - Weather pattern analysis and storm prediction
- 🏙️ **Urban Monitor** - Air quality and urban environmental health
- 💧 **Water Watcher** - Water quality and flood monitoring
- 🛡️ **Security Sentinel** - System security and threat detection
- 🌍 **Land Surveyor** - Geological and land use monitoring
- 🚨 **Disaster Responder** - Emergency response coordination
- **Hierarchical Swarm Coordination** for complex multi-agent missions
- **Real-time Decision Making** based on environmental data analysis
- **Adaptive Learning** from environmental patterns and user feedback

#### **🌍 Environmental Monitoring Features**
- **Real-time Satellite Data** from NASA, NOAA, USGS, and ESA
- **Custom Satellite Simulation** with real physics orbital mechanics
- **Risk Detection Algorithms** for floods, droughts, wildfires, earthquakes
- **Interactive 3D Earth Visualization** with live environmental data
- **Mission Control Dashboard** for coordinating monitoring operations
- **Community Alerts** for environmental threats and opportunities

### **Result**
A fully functional decentralized environmental monitoring platform that:
- ✅ **Monitors** environmental conditions in real-time across the globe
- ✅ **Rewards** community members for environmental data contribution
- ✅ **Predicts** environmental threats using AI-powered analysis
- ✅ **Coordinates** response efforts through decentralized governance
- ✅ **Transparent** data storage on Solana blockchain
- ✅ **Scalable** architecture supporting global environmental monitoring

---

## 🚀 **Quick Start**

### **Prerequisites**
- Node.js 18+ and npm/yarn
- Python 3.9+ and pip
- MongoDB 5.0+
- Solana CLI tools
- Git

### **1. Clone Repository**
```bash
git clone (https://github.com/YadidyaM/Nebula-2.0---Decentralized-Earth-Observation-Platform.git)]
cd nebula-protocol
```

### **2. Backend Setup**
```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration (see Required Keys section)

# Start MongoDB
mongod

# Run database migrations
python -m app.db.migrate

# Start the backend server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### **3. Frontend Setup**
```bash
cd frontend

# Install dependencies
npm install

# Set up environment variables
cp .env.example .env.local
# Edit .env.local with your configuration

# Start the development server
npm run dev
```

### **4. Access the Application**
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000


---

## 🔑 **Required API Keys & Configuration**

### **Environment Variables**

#### **Backend (.env)**
```bash
# Database
MONGODB_URL=mongodb://localhost:27017/nebula_protocol

# Solana Configuration
SOLANA_RPC_URL=[https://api.devnet.solana.com](https://api.devnet.solana.com)
SOLANA_PRIVATE_KEY=your_solana_private_key_here
SOLANA_PROGRAM_ID=your_program_id_here

# Swarms AI Configuration
SWARMS_API_KEY=your_swarms_api_key_here
SWARMS_BASE_URL=[https://api.swarms.ai](https://api.swarms.ai)

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
```

#### **Frontend (.env.local)**
```bash
# API Configuration
VITE_API_URL=http://localhost:8000/api/v1
VITE_WS_URL=ws://localhost:8000/ws

# Solana Configuration
VITE_SOLANA_RPC_URL=[https://api.devnet.solana.com](https://api.devnet.solana.com)
VITE_SOLANA_NETWORK=devnet

# External Services
VITE_MAPBOX_TOKEN=your_mapbox_token_here
VITE_GEMINI_API_KEY=your_gemini_api_key_here

# Feature Flags
VITE_ENABLE_VOICE_COMMANDS=true
VITE_ENABLE_3D_VISUALIZATION=true
```

### **Required API Keys**

#### **🌌 Solana**
1. **Solana RPC Endpoint**: Get from [Solana RPC Providers](https://docs.solana.com/cluster/rpc-endpoints)
   - **Devnet**: `https://api.devnet.solana.com` (free)
   - **Mainnet**: Use Alchemy, QuickNode, or Helius (paid)

2. **Solana Wallet**: Generate using Solana CLI
   ```bash
   solana-keygen new --outfile ~/.config/solana/id.json
   ```

#### **🤖 Swarms AI**
1. **Swarms API Key**: Get from [Swarms AI Platform](https://swarms.ai)
   - Sign up for developer access
   - Generate API key from dashboard
   - Configure agent models and parameters

#### **🛰️ Environmental Data APIs**
1. **NASA API**: Get from [NASA API Portal](https://api.nasa.gov)
   - Free tier: 1000 requests/hour
   - Required for satellite imagery and Earth observation data

2. **NOAA API**: Get from [NOAA API](https://www.weather.gov/documentation/services-web-api)
   - Free tier: 1000 requests/day
   - Required for weather data and storm tracking

3. **USGS API**: Get from [USGS API](https://earthquake.usgs.gov/fdsnws/event/1/)
   - Free tier: No rate limits
   - Required for earthquake and geological data

4. **Mapbox Token**: Get from [Mapbox](https://www.mapbox.com)
   - Free tier: 50,000 map loads/month
   - Required for interactive maps and geospatial visualization

#### **🔊 Additional Services**
1. **Google Gemini API**: Get from [Google AI Studio](https://makersuite.google.com)
   - Free tier: 15 requests/minute
   - Required for voice commands and AI chat

2. **IPFS/Arweave**: For decentralized data storage
   - **Pinata**: Get from [Pinata](https://pinata.cloud) (IPFS)
   - **Bundlr**: Get from [Bundlr](https://bundlr.network) (Arweave)

---

## 🏗️ **Architecture Overview**

### **System Architecture**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   Blockchain    │
│   (React/Vite)  │◄──►│   (FastAPI)     │◄──►│   (Solana)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   WebSocket     │    │   Swarms AI     │    │   IPFS/Arweave  │
│   (Real-time)   │    │   (Agents)      │    │   (Storage)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### **Key Components**

#### **Frontend (React + TypeScript)**
- **Dashboard**: Main mission control interface
- **3D Visualization**: Three.js Earth scene with satellite orbits
- **Real-time Charts**: Environmental data visualization
- **Wallet Integration**: Solana wallet connection and management
- **Voice Commands**: AI-powered voice interface

#### **Backend (FastAPI + Python)**
- **REST API**: Mission management and data endpoints
- **WebSocket Server**: Real-time data streaming
- **Swarms AI Integration**: Agent coordination and management
- **Data Sources**: NASA, NOAA, USGS API integration
- **MongoDB**: Environmental data and user management

#### **Blockchain (Solana)**
- **Smart Contracts**: Mission deployment and rewards
- **NFT Agents**: Environmental monitoring satellites
- **Token Economics**: $NEBULA ecosystem tokens
- **Data Verification**: On-chain environmental data storage

---

## 🎮 **How to Use**

### **1. Connect Wallet**
- Click "Connect Wallet" in the top-right corner
- Select your Solana wallet (Phantom, Solflare, etc.)
- Approve the connection

### **2. Deploy Mission**
- Navigate to the Mission Control panel
- Click "Launch Mission"
- Select environmental monitoring parameters
- Confirm transaction on Solana

### **3. Monitor Environment**
- View real-time environmental data on the dashboard
- Track satellite positions and telemetry
- Receive alerts for environmental threats
- Analyze trends and patterns

### **4. Earn Rewards**
- Complete environmental monitoring missions
- Contribute verified environmental data
- Participate in community governance
- Earn $NEBULA tokens for contributions

---

## 🛠️ **Development**

### **Tech Stack**
- **Frontend**: React 18, TypeScript, Vite, Tailwind CSS, Three.js
- **Backend**: FastAPI, Python 3.9+, MongoDB, Redis
- **Blockchain**: Solana, Anchor Framework
- **AI**: Swarms AI, OpenAI GPT-4, Google Gemini
- **Data Sources**: NASA APIs, NOAA APIs, USGS APIs
- **Satellite Physics**: SGP4 orbital mechanics, real-time position calculations
- **Maps**: Mapbox GL JS
- **Real-time**: WebSockets, Server-Sent Events

### **Project Structure**
```
nebula-protocol/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API endpoints
│   │   ├── agents/         # Swarms AI agents
│   │   ├── db/             # Database models
│   │   ├── services/       # External API services
│   │   └── main.py         # FastAPI application
│   └── requirements.txt
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── contexts/      # React contexts
│   │   ├── hooks/         # Custom hooks
│   │   ├── lib/           # Utility libraries
│   │   ├── pages/         # Page components
│   │   └── styles/        # CSS styles
│   └── package.json
├── contracts/             # Solana smart contracts
└── docs/                 # Documentation
```

### **Running Tests**
```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

---

## 🌟 **Features**

### **🔗 Solana Integration**
- ✅ Multi-wallet support (Phantom, Solflare, etc.)
- ✅ NFT-based environmental monitoring agents
- ✅ Token rewards for environmental contributions
- ✅ On-chain mission verification
- ✅ Decentralized governance

### **🤖 Swarms AI**
- ✅ 8 specialized environmental monitoring agents
- ✅ Hierarchical swarm coordination
- ✅ Real-time environmental analysis
- ✅ Adaptive learning from data patterns
- ✅ Intelligent mission planning

### **🌍 Environmental Monitoring**
- ✅ Real-time satellite data integration
- ✅ **Custom satellite simulation with real physics orbital mechanics**
- ✅ **SGP4-based orbital calculations for accurate satellite positioning**
- ✅ Risk detection algorithms
- ✅ Interactive 3D Earth visualization
- ✅ Community alert system
- ✅ Mission control dashboard

### **🎨 User Experience**
- ✅ Cinematic holographic UI
- ✅ Voice command interface
- ✅ Real-time data visualization
- ✅ Mobile-responsive design
- ✅ Accessibility features

---

## 🤝 **Contributing**

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### **Development Setup**
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

---

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🏆 **Hackathon Submission**

**Built for**: Proof of Future Global Youth Web3 IdeaLab Hackathon

**Track**: Environmental Sustainability & Climate Action

**Technologies Used**:
- **Solana Blockchain** for decentralized environmental data storage
- **Swarms AI** for intelligent agent coordination
- **Real-time Environmental Monitoring** with satellite data
- **Community-driven** environmental protection

**Impact**: Empowering communities to monitor and protect their environment through decentralized technology and AI-powered insights.

---

## 📞 **Contact**

- **Email**: yadikrish@gmail.com


---

## 🙏 **Acknowledgments**

- **Solana Foundation** for blockchain infrastructure
- **Swarms AI** for AI agent coordination platform
- **NASA, NOAA, USGS** for environmental data APIs
- **Proof of Future** for organizing this amazing hackathon
- **Open Source Community** for the amazing tools and libraries

---

*Built with ❤️ for a sustainable future*


