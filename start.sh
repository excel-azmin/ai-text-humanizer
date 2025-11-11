#!/bin/bash

# AI Text Humanizer - Setup and Run Script
# Combined setup and execution script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to check if setup is needed
check_setup() {
    if [ ! -d "venv" ] || [ ! -f ".env" ]; then
        return 0  # Setup needed
    fi
    return 1  # Setup not needed
}

# Ensure key Python dependencies are installed in current environment
ensure_deps() {
    # Activate virtual environment if present but not already activated
    if [ -d "venv" ] && [ -z "$VIRTUAL_ENV" ]; then
        # shellcheck disable=SC1091
        source venv/bin/activate
    fi
    # Check for FastAPI as sentinel; install requirements if missing
    if ! python -c "import fastapi" >/dev/null 2>&1; then
        echo -e "${YELLOW}Installing required Python packages...${NC}"
        pip install -r requirements.txt
        echo -e "${GREEN}✓ Dependencies installed${NC}"
    fi
}

# Setup function
setup() {
    echo -e "${BLUE}🚀 AI Text Humanizer Setup${NC}"
    echo "=========================="

    # Check Python version
    echo -e "${YELLOW}Checking Python version...${NC}"
    python_version=$(python3 --version 2>&1 | grep -Po '(?<=Python )\d+\.\d+')
    required_version="3.8"

    if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" = "$required_version" ]; then 
        echo -e "${GREEN}✓ Python $python_version is installed${NC}"
    else
        echo -e "${RED}✗ Python 3.8+ is required. Found: $python_version${NC}"
        exit 1
    fi

    # Check for GPU support
    echo -e "${YELLOW}Checking for GPU support...${NC}"
    if command -v nvidia-smi &> /dev/null; then
        echo -e "${GREEN}✓ NVIDIA GPU detected${NC}"
        nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
        USE_GPU="true"
    else
        echo -e "${YELLOW}⚠ No NVIDIA GPU detected. Will use CPU mode${NC}"
        USE_GPU="false"
    fi

    # Create virtual environment
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        echo -e "${GREEN}✓ Virtual environment created${NC}"
    else
        echo -e "${GREEN}✓ Virtual environment already exists${NC}"
    fi

    # Activate virtual environment
    source venv/bin/activate

    # Upgrade pip
    echo -e "${YELLOW}Upgrading pip...${NC}"
    pip install --upgrade pip wheel setuptools > /dev/null 2>&1
    echo -e "${GREEN}✓ Pip upgraded${NC}"

    # Install PyTorch based on GPU availability
    echo -e "${YELLOW}Installing PyTorch...${NC}"
    if [ "$USE_GPU" = "true" ]; then
        pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118 > /dev/null 2>&1
        echo -e "${GREEN}✓ PyTorch installed with CUDA support${NC}"
    else
        pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu > /dev/null 2>&1
        echo -e "${GREEN}✓ PyTorch installed (CPU only)${NC}"
    fi

    # Install requirements
    echo -e "${YELLOW}Installing dependencies...${NC}"
    pip install -r requirements.txt > /dev/null 2>&1
    echo -e "${GREEN}✓ Dependencies installed${NC}"

    # Download spaCy model
    echo -e "${YELLOW}Downloading language models...${NC}"
    python -m spacy download en_core_web_sm > /dev/null 2>&1
    echo -e "${GREEN}✓ SpaCy model downloaded${NC}"

    # Download NLTK data
    echo -e "${YELLOW}Downloading NLTK data...${NC}"
    python -c "import nltk; nltk.download('punkt', quiet=True); nltk.download('wordnet', quiet=True); nltk.download('omw-1.4', quiet=True)"
    echo -e "${GREEN}✓ NLTK data downloaded${NC}"

    # Check Redis
    echo -e "${YELLOW}Checking Redis...${NC}"
    if command -v redis-cli &> /dev/null; then
        if redis-cli ping > /dev/null 2>&1; then
            echo -e "${GREEN}✓ Redis is running${NC}"
            REDIS_AVAILABLE="true"
        else
            echo -e "${YELLOW}⚠ Redis installed but not running${NC}"
            echo "  To start Redis: redis-server"
            REDIS_AVAILABLE="false"
        fi
    else
        echo -e "${YELLOW}⚠ Redis not installed (optional for caching)${NC}"
        echo "  To install: sudo apt-get install redis-server"
        REDIS_AVAILABLE="false"
    fi

    # Create necessary directories
    echo -e "${YELLOW}Creating directories...${NC}"
    mkdir -p models cache logs static templates
    echo -e "${GREEN}✓ Directories created${NC}"

    # Create .env file if it doesn't exist
    if [ ! -f ".env" ]; then
        echo -e "${YELLOW}Creating configuration...${NC}"
        cat > .env << EOF
# AI Humanizer Configuration
USE_GPU=$USE_GPU
REDIS_AVAILABLE=$REDIS_AVAILABLE
HOST=0.0.0.0
PORT=3650
WORKERS=4
RELOAD=false
ENVIRONMENT=production
LOG_LEVEL=INFO
CACHE_ENABLED=true
CACHE_TTL=3600
MODEL_SIZE_FAST=small
MODEL_SIZE_BALANCED=medium
MODEL_SIZE_QUALITY=large
EOF
        echo -e "${GREEN}✓ Configuration saved to .env${NC}"
    fi

    # Test import
    echo -e "${YELLOW}Testing installation...${NC}"
    python -c "
try:
    import torch
    import transformers
    import fastapi
    import spacy
    print('✓ All modules imported successfully')
except ImportError as e:
    print(f'✗ Import error: {e}')
    exit(1)
"

    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}✓ Setup completed successfully!${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
}

# Run function
run() {
    echo -e "${BLUE}Starting AI Humanizer API...${NC}"
    
    # Activate virtual environment if it exists
    if [ -d "venv" ]; then
        source venv/bin/activate
    fi

    # Set environment variables if .env exists
    if [ -f ".env" ]; then
        export $(cat .env | grep -v '^#' | xargs)
    fi
    
    # Ensure dependencies are present (handles cases where setup was skipped previously)
    ensure_deps

    # Run the application
    python -m app.main
}

# Main logic
if [ "$1" == "setup" ]; then
    setup
elif [ "$1" == "run" ]; then
    run
else
    # Auto-detect: setup if needed, then run
    if check_setup; then
        echo -e "${YELLOW}First-time setup detected. Running setup...${NC}"
        setup
        echo ""
        echo -e "${YELLOW}Setup complete. Starting application...${NC}"
        echo ""
    fi
    run
fi

