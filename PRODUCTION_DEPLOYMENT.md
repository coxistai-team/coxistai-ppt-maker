# AI Presentation Service - Production Deployment Guide

## Overview

This guide covers the production deployment of the AI Presentation Generator service with enterprise-level features, security, and scalability.

## 🚀 Quick Start

### 1. Environment Setup

```bash
# Clone the repository
git clone <your-repo>
cd coxistai-ppt-maker

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Variables

Create a `.env` file with the following variables:

```env
# API Configuration
OPENROUTER_API_KEY=your_openrouter_api_key_here
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Storage Configuration
RENDER_DISK_PATH=/opt/render/project/src/persistent_data

# S3/R2 Configuration (Optional)
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=us-east-1
S3_BUCKET_NAME=your-bucket-name

# Security
JWT_SECRET=your_jwt_secret_here
FLASK_SECRET_KEY=your_flask_secret_key

# Logging
LOG_LEVEL=INFO
LOG_FILE=ppt_service.log

# Rate Limiting
MAX_REQUESTS_PER_MINUTE=30
```

### 3. Production Dependencies

Update `requirements.txt` for production:

```txt
Flask==2.3.3
flask-cors==4.0.0
python-pptx==0.6.21
reportlab==4.0.4
boto3==1.28.44
requests==2.31.0
python-dotenv==1.0.0
gunicorn==21.2.0
prometheus-client==0.17.1
structlog==23.1.0
```

## 🔧 Production Configuration

### 1. Gunicorn Configuration

Create `gunicorn.conf.py`:

```python
import multiprocessing
import os

# Server socket
bind = "0.0.0.0:5002"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50

# Timeout
timeout = 30
keepalive = 2

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process naming
proc_name = "ai-presentation-service"

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# SSL (if using HTTPS)
# keyfile = "/path/to/keyfile"
# certfile = "/path/to/certfile"
```

### 2. Docker Configuration

Create `Dockerfile.prod`:

```dockerfile
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV FLASK_ENV=production

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Create persistent data directory
RUN mkdir -p /app/persistent_data

# Expose port
EXPOSE 5002

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5002/health || exit 1

# Run the application
CMD ["gunicorn", "--config", "gunicorn.conf.py", "ppt_flask:app"]
```

### 3. Docker Compose for Production

Create `docker-compose.prod.yml`:

```yaml
version: "3.8"

services:
  ai-presentation-service:
    build:
      context: .
      dockerfile: Dockerfile.prod
    ports:
      - "5002:5002"
    environment:
      - OPENROUTER_API_KEY=${OPENROUTER_API_KEY}
      - ALLOWED_ORIGINS=${ALLOWED_ORIGINS}
      - RENDER_DISK_PATH=/app/persistent_data
      - AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
      - AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
      - AWS_REGION=${AWS_REGION}
      - S3_BUCKET_NAME=${S3_BUCKET_NAME}
    volumes:
      - presentation_data:/app/persistent_data
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5002/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - ai-presentation-service
    restart: unless-stopped

volumes:
  presentation_data:
```

### 4. Nginx Configuration

Create `nginx.conf`:

```nginx
events {
    worker_connections 1024;
}

http {
    upstream ai_presentation_service {
        server ai-presentation-service:5002;
    }

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=30r/m;

    server {
        listen 80;
        server_name yourdomain.com;
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name yourdomain.com;

        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
        ssl_prefer_server_ciphers off;

        # Security headers
        add_header X-Frame-Options DENY;
        add_header X-Content-Type-Options nosniff;
        add_header X-XSS-Protection "1; mode=block";
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

        # Rate limiting
        limit_req zone=api burst=10 nodelay;

        location / {
            proxy_pass http://ai_presentation_service;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;

            # Timeouts
            proxy_connect_timeout 30s;
            proxy_send_timeout 30s;
            proxy_read_timeout 30s;

            # Buffer settings
            proxy_buffering on;
            proxy_buffer_size 4k;
            proxy_buffers 8 4k;
        }

        # Health check endpoint
        location /health {
            access_log off;
            proxy_pass http://ai_presentation_service;
        }
    }
}
```

## 🔒 Security Features

### 1. Input Validation

The service includes comprehensive input validation:

- Topic length limits (max 200 characters)
- Slide count validation (1-20 slides)
- File type validation for uploads
- SQL injection prevention
- XSS protection

### 2. Rate Limiting

- Client-based rate limiting (30 requests per minute)
- Burst handling with nginx
- Configurable limits via environment variables

### 3. CORS Configuration

```python
CORS(app, resources={
    r"/*": {
        "origins": os.getenv("ALLOWED_ORIGINS", "*").split(","),
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True,
        "max_age": 86400
    }
})
```

## 📊 Monitoring and Logging

### 1. Structured Logging

```python
import structlog

structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)
```

### 2. Health Check Endpoint

```python
@app.route('/health')
def health_check():
    """Enhanced health check with detailed status"""
    try:
        # Check S3 connectivity
        s3_available = s3_service.is_available()

        # Check disk space
        import shutil
        disk_usage = shutil.disk_usage(PERSISTENT_STORAGE_PATH)
        disk_free_gb = disk_usage.free / (1024**3)

        # Check memory usage
        import psutil
        memory_percent = psutil.virtual_memory().percent

        return jsonify({
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "s3_available": s3_available,
            "openrouter_configured": bool(OPENROUTER_API_KEY),
            "disk_free_gb": round(disk_free_gb, 2),
            "memory_percent": round(memory_percent, 2),
            "presentations_in_memory": len(presentations_db)
        })
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "error": str(e)
        }), 500
```

### 3. Metrics Collection

```python
from prometheus_client import Counter, Histogram, generate_latest

# Metrics
presentation_requests = Counter('presentation_requests_total', 'Total presentation requests', ['status'])
presentation_duration = Histogram('presentation_duration_seconds', 'Time spent creating presentations')
slide_operations = Counter('slide_operations_total', 'Total slide operations', ['operation'])

@app.route('/metrics')
def metrics():
    """Prometheus metrics endpoint"""
    return generate_latest()
```

## 🚀 Deployment Commands

### 1. Local Production Setup

```bash
# Install production dependencies
pip install -r requirements.txt

# Set environment variables
export FLASK_ENV=production
export OPENROUTER_API_KEY=your_key_here

# Run with Gunicorn
gunicorn --config gunicorn.conf.py ppt_flask:app
```

### 2. Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose -f docker-compose.prod.yml up -d

# Check logs
docker-compose -f docker-compose.prod.yml logs -f

# Scale the service
docker-compose -f docker-compose.prod.yml up -d --scale ai-presentation-service=3
```

### 3. Kubernetes Deployment

Create `k8s-deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ai-presentation-service
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ai-presentation-service
  template:
    metadata:
      labels:
        app: ai-presentation-service
    spec:
      containers:
        - name: ai-presentation-service
          image: your-registry/ai-presentation-service:latest
          ports:
            - containerPort: 5002
          env:
            - name: OPENROUTER_API_KEY
              valueFrom:
                secretKeyRef:
                  name: ai-presentation-secrets
                  key: openrouter-api-key
          resources:
            requests:
              memory: "256Mi"
              cpu: "250m"
            limits:
              memory: "512Mi"
              cpu: "500m"
          livenessProbe:
            httpGet:
              path: /health
              port: 5002
            initialDelaySeconds: 30
            periodSeconds: 10
          readinessProbe:
            httpGet:
              path: /health
              port: 5002
            initialDelaySeconds: 5
            periodSeconds: 5
```

## 🧪 Testing

### 1. Run the Test Suite

```bash
# Install test dependencies
pip install requests pytest

# Run tests
python test_features.py

# Or run with custom URL
PPT_SERVICE_URL=https://yourdomain.com python test_features.py
```

### 2. Load Testing

```bash
# Install locust
pip install locust

# Run load test
locust -f load_test.py --host=https://yourdomain.com
```

## 🔧 Troubleshooting

### Common Issues

1. **Service not starting**

   - Check environment variables
   - Verify API keys are set
   - Check port availability

2. **Rate limiting issues**

   - Adjust `MAX_REQUESTS_PER_MINUTE` in environment
   - Check nginx rate limiting configuration

3. **Memory issues**

   - Increase worker memory limits
   - Implement presentation cleanup
   - Monitor memory usage

4. **S3 connectivity**
   - Verify AWS credentials
   - Check bucket permissions
   - Test S3 connectivity separately

### Log Analysis

```bash
# View real-time logs
tail -f ppt_service.log

# Search for errors
grep "ERROR" ppt_service.log

# Monitor request patterns
grep "create_presentation" ppt_service.log | wc -l
```

## 📈 Performance Optimization

### 1. Caching

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_cached_presentation(presentation_id):
    # Cache frequently accessed presentations
    pass
```

### 2. Database Integration

For production, consider using a proper database:

```python
# PostgreSQL integration
import psycopg2
from psycopg2.extras import RealDictCursor

def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )
```

### 3. Async Processing

For heavy operations, consider async processing:

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

async def create_presentation_async(topic, slides):
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as executor:
        return await loop.run_in_executor(
            executor,
            create_presentation_sync,
            topic,
            slides
        )
```

## 🎯 Success Metrics

Monitor these key metrics:

- **Response Time**: < 5 seconds for presentation creation
- **Uptime**: > 99.9%
- **Error Rate**: < 1%
- **Throughput**: > 100 requests/minute
- **Memory Usage**: < 80% of allocated
- **Disk Usage**: < 90% of available space

## 📞 Support

For production support:

1. **Monitoring**: Set up alerts for health check failures
2. **Backup**: Regular backups of persistent data
3. **Updates**: Scheduled maintenance windows
4. **Documentation**: Keep deployment docs updated

---

**Version**: 1.0.0  
**Last Updated**: 2024  
**Maintainer**: Your Team
