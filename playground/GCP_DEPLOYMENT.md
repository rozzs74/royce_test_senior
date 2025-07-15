# Google Cloud Run Deployment Guide

This guide provides step-by-step instructions for deploying the Bowling Shoes Rental Service FastAPI application to Google Cloud Run.

## Overview

Google Cloud Run is a fully managed serverless platform that automatically scales your containerized applications. It's perfect for FastAPI applications because:

- **Serverless**: No infrastructure management
- **Auto-scaling**: Scales to zero when not in use
- **Pay-per-use**: Only pay for actual usage
- **Container-based**: Uses our existing Docker setup
- **Global**: Deploy to multiple regions easily

## Prerequisites

### 1. Google Cloud Setup

1. **Google Cloud Account**: Create a Google Cloud account at [cloud.google.com](https://cloud.google.com)
2. **Google Cloud Project**: Create a new project or use an existing one
3. **Billing**: Enable billing for your project
4. **APIs**: Enable required APIs (done automatically during deployment)

### 2. Local Development Tools

Install the following tools on your local machine:

```bash
# Install Google Cloud CLI
# macOS
brew install --cask google-cloud-sdk

# Ubuntu/Debian
sudo apt-get install google-cloud-cli

# Windows
# Download from https://cloud.google.com/sdk/docs/install

# Verify installation
gcloud --version
```

### 3. Authentication

```bash
# Login to Google Cloud
gcloud auth login

# Set your project ID
gcloud config set project YOUR_PROJECT_ID

# Configure Docker to use gcloud as a credential helper
gcloud auth configure-docker
```

## Deployment Architecture

```
Internet → Cloud Load Balancer → Cloud Run Service → Supabase Database
                                      ↓
                                 OpenAI API
```

### Components:
- **Cloud Run**: Hosts the FastAPI application
- **Container Registry**: Stores Docker images
- **Cloud Load Balancer**: Handles HTTPS and routing
- **Supabase**: External PostgreSQL database
- **OpenAI API**: External LLM service

## Step-by-Step Deployment

### Step 1: Prepare the Application

1. **Update Dockerfile for Cloud Run**:

```dockerfile
# Add to Dockerfile after the existing content
# Cloud Run specific optimizations
ENV PORT=8080
EXPOSE 8080

# Update CMD to use PORT environment variable
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

2. **Create `.gcloudignore` file**:

```bash
# Create .gcloudignore
cat > .gcloudignore << 'EOF'
.git
.gitignore
README.md
*.md
.DS_Store
.env
.env.*
!.env.example
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.venv/
pip-log.txt
pip-delete-this-directory.txt
.tox
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.log
.mypy_cache
.pytest_cache
.hypothesis
test_*.py
tests/
EOF
```

### Step 2: Configure Environment Variables

1. **Create `app.yaml` for environment configuration**:

```yaml
# app.yaml - Cloud Run service configuration
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: bowling-shoes-rental
  annotations:
    run.googleapis.com/ingress: all
spec:
  template:
    metadata:
      annotations:
        run.googleapis.com/execution-environment: gen2
        run.googleapis.com/cpu-throttling: "false"
    spec:
      containerConcurrency: 100
      timeoutSeconds: 300
      containers:
      - image: gcr.io/PROJECT_ID/bowling-shoes-rental
        ports:
        - containerPort: 8080
        env:
        - name: SUPABASE_URL
          value: "your_supabase_url"
        - name: SUPABASE_KEY
          value: "your_supabase_key"
        - name: OPENAI_API_KEY
          value: "your_openai_api_key"
        - name: DATABASE_URL
          value: "your_database_url"
        resources:
          limits:
            cpu: "1000m"
            memory: "512Mi"
```

2. **Create deployment script**:

```bash
#!/bin/bash
# deploy.sh - Deployment script

set -e

# Configuration
PROJECT_ID="your-project-id"
SERVICE_NAME="bowling-shoes-rental"
REGION="us-central1"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

echo "🚀 Deploying Bowling Shoes Rental Service to Cloud Run"
echo "================================================="

# Set project
gcloud config set project $PROJECT_ID

# Build and push Docker image
echo "📦 Building Docker image..."
docker build -t $IMAGE_NAME .

echo "📤 Pushing image to Container Registry..."
docker push $IMAGE_NAME

# Deploy to Cloud Run
echo "🌐 Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
  --image $IMAGE_NAME \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --set-env-vars="SUPABASE_URL=${SUPABASE_URL},SUPABASE_KEY=${SUPABASE_KEY},OPENAI_API_KEY=${OPENAI_API_KEY},DATABASE_URL=${DATABASE_URL}" \
  --memory=512Mi \
  --cpu=1 \
  --concurrency=100 \
  --timeout=300 \
  --max-instances=10 \
  --min-instances=0

echo "✅ Deployment complete!"
echo "🌐 Service URL: https://${SERVICE_NAME}-${REGION}-${PROJECT_ID}.a.run.app"
```

### Step 3: Deploy Using Cloud Build (Recommended)

1. **Create `cloudbuild.yaml`**:

```yaml
# cloudbuild.yaml - Automated build and deployment
steps:
  # Build the Docker image
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/bowling-shoes-rental', '.']
  
  # Push to Container Registry
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/bowling-shoes-rental']
  
  # Deploy to Cloud Run
  - name: 'gcr.io/cloud-builders/gcloud'
    args:
    - 'run'
    - 'deploy'
    - 'bowling-shoes-rental'
    - '--image'
    - 'gcr.io/$PROJECT_ID/bowling-shoes-rental'
    - '--region'
    - 'us-central1'
    - '--platform'
    - 'managed'
    - '--allow-unauthenticated'
    - '--memory'
    - '512Mi'
    - '--cpu'
    - '1'
    - '--concurrency'
    - '100'
    - '--timeout'
    - '300'
    - '--max-instances'
    - '10'
    - '--min-instances'
    - '0'

images:
  - 'gcr.io/$PROJECT_ID/bowling-shoes-rental'

options:
  logging: CLOUD_LOGGING_ONLY
```

2. **Deploy using Cloud Build**:

```bash
# Submit build to Cloud Build
gcloud builds submit --config cloudbuild.yaml .
```

### Step 4: Set Up Environment Variables Securely

1. **Create Secret Manager secrets**:

```bash
# Create secrets in Secret Manager
echo -n "your_supabase_url" | gcloud secrets create supabase-url --data-file=-
echo -n "your_supabase_key" | gcloud secrets create supabase-key --data-file=-
echo -n "your_openai_api_key" | gcloud secrets create openai-api-key --data-file=-
echo -n "your_database_url" | gcloud secrets create database-url --data-file=-
```

2. **Update Cloud Run service to use secrets**:

```bash
# Deploy with secrets
gcloud run deploy bowling-shoes-rental \
  --image gcr.io/$PROJECT_ID/bowling-shoes-rental \
  --region us-central1 \
  --set-secrets="SUPABASE_URL=supabase-url:latest,SUPABASE_KEY=supabase-key:latest,OPENAI_API_KEY=openai-api-key:latest,DATABASE_URL=database-url:latest" \
  --allow-unauthenticated
```

## Production Configuration

### 1. Update Dockerfile for Production

```dockerfile
# Dockerfile.prod - Production optimized
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        libpq-dev \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Create non-root user
RUN adduser --disabled-password --gecos '' appuser
RUN chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Run the application
CMD exec uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 1
```

### 2. Environment-Specific Configuration

Create different configurations for different environments:

```python
# app/config.py - Environment configuration
import os
from typing import Optional

class Settings:
    def __init__(self):
        self.environment = os.getenv("ENVIRONMENT", "development")
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.database_url = os.getenv("DATABASE_URL")
        self.port = int(os.getenv("PORT", "8080"))
        self.debug = os.getenv("DEBUG", "false").lower() == "true"
        
        # Production settings
        if self.environment == "production":
            self.debug = False
            self.log_level = "INFO"
        else:
            self.log_level = "DEBUG"

settings = Settings()
```

### 3. Monitoring and Logging

1. **Add structured logging**:

```python
# app/logging_config.py
import logging
import sys
from pythonjsonlogger import jsonlogger

def setup_logging():
    """Setup structured logging for Cloud Run"""
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # Create console handler
    handler = logging.StreamHandler(sys.stdout)
    
    # Create JSON formatter
    formatter = jsonlogger.JsonFormatter(
        '%(asctime)s %(name)s %(levelname)s %(message)s'
    )
    handler.setFormatter(formatter)
    
    logger.addHandler(handler)
    return logger
```

2. **Add to requirements.txt**:

```txt
python-json-logger==2.0.7
```

## Monitoring and Observability

### 1. Health Checks

The application already includes health checks at `/health`. Cloud Run will use this for:
- Startup probes
- Liveness probes
- Readiness probes

### 2. Cloud Monitoring

```python
# app/monitoring.py
from google.cloud import monitoring_v3
import time

def record_metric(metric_name: str, value: float, labels: dict = None):
    """Record custom metrics to Cloud Monitoring"""
    client = monitoring_v3.MetricServiceClient()
    project_name = f"projects/{PROJECT_ID}"
    
    series = monitoring_v3.TimeSeries()
    series.metric.type = f"custom.googleapis.com/{metric_name}"
    series.resource.type = "cloud_run_revision"
    
    if labels:
        for key, value in labels.items():
            series.metric.labels[key] = value
    
    now = time.time()
    seconds = int(now)
    nanos = int((now - seconds) * 10 ** 9)
    interval = monitoring_v3.TimeInterval(
        {"end_time": {"seconds": seconds, "nanos": nanos}}
    )
    
    point = monitoring_v3.Point(
        {"interval": interval, "value": {"double_value": value}}
    )
    series.points = [point]
    
    client.create_time_series(name=project_name, time_series=[series])
```

### 3. Error Reporting

```python
# app/error_reporting.py
from google.cloud import error_reporting
import logging

def setup_error_reporting():
    """Setup Cloud Error Reporting"""
    client = error_reporting.Client()
    
    def report_exception(exception):
        client.report_exception()
    
    return report_exception
```

## Security Best Practices

### 1. Service Account

Create a dedicated service account:

```bash
# Create service account
gcloud iam service-accounts create bowling-shoes-rental-sa \
    --description="Service account for Bowling Shoes Rental API" \
    --display-name="Bowling Shoes Rental Service Account"

# Grant necessary permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:bowling-shoes-rental-sa@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"

# Use service account in Cloud Run
gcloud run services update bowling-shoes-rental \
    --service-account=bowling-shoes-rental-sa@$PROJECT_ID.iam.gserviceaccount.com \
    --region=us-central1
```

### 2. VPC Connector (Optional)

For additional security, connect to a VPC:

```bash
# Create VPC connector
gcloud compute networks vpc-access connectors create bowling-shoes-connector \
    --region=us-central1 \
    --subnet=default \
    --subnet-project=$PROJECT_ID \
    --min-instances=2 \
    --max-instances=10

# Deploy with VPC connector
gcloud run deploy bowling-shoes-rental \
    --vpc-connector=bowling-shoes-connector \
    --vpc-egress=all-traffic \
    --region=us-central1
```

### 3. Authentication (Optional)

Enable authentication if needed:

```bash
# Deploy with authentication required
gcloud run deploy bowling-shoes-rental \
    --no-allow-unauthenticated \
    --region=us-central1
```

## Cost Optimization

### 1. Resource Limits

```yaml
# Optimize resources based on usage
resources:
  limits:
    cpu: "1000m"      # 1 vCPU
    memory: "512Mi"   # 512 MB RAM
```

### 2. Scaling Configuration

```bash
# Configure auto-scaling
gcloud run services update bowling-shoes-rental \
    --min-instances=0 \
    --max-instances=10 \
    --concurrency=100 \
    --cpu-throttling \
    --region=us-central1
```

### 3. Request Timeout

```bash
# Set appropriate timeout
gcloud run services update bowling-shoes-rental \
    --timeout=300 \
    --region=us-central1
```

## Continuous Deployment

### 1. GitHub Actions

```yaml
# .github/workflows/deploy.yml
name: Deploy to Cloud Run

on:
  push:
    branches: [ main ]

env:
  PROJECT_ID: ${{ secrets.GCP_PROJECT_ID }}
  SERVICE_NAME: bowling-shoes-rental
  REGION: us-central1

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Setup Google Cloud CLI
      uses: google-github-actions/setup-gcloud@v1
      with:
        service_account_key: ${{ secrets.GCP_SA_KEY }}
        project_id: ${{ secrets.GCP_PROJECT_ID }}
    
    - name: Configure Docker
      run: gcloud auth configure-docker
    
    - name: Build and Push Docker image
      run: |
        docker build -t gcr.io/$PROJECT_ID/$SERVICE_NAME .
        docker push gcr.io/$PROJECT_ID/$SERVICE_NAME
    
    - name: Deploy to Cloud Run
      run: |
        gcloud run deploy $SERVICE_NAME \
          --image gcr.io/$PROJECT_ID/$SERVICE_NAME \
          --region $REGION \
          --platform managed \
          --allow-unauthenticated \
          --set-secrets="SUPABASE_URL=supabase-url:latest,SUPABASE_KEY=supabase-key:latest,OPENAI_API_KEY=openai-api-key:latest,DATABASE_URL=database-url:latest"
```

### 2. Cloud Build Triggers

```bash
# Create Cloud Build trigger
gcloud builds triggers create github \
    --repo-name=your-repo \
    --repo-owner=your-username \
    --branch-pattern="^main$" \
    --build-config=cloudbuild.yaml
```

## Testing the Deployment

### 1. Smoke Tests

```bash
# Test health endpoint
curl https://your-service-url/health

# Test API endpoints
curl -X POST https://your-service-url/customers \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Customer",
    "age": 25,
    "contact_info": "test@example.com",
    "is_disabled": false
  }'
```

### 2. Load Testing

```bash
# Install hey for load testing
go install github.com/rakyll/hey@latest

# Run load test
hey -n 1000 -c 10 https://your-service-url/health
```

## Troubleshooting

### Common Issues

1. **Cold Start Issues**:
   - Use minimum instances: `--min-instances=1`
   - Optimize Docker image size
   - Use Cloud Run gen2 execution environment

2. **Memory Issues**:
   - Increase memory: `--memory=1Gi`
   - Monitor memory usage in Cloud Console

3. **Timeout Issues**:
   - Increase timeout: `--timeout=900`
   - Optimize database queries

4. **Environment Variables**:
   - Use Secret Manager for sensitive data
   - Verify secrets are properly mounted

### Debugging

```bash
# View logs
gcloud logs read "resource.type=cloud_run_revision AND resource.labels.service_name=bowling-shoes-rental" --limit=50

# Stream logs
gcloud logs tail "resource.type=cloud_run_revision AND resource.labels.service_name=bowling-shoes-rental"

# Check service status
gcloud run services describe bowling-shoes-rental --region=us-central1
```

## Cleanup

```bash
# Delete Cloud Run service
gcloud run services delete bowling-shoes-rental --region=us-central1

# Delete Docker images
gcloud container images delete gcr.io/$PROJECT_ID/bowling-shoes-rental

# Delete secrets
gcloud secrets delete supabase-url
gcloud secrets delete supabase-key
gcloud secrets delete openai-api-key
gcloud secrets delete database-url
```

## Conclusion

This deployment guide provides a comprehensive approach to deploying your FastAPI application to Google Cloud Run. The setup includes:

- ✅ Containerized deployment with Docker
- ✅ Secure environment variable management
- ✅ Auto-scaling and cost optimization
- ✅ Monitoring and logging
- ✅ CI/CD pipeline setup
- ✅ Security best practices

Your application will be highly available, scalable, and cost-effective on Google Cloud Run. 