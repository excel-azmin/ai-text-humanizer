# AI Text Humanizer - Fast Open Source Solution

A powerful, fast, and open-source tool for transforming AI-generated content into natural, human-like text that bypasses AI detection systems.


## 🚀 Features

- **Multiple Processing Modes**: Fast (real-time), Balanced, and Quality modes
- **Advanced Techniques**: 
  - Sentence structure variation
  - Perplexity modulation
  - Semantic paraphrasing
  - Human pattern injection
  - Stylistic elements
- **High Performance**: GPU acceleration support, Redis caching, batch processing
- **REST API**: Full-featured API with FastAPI
- **WebSocket Support**: Real-time humanization
- **Web Interface**: Beautiful, responsive UI
- **Docker Support**: Easy deployment with Docker Compose
- **Production Ready**: Industry-standard folder structure and best practices

## 📁 Project Structure

```
ai-text-humanizer/
├── app/                          # Main application package
│   ├── __init__.py              # Package initialization
│   ├── main.py                  # FastAPI application entry point
│   │
│   ├── api/                     # API routes
│   │   ├── __init__.py
│   │   └── v1/                  # API version 1
│   │       ├── __init__.py
│   │       ├── router.py       # Main v1 router
│   │       ├── health.py        # Health check endpoints
│   │       ├── humanize.py      # Humanization endpoints
│   │       ├── analyze.py       # Text analysis endpoints
│   │       └── techniques.py    # Techniques listing
│   │
│   ├── core/                    # Core configuration
│   │   ├── __init__.py
│   │   ├── config.py            # Settings and configuration
│   │   ├── logging.py           # Logging setup
│   │   └── dependencies.py     # Dependency injection
│   │
│   ├── models/                  # Pydantic models
│   │   ├── __init__.py
│   │   └── schemas.py           # Request/Response schemas
│   │
│   ├── services/                # Business logic services
│   │   ├── __init__.py
│   │   ├── engine.py           # Humanizer engine
│   │   ├── humanizer_service.py # Humanizer service wrapper
│   │   └── cache_service.py    # Redis cache service
│   │
│   └── utils/                   # Utility functions
│       └── __init__.py
│
├── templates/                   # HTML templates (UI served by FastAPI)
│   ├── web_interface.html      # Home UI (editor)
│   ├── pricing.html            # Pricing page
│   ├── features.html           # Features page
│   ├── faq.html                # FAQ page
│   ├── blog.html               # Blog landing page
│   ├── about.html              # About Us page
│   ├── privacy.html            # Privacy Policy
│   ├── _shared_head.html       # Optional shared header (standalone variant)
│   └── _shared_footer.html     # Optional shared footer (standalone variant)
│
├── static/                      # Static files (CSS, JS, images)
├── tests/                       # Test files
├── scripts/                     # Utility scripts
├── logs/                        # Application logs
├── cache/                       # Cache directory
├── models/                      # ML model cache
│
├── .env.example                 # Environment variables template
├── .gitignore                   # Git ignore rules
├── requirements.txt             # Python dependencies
├── Dockerfile                   # Docker image definition
├── docker-compose.yml           # Docker Compose configuration
└── start.sh                    # Combined setup + run helper script
```

### Key Components

- **`app/main.py`**: FastAPI application initialization, middleware setup, and route registration
- **`app/api/v1/`**: Versioned API endpoints (health, humanize, analyze, techniques, WebSocket)
- **`app/core/config.py`**: Environment-based settings using Pydantic Settings
- **`app/core/logging.py`**: Structured logging configuration
- **`app/services/engine.py`**: Core humanization engine
- **`app/models/schemas.py`**: Pydantic models for request/response validation

## 🛠️ Installation

### Quick Start (Automated)

```bash
# Clone the repository
git clone https://github.com/yourusername/ai-humanizer.git
cd ai-humanizer

# Run setup and start (auto-detects if setup is needed)
./start.sh
```

The script will:
- Check Python version
- Detect GPU availability
- Create virtual environment
- Install all dependencies
- Download language models
- Create configuration files
- Start the application

### Manual Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Download language models
python -m spacy download en_core_web_sm
python -c "import nltk; nltk.download('punkt'); nltk.download('wordnet'); nltk.download('omw-1.4')"

# Copy environment template
cp .env.example .env
# Edit .env with your settings

# Run the application
python -m app.main
```

### Docker Installation (Recommended for Production)

```bash
# Build and run with Docker Compose
docker-compose up -d

# Check logs
docker-compose logs -f humanizer
```

Access the application at `http://localhost:3650`

Site pages (same-origin)
- Home: `/`
- Features: `/features`
- Pricing: `/pricing`
- About Us: `/about`
- FAQ: `/faq`
- Blog: `/blog`
- Privacy: `/privacy`

## 📖 Usage

### Command Line

```bash
# Setup only
./start.sh setup

# Run only (assumes setup is complete)
./start.sh run

# Setup and run (auto-detects)
./start.sh
```

### Python API

```python
from app.services.engine import HumanizerEngine

# Initialize
humanizer = HumanizerEngine(
    use_gpu=True,
    model_size="medium",
    techniques=["sentence_variation", "human_patterns"]
)

# Humanize text
text = "Your AI-generated text here..."
humanized = humanizer.humanize(
    text, 
    intensity=0.7,
    preserve_meaning=True
)
print(humanized)
```

### REST API

All endpoints are prefixed with `/api/v1/`:

```bash
# Basic humanization
curl -X POST "http://localhost:3650/api/v1/humanize" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Your AI text here",
    "mode": "balanced",
    "intensity": 0.7
  }'

# Batch processing
curl -X POST "http://localhost:3650/api/v1/humanize/batch" \
  -H "Content-Type: application/json" \
  -d '{
    "texts": ["Text 1", "Text 2", "Text 3"],
    "mode": "fast"
  }'

# Analyze text for AI patterns
curl -X POST "http://localhost:3650/api/v1/analyze" \
  -H "Content-Type: application/json" \
  -d '{"text": "Your text here"}'

# Health check
curl "http://localhost:3650/api/v1/health"
```

### WebSocket (Real-time)

```javascript
const ws = new WebSocket('ws://localhost:3650/api/v1/humanize/ws');

ws.onopen = () => {
    ws.send(JSON.stringify({
        text: "Your text here",
        intensity: 0.7
    }));
};

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('Humanized:', data.humanized);
};
```

## 🎯 Processing Modes

### Fast Mode ⚡
- **Speed**: < 0.5 seconds
- **Techniques**: Pattern-based modifications
- **Use Case**: Real-time applications, live typing
- **Models**: Lightweight, CPU-friendly

### Balanced Mode ⚖️
- **Speed**: 1-3 seconds
- **Techniques**: Pattern + semantic paraphrasing
- **Use Case**: General content, blog posts
- **Models**: Medium-sized, GPU recommended

### Quality Mode ✨
- **Speed**: 3-10 seconds
- **Techniques**: All available techniques
- **Use Case**: Important documents, academic content
- **Models**: Large models, GPU required

## 🔧 Configuration

### Environment Variables

Create a `.env` file (see `.env.example` for template):

```bash
# Application Settings
APP_NAME=AI Text Humanizer API
APP_VERSION=1.0.0
DEBUG=false
ENVIRONMENT=production

# Server Configuration
HOST=0.0.0.0
PORT=3650
WORKERS=4
RELOAD=false

# CORS Configuration
CORS_ORIGINS=["*"]
CORS_ALLOW_CREDENTIALS=true

# Redis Cache Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
CACHE_TTL=3600
CACHE_ENABLED=true

# Model Configuration
USE_GPU=true
MODEL_SIZE_FAST=small
MODEL_SIZE_BALANCED=medium
MODEL_SIZE_QUALITY=large

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
```

### Customization

```python
# Custom techniques
techniques = [
    "sentence_variation",      # Vary sentence structure
    "perplexity_modulation",   # Add unpredictability
    "stylistic_injection",     # Add style elements
    "semantic_paraphrasing",   # Paraphrase content
    "human_patterns"           # Add human-like patterns
]

# Intensity levels
intensity_levels = {
    "light": 0.3,    # Minor modifications
    "medium": 0.5,   # Balanced changes
    "heavy": 0.7,    # Significant humanization
    "maximum": 0.9   # Maximum transformation
}
```

## 📊 Performance Benchmarks

| Mode | Text Length | Processing Time | GPU | Similarity |
|------|------------|----------------|-----|------------|
| Fast | 500 words | 0.3s | No | 95% |
| Fast | 2000 words | 0.8s | No | 94% |
| Balanced | 500 words | 1.5s | Yes | 92% |
| Balanced | 2000 words | 3.2s | Yes | 91% |
| Quality | 500 words | 4.5s | Yes | 88% |
| Quality | 2000 words | 9.8s | Yes | 87% |

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│             Web Interface               │
├─────────────────────────────────────────┤
│          FastAPI REST API               │
│         WebSocket Handler               │
├─────────────────────────────────────────┤
│         Humanizer Engine                │
│   ┌─────────────┬──────────────┐       │
│   │ Techniques  │   Models     │       │
│   ├─────────────┼──────────────┤       │
│   │ Patterns    │ T5 Paraphrase│       │
│   │ Variation   │ GPT-2 Style  │       │
│   │ Injection   │ Sentence BERT│       │
│   └─────────────┴──────────────┘       │
├─────────────────────────────────────────┤
│      Cache Layer (Redis)                │
└─────────────────────────────────────────┘
```

## 🔒 API Endpoints

All endpoints are under `/api/v1/`:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Web interface |
| `/api` | GET | API information |
| `/api/v1/health` | GET | Health check |
| `/api/v1/techniques` | GET | List available techniques |
| `/api/v1/humanize` | POST | Humanize single text |
| `/api/v1/humanize/batch` | POST | Batch processing |
| `/api/v1/analyze` | POST | Analyze AI patterns |
| `/api/v1/analyze/detect-and-humanize` | POST | Auto-detect and humanize |
| `/api/v1/humanize/ws` | WebSocket | Real-time humanization |

## 🚀 Deployment

### Production Setup

1. **SSL/TLS Configuration**
```nginx
server {
    listen 443 ssl http2;
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    
    location / {
        proxy_pass http://humanizer:3650;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

2. **Scaling**
```yaml
# docker-compose.override.yml
services:
  humanizer:
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '2'
          memory: 4G
```

3. **Monitoring**
```python
# Add Prometheus metrics
from prometheus_client import Counter, Histogram

request_count = Counter('humanizer_requests_total', 'Total requests')
request_duration = Histogram('humanizer_duration_seconds', 'Request duration')
```

## 🔄 Migration from Old Structure

If you're upgrading from the old structure:

### API Path Changes
- `POST /humanize` → `POST /api/v1/humanize`
- `GET /health` → `GET /api/v1/health`
- `POST /analyze` → `POST /api/v1/analyze`
- `WS /ws/humanize` → `WS /api/v1/humanize/ws`

### Import Path Changes
- `from humanizer_engine import ...` → `from app.services.engine import ...`
- `from api_service import ...` → `from app.main import ...`

### Benefits
1. **Maintainability**: Clear separation of concerns
2. **Scalability**: Easy to add new API versions
3. **Configuration**: Environment-based settings
4. **Logging**: Production-ready logging system
5. **Testing**: Organized structure for test files
6. **Documentation**: Better code organization

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run tests
pytest tests/

# Run linting
flake8 .
black .

# Run type checking
mypy .
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Hugging Face for transformer models
- SpaCy for NLP capabilities
- FastAPI for the web framework
- Open source community for various contributions

## ⚠️ Ethical Use

This tool is designed for legitimate purposes such as:
- Improving content readability
- Enhancing writing style
- Research and education
- Creative writing assistance

Please use responsibly and maintain transparency about AI assistance in your content where appropriate.

## 📧 Contact

- GitHub: [@yourusername](https://github.com/yourusername)
- Email: your.email@example.com

## 🐛 Known Issues

- GPU memory usage can be high with large models
- Some techniques may slightly alter meaning at high intensities
- WebSocket connections may timeout after extended idle periods

## 🗺️ Roadmap

- [ ] Support for more languages
- [ ] Integration with popular writing tools
- [ ] Advanced style transfer options
- [ ] Fine-tuning interface for custom domains
- [ ] Mobile application
- [ ] Browser extension

---

**Note**: This tool is for educational and legitimate use only. Always respect copyright and intellectual property rights.
