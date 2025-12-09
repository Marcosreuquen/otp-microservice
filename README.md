# Enterprise OTP Microservice

A production-ready **One-Time Password (OTP) microservice** built with modern Python architecture. This service provides secure multi-factor authentication capabilities with support for TOTP/OTP generation, verification, and delivery across multiple channels (Email, SMS, WhatsApp).

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13+-4169E1?logo=postgresql&logoColor=white)](https://postgresql.org)
[![Redis](https://img.shields.io/badge/Redis-7+-DC382D?logo=redis&logoColor=white)](https://redis.io)
[![CI](https://github.com/marcosreuquen/otp-microservice/actions/workflows/ci.yml/badge.svg)](https://github.com/marcosreuquen/otp-microservice/actions/workflows/ci.yml)
![Coverage](https://img.shields.io/badge/coverage-66%25-yellow)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## 🚀 Key Features

### Multi-Channel Authentication
- **TOTP/OTP Generation & Verification** - RFC 6238 compliant time-based codes
- **Multi-Channel Delivery** - Email (Resend), SMS & WhatsApp (Twilio)
- **Application Management** - Multi-tenant architecture with app registration
- **JWT Authentication** - Secure session management with configurable expiration

### Production-Ready Architecture
- **Clean Architecture** - Separation of concerns with controllers, services, and repositories
- **Domain-Driven Design** - Custom exception handling with structured error responses
- **Async Operations** - Non-blocking I/O with Redis caching and connection pooling
- **Comprehensive Testing** - pytest with coverage reporting and CI/CD ready
- **Docker Support** - Multi-stage builds with Docker Compose orchestration

## 📋 API Overview

| Endpoint | Purpose | Features |
|----------|---------|----------|
| `/api/code` | TOTP code operations | Generate, verify time-based codes |
| `/api/otp` | OTP flow management | Registration, QR generation, verification |
| `/api/auth` | User authentication | Login, logout, JWT token management |
| `/api/app` | Application management | Multi-tenant app registration |
| `/health` | Service monitoring | Health checks and system status |

## 🏗️ Technical Architecture

### Technology Stack
- **Framework**: FastAPI 0.115+ (async/await, automatic API docs)
- **Database**: PostgreSQL with SQLModel ORM (type-safe SQL operations)
- **Cache**: Redis 7+ (rate limiting, session storage, OTP caching)
- **Authentication**: JWT tokens with PyJWT and python-jose
- **OTP Generation**: pyotp library (RFC 6238/4226 compliant)
- **External Services**: Resend (email), Twilio (SMS/WhatsApp)

### Project Structure
```
app/
├── controllers/     # Business logic layer
├── lib/            # External service integrations
├── models/         # SQLModel database schemas
├── routes/         # FastAPI route handlers
├── schemas/        # Pydantic request/response models
├── utils/          # Utilities, middleware, error handling
└── main.py         # Application entry point
```

### Design Patterns & Best Practices
- **Dependency Injection** - FastAPI's built-in DI container for database sessions, Redis connections
- **Repository Pattern** - Data access abstraction with SQLModel
- **Factory Pattern** - Service instantiation and configuration management
- **Error Boundary Pattern** - Global exception handling with structured responses
- **Circuit Breaker** - Resilient Redis operations with fallback mechanisms

## 🛠️ Development Setup

### Prerequisites
- Python 3.10+
- PostgreSQL 13+
- Redis 7+
- Docker & Docker Compose (recommended)

### Quick Start with Docker
```bash
git clone https://github.com/marcosreuquen/otp-microservice.git
cd otp-microservice
cp .env.example .env  # Configure your environment variables
docker-compose up -d
```

### Local Development Setup
```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install git hooks (updates coverage badge automatically)
bash scripts/install-hooks.sh

# Set up environment
cp .env.example .env
# Edit .env with your configuration

# Run database migrations (if applicable)
# Start the application
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Environment Configuration
```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/otpdb
POSTGRES_USER=otpuser
POSTGRES_PASSWORD=secure_password
POSTGRES_DB=otpdb
POSTGRES_HOST=localhost

# Authentication
SECRET_KEY=your-super-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# External Services
RESEND_API_KEY=your_resend_api_key
EMAIL_ADDRESS=noreply@yourdomain.com
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
TWILIO_PHONE_NUMBER=+1234567890
TWILIO_WHATSAPP_NUMBER=whatsapp:+1234567890

# Cache
REDIS_URL=redis://localhost:6379
```

## 🧪 Testing & Quality Assurance

### Running Tests
```bash
# Run all tests with coverage
pytest

# Run with verbose output
pytest -v

# View coverage report
open reports/coverage_html/index.html

# Run tests quietly without coverage analysis
pytest --no-cov

# Run specific tests
pytest tests/lib/test_redis_service.py -v
```

### Test Artifacts
The project generates comprehensive test reports:
- `reports/junit.xml` - JUnit XML format for CI/CD integration
- `reports/coverage.xml` - Coverage data in XML format
- `reports/coverage_html/` - Interactive HTML coverage report
- `reports/coverage.json` - Coverage data in JSON format (for badge updates)

### Git Hooks & Automation
The project includes pre-commit hooks that automatically update the coverage badge:

```bash
# Install git hooks
bash scripts/install-hooks.sh

# Manually update coverage badge
bash scripts/update-coverage-badge.sh

# Skip hooks for a specific commit
git commit --no-verify
```

The pre-commit hook automatically:
- Runs tests when Python files are modified
- Updates the coverage badge in README.md
- Stages the updated README.md for commit

### Code Quality
- **Type Safety**: Full type hints with mypy compatibility
- **Code Formatting**: Black and isort for consistent style
- **Linting**: Flake8 for code quality checks
- **Security**: Bandit for security vulnerability scanning

## 🔒 Security Features

### Authentication & Authorization
- **JWT Token Management** - Secure session handling with configurable expiration
- **Password Hashing** - bcrypt with salt for secure password storage
- **Rate Limiting** - Redis-backed request throttling
- **CORS Configuration** - Configurable cross-origin resource sharing

### OTP Security
- **Time-Based Codes** - RFC 6238 compliant TOTP implementation
- **Secure Random Generation** - Cryptographically secure secret generation
- **Code Expiration** - Configurable time windows for code validity
- **Replay Attack Prevention** - Single-use code enforcement

## 📊 Monitoring & Observability

### Health Checks
- **Service Health** - `/health` endpoint for load balancer integration
- **Database Connectivity** - PostgreSQL connection monitoring
- **Cache Availability** - Redis health checks with graceful degradation

### Logging
- **Structured Logging** - JSON formatted logs for easy parsing
- **Log Levels** - Configurable logging levels (DEBUG, INFO, WARN, ERROR)
- **Request Tracing** - Correlation IDs for request tracking

## 🚀 Deployment

### Docker Production
```bash
# Build production image
docker build -t otp-microservice:latest .

# Run with production settings
docker run -d \
  --name otp-service \
  -p 8000:8000 \
  --env-file .env.production \
  otp-microservice:latest
```

### Kubernetes Deployment
```yaml
# Example Kubernetes deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: otp-microservice
spec:
  replicas: 3
  selector:
    matchLabels:
      app: otp-microservice
  template:
    metadata:
      labels:
        app: otp-microservice
    spec:
      containers:
      - name: otp-service
        image: otp-microservice:latest
        ports:
        - containerPort: 8000
        envFrom:
        - configMapRef:
            name: otp-config
```

## 📈 Performance Considerations

### Scalability Features
- **Async Operations** - Non-blocking I/O for high concurrency
- **Connection Pooling** - Efficient database connection management
- **Redis Caching** - Fast data retrieval and session storage
- **Stateless Design** - Horizontal scaling capability

### Performance Metrics
- **Response Time** - Sub-100ms for most operations
- **Throughput** - 1000+ requests/second (hardware dependent)
- **Memory Usage** - ~50MB base footprint
- **Database Efficiency** - Optimized queries with SQLModel

## 🏢 Enterprise Features

### Multi-Tenancy
- **Application Isolation** - Secure tenant separation
- **Resource Quotas** - Configurable limits per application
- **Usage Analytics** - Detailed metrics and reporting

### Integration Capabilities
- **RESTful API** - Standard HTTP/JSON interface
- **OpenAPI Documentation** - Auto-generated API docs
- **Webhook Support** - Event-driven notifications
- **SDK Ready** - Easy client library development

## 🤝 Contributing

This project follows industry best practices for open-source contributions:

### Development Workflow
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Make your changes with proper tests
4. Run the test suite (`pytest`)
5. Commit with conventional commit messages
6. Push to your branch (`git push origin feature/your-feature`)
7. Open a Pull Request

### Code Standards
- Follow PEP 8 style guidelines
- Add type hints to all functions
- Write comprehensive tests for new features
- Update documentation for API changes

## 👨‍💻 About the Developer

This microservice was architected and developed by **Marcos Díaz**, a Software Developer specializing in backend systems, microservices architecture, and scalable web applications.

### Connect
- **Website**: [marcosdiaz.dev](https://marcosdiaz.dev)
- **GitHub**: [@marcosreuquen](https://github.com/marcosreuquen)
- **LinkedIn**: [Marcos Díaz](https://linkedin.com/in/marcos-reuquen-diaz)
