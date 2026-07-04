#!/bin/bash

# Setup script for Last-Mile Route Optimizer
# This script sets up both backend and frontend

set -e

echo "🚀 Setting up Last-Mile Route Optimizer..."
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if Python 3.10+ is installed
echo -e "${BLUE}Checking Python version...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed. Please install Python 3.10 or higher.${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo -e "${GREEN}✓ Found Python ${PYTHON_VERSION}${NC}"

# Check if Node.js is installed
echo -e "${BLUE}Checking Node.js version...${NC}"
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js is not installed. Please install Node.js 18 or higher.${NC}"
    exit 1
fi

NODE_VERSION=$(node --version)
echo -e "${GREEN}✓ Found Node.js ${NODE_VERSION}${NC}"

# Setup Backend
echo ""
echo -e "${BLUE}📦 Setting up Backend...${NC}"
cd backend

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo -e "${GREEN}✓ Created .env file. Please review and update if needed.${NC}"
fi

cd ..

# Setup Frontend
echo ""
echo -e "${BLUE}📦 Setting up Frontend...${NC}"
cd frontend

# Install dependencies
echo "Installing Node.js dependencies..."
npm install

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo -e "${GREEN}✓ Created .env file. Please review and update if needed.${NC}"
fi

cd ..

# Summary
echo ""
echo -e "${GREEN}✅ Setup complete!${NC}"
echo ""
echo "To start the application:"
echo ""
echo -e "${BLUE}Backend:${NC}"
echo "  cd backend"
echo "  source venv/bin/activate"
echo "  uvicorn app.main:app --reload"
echo ""
echo -e "${BLUE}Frontend:${NC}"
echo "  cd frontend"
echo "  npm run dev"
echo ""
echo -e "${BLUE}Or use Docker Compose:${NC}"
echo "  docker-compose up"
echo ""
echo "📚 Read README.md for more information"
echo ""
