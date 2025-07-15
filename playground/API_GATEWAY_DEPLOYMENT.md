# GCP API Gateway Deployment Guide

This guide provides step-by-step instructions for deploying the Bowling Shoes Rental Service OpenAPI specification to Google Cloud API Gateway.

## Overview

Google Cloud API Gateway provides a unified interface for managing APIs with features like:

- **API Management**: Centralized API configuration and versioning
- **Authentication**: API key and OAuth2 authentication
- **Rate Limiting**: Request quotas and throttling
- **Monitoring**: Request metrics and logging
- **Security**: CORS, validation, and access control
- **Documentation**: Auto-generated API documentation

## Architecture

```
Internet → API Gateway → Cloud Run Service → Supabase Database
             ↓                ↓
        Rate Limiting    OpenAI API
        Authentication
        Monitoring
```

## Prerequisites

1. **Google Cloud Project**: With billing enabled
2. **APIs Enabled**:
   - API Gateway API
   - Service Management API
   - Service Control API
   - Cloud Run API
3. **Cloud Run Service**: Already deployed (see GCP_DEPLOYMENT.md)
4. **Google Cloud CLI**: Installed and authenticated

## Step-by-Step Deployment

### Step 1: Enable Required APIs

```bash
# Enable required APIs
gcloud services enable apigateway.googleapis.com
gcloud services enable servicemanagement.googleapis.com
gcloud services enable servicecontrol.googleapis.com
```

### Step 2: Prepare OpenAPI Specification

1. **Update the OpenAPI spec** with your project details:

```bash
# Replace placeholders in openapi-spec.yaml
sed -i 's/{project-id}/YOUR_PROJECT_ID/g' openapi-spec.yaml
```

2. **Validate the OpenAPI specification**:

```bash
# Install swagger-codegen for validation (optional)
npm install -g swagger-codegen-cli

# Validate the spec
swagger-codegen-cli validate -i openapi-spec.yaml
```

### Step 3: Create API Configuration

```bash
# Create API configuration
gcloud api-gateway api-configs create bowling-shoes-config \
    --api=bowling-shoes-rental \
    --openapi-spec=openapi-spec.yaml \
    --project=YOUR_PROJECT_ID
```

### Step 4: Create API Gateway

```bash
# Create the API Gateway
gcloud api-gateway gateways create bowling-shoes-gateway \
    --api=bowling-shoes-rental \
    --api-config=bowling-shoes-config \
    --location=us-central1 \
    --project=YOUR_PROJECT_ID
```

### Step 5: Get Gateway URL

```bash
# Get the gateway URL
gcloud api-gateway gateways describe bowling-shoes-gateway \
    --location=us-central1 \
    --project=YOUR_PROJECT_ID
```

## Configuration Files

### 1. API Gateway Configuration Script

Create `deploy-gateway.sh`:

```bash
#!/bin/bash
# deploy-gateway.sh - API Gateway deployment script

set -e

# Configuration
PROJECT_ID="your-project-id"
API_NAME="bowling-shoes-rental"
CONFIG_NAME="bowling-shoes-config"
GATEWAY_NAME="bowling-shoes-gateway"
LOCATION="us-central1"

echo "🚀 Deploying API Gateway for Bowling Shoes Rental Service"
echo "========================================================="

# Set project
gcloud config set project $PROJECT_ID

# Enable required APIs
echo "📋 Enabling required APIs..."
gcloud services enable apigateway.googleapis.com
gcloud services enable servicemanagement.googleapis.com
gcloud services enable servicecontrol.googleapis.com

# Create or update API
echo "🔧 Creating API..."
gcloud api-gateway apis create $API_NAME \
    --project=$PROJECT_ID || echo "API already exists"

# Create API configuration
echo "📝 Creating API configuration..."
gcloud api-gateway api-configs create $CONFIG_NAME \
    --api=$API_NAME \
    --openapi-spec=openapi-spec.yaml \
    --project=$PROJECT_ID

# Create or update gateway
echo "🌐 Creating API Gateway..."
gcloud api-gateway gateways create $GATEWAY_NAME \
    --api=$API_NAME \
    --api-config=$CONFIG_NAME \
    --location=$LOCATION \
    --project=$PROJECT_ID || \
gcloud api-gateway gateways update $GATEWAY_NAME \
    --api=$API_NAME \
    --api-config=$CONFIG_NAME \
    --location=$LOCATION \
    --project=$PROJECT_ID

# Get gateway URL
echo "✅ Deployment complete!"
echo "🌐 Gateway URL:"
gcloud api-gateway gateways describe $GATEWAY_NAME \
    --location=$LOCATION \
    --project=$PROJECT_ID \
    --format="value(defaultHostname)"
```

### 2. Environment-Specific Configurations

Create different OpenAPI specs for different environments:

```yaml
# openapi-spec-dev.yaml
openapi: 3.0.3
info:
  title: Bowling Shoes Rental Service API (Development)
  version: 1.0.0-dev
servers:
  - url: https://bowling-shoes-rental-dev-gateway-{project-id}.a.run.app
    description: Development API Gateway
x-google-backend:
  address: https://bowling-shoes-rental-dev-us-central1-{project-id}.a.run.app
  protocol: h2
```

```yaml
# openapi-spec-prod.yaml
openapi: 3.0.3
info:
  title: Bowling Shoes Rental Service API (Production)
  version: 1.0.0
servers:
  - url: https://bowling-shoes-rental-gateway-{project-id}.a.run.app
    description: Production API Gateway
x-google-backend:
  address: https://bowling-shoes-rental-us-central1-{project-id}.a.run.app
  protocol: h2
```

## Authentication Setup

### 1. API Key Authentication

```bash
# Create API key
gcloud alpha services api-keys create \
    --display-name="Bowling Shoes Rental API Key" \
    --api-target=service=bowling-shoes-rental-gateway-{project-id}.a.run.app

# Get API key value
gcloud alpha services api-keys get-key-string API_KEY_ID
```

### 2. OAuth2 Authentication

```bash
# Create OAuth2 client
gcloud alpha iap oauth-clients create \
    --display-name="Bowling Shoes Rental OAuth Client"

# Configure OAuth consent screen
gcloud alpha iap oauth-consent-screen update \
    --application-title="Bowling Shoes Rental Service" \
    --support-email=dev@kodeacross.com
```

### 3. Service Account Authentication

```bash
# Create service account for API access
gcloud iam service-accounts create bowling-shoes-api-client \
    --description="Service account for API client access" \
    --display-name="Bowling Shoes API Client"

# Grant necessary permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:bowling-shoes-api-client@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/servicemanagement.serviceController"
```

## Rate Limiting and Quotas

### 1. Configure Rate Limits

Update the OpenAPI spec with rate limiting:

```yaml
x-google-quota:
  metricCosts:
    read-requests: 1
    write-requests: 2
    discount-calculations: 5
  limits:
    - name: "requests-per-minute"
      metric: "read-requests"
      unit: "1/min"
      values:
        STANDARD: 1000
    - name: "discount-calculations-per-minute"
      metric: "discount-calculations"
      unit: "1/min"
      values:
        STANDARD: 100
```

### 2. Create Custom Quotas

```bash
# Create quota configuration
cat > quota-config.yaml << 'EOF'
name: projects/YOUR_PROJECT_ID/services/bowling-shoes-rental-gateway-YOUR_PROJECT_ID.a.run.app/configs/quota
quotas:
  - name: "requests-per-minute"
    metric: "serviceruntime.googleapis.com/api/request_count"
    unit: "1/min"
    values:
      STANDARD: 1000
  - name: "discount-calculations-per-minute"
    metric: "bowling-shoes-rental/discount_calculations"
    unit: "1/min"
    values:
      STANDARD: 100
EOF

# Apply quota configuration
gcloud service-management configs submit quota-config.yaml \
    --service=bowling-shoes-rental-gateway-YOUR_PROJECT_ID.a.run.app
```

## Monitoring and Logging

### 1. Enable Monitoring

```bash
# Enable Cloud Monitoring
gcloud services enable monitoring.googleapis.com

# Create monitoring dashboard
cat > monitoring-dashboard.json << 'EOF'
{
  "displayName": "Bowling Shoes Rental API Gateway",
  "mosaicLayout": {
    "tiles": [
      {
        "width": 6,
        "height": 4,
        "widget": {
          "title": "Request Count",
          "xyChart": {
            "dataSets": [
              {
                "timeSeriesQuery": {
                  "timeSeriesFilter": {
                    "filter": "resource.type=\"api\" AND resource.labels.service=\"bowling-shoes-rental-gateway-YOUR_PROJECT_ID.a.run.app\"",
                    "aggregation": {
                      "alignmentPeriod": "60s",
                      "perSeriesAligner": "ALIGN_RATE"
                    }
                  }
                }
              }
            ]
          }
        }
      }
    ]
  }
}
EOF

# Create dashboard
gcloud monitoring dashboards create --config-from-file=monitoring-dashboard.json
```

### 2. Set Up Alerts

```bash
# Create alert policy
cat > alert-policy.yaml << 'EOF'
displayName: "High API Gateway Error Rate"
conditions:
  - displayName: "Error rate too high"
    conditionThreshold:
      filter: 'resource.type="api" AND resource.labels.service="bowling-shoes-rental-gateway-YOUR_PROJECT_ID.a.run.app"'
      comparison: COMPARISON_GREATER_THAN
      thresholdValue: 0.1
      duration: 300s
notificationChannels:
  - "projects/YOUR_PROJECT_ID/notificationChannels/NOTIFICATION_CHANNEL_ID"
EOF

# Create alert
gcloud alpha monitoring policies create --policy-from-file=alert-policy.yaml
```

## Security Configuration

### 1. CORS Configuration

Update OpenAPI spec with CORS settings:

```yaml
x-google-endpoints:
  - name: bowling-shoes-rental-gateway-{project-id}.a.run.app
    allowCors: true
    corsSettings:
      allowOrigins:
        - "https://your-frontend-domain.com"
        - "http://localhost:3000"
      allowMethods:
        - GET
        - POST
        - OPTIONS
      allowHeaders:
        - Content-Type
        - Authorization
        - X-API-Key
      maxAge: 86400
```

### 2. Request Validation

```yaml
# Add request validation
components:
  securitySchemes:
    api_key:
      type: apiKey
      in: header
      name: X-API-Key
      x-google-issuer: "https://your-project-id.apigateway.your-region.gateway.dev"
      x-google-jwks_uri: "https://your-project-id.apigateway.your-region.gateway.dev/.well-known/jwks"
```

## Testing the API Gateway

### 1. Test with curl

```bash
# Test health endpoint
curl -H "X-API-Key: YOUR_API_KEY" \
  https://bowling-shoes-rental-gateway-YOUR_PROJECT_ID.a.run.app/health

# Test customer creation
curl -X POST \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_API_KEY" \
  -d '{
    "name": "Test Customer",
    "age": 25,
    "contact_info": "test@example.com",
    "is_disabled": false
  }' \
  https://bowling-shoes-rental-gateway-YOUR_PROJECT_ID.a.run.app/customers

# Test discount calculation
curl -X POST \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_API_KEY" \
  -d '{
    "age": 70,
    "is_disabled": true,
    "medical_conditions": ["diabetes"]
  }' \
  https://bowling-shoes-rental-gateway-YOUR_PROJECT_ID.a.run.app/calculate-discount
```

### 2. Load Testing

```bash
# Install artillery for load testing
npm install -g artillery

# Create load test configuration
cat > load-test.yml << 'EOF'
config:
  target: 'https://bowling-shoes-rental-gateway-YOUR_PROJECT_ID.a.run.app'
  phases:
    - duration: 60
      arrivalRate: 10
  defaults:
    headers:
      X-API-Key: 'YOUR_API_KEY'

scenarios:
  - name: "Health Check"
    weight: 50
    flow:
      - get:
          url: "/health"
  - name: "Get Customers"
    weight: 30
    flow:
      - get:
          url: "/customers"
  - name: "Calculate Discount"
    weight: 20
    flow:
      - post:
          url: "/calculate-discount"
          json:
            age: 25
            is_disabled: false
            medical_conditions: null
EOF

# Run load test
artillery run load-test.yml
```

## Version Management

### 1. Create New API Version

```bash
# Create new API configuration version
gcloud api-gateway api-configs create bowling-shoes-config-v2 \
    --api=bowling-shoes-rental \
    --openapi-spec=openapi-spec-v2.yaml \
    --project=YOUR_PROJECT_ID

# Update gateway to use new version
gcloud api-gateway gateways update bowling-shoes-gateway \
    --api=bowling-shoes-rental \
    --api-config=bowling-shoes-config-v2 \
    --location=us-central1 \
    --project=YOUR_PROJECT_ID
```

### 2. Rollback to Previous Version

```bash
# Rollback to previous configuration
gcloud api-gateway gateways update bowling-shoes-gateway \
    --api=bowling-shoes-rental \
    --api-config=bowling-shoes-config \
    --location=us-central1 \
    --project=YOUR_PROJECT_ID
```

## Continuous Deployment

### 1. GitHub Actions Workflow

```yaml
# .github/workflows/deploy-api-gateway.yml
name: Deploy API Gateway

on:
  push:
    branches: [ main ]
    paths: [ 'openapi-spec.yaml' ]

env:
  PROJECT_ID: ${{ secrets.GCP_PROJECT_ID }}
  API_NAME: bowling-shoes-rental
  LOCATION: us-central1

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
    
    - name: Replace project ID in OpenAPI spec
      run: |
        sed -i 's/{project-id}/${{ env.PROJECT_ID }}/g' openapi-spec.yaml
    
    - name: Create API configuration
      run: |
        CONFIG_NAME="bowling-shoes-config-$(date +%Y%m%d%H%M%S)"
        gcloud api-gateway api-configs create $CONFIG_NAME \
          --api=$API_NAME \
          --openapi-spec=openapi-spec.yaml \
          --project=$PROJECT_ID
        
        # Update gateway
        gcloud api-gateway gateways update bowling-shoes-gateway \
          --api=$API_NAME \
          --api-config=$CONFIG_NAME \
          --location=$LOCATION \
          --project=$PROJECT_ID
```

### 2. Cloud Build Configuration

```yaml
# cloudbuild-gateway.yaml
steps:
  # Validate OpenAPI spec
  - name: 'gcr.io/cloud-builders/npm'
    args: ['install', '-g', 'swagger-codegen-cli']
  
  - name: 'gcr.io/cloud-builders/npm'
    args: ['run', 'swagger-codegen-cli', 'validate', '-i', 'openapi-spec.yaml']
  
  # Replace project ID
  - name: 'gcr.io/cloud-builders/gcloud'
    args: ['config', 'set', 'project', '$PROJECT_ID']
  
  - name: 'bash'
    args: ['sed', '-i', 's/{project-id}/$PROJECT_ID/g', 'openapi-spec.yaml']
  
  # Deploy API Gateway
  - name: 'gcr.io/cloud-builders/gcloud'
    args:
    - 'api-gateway'
    - 'api-configs'
    - 'create'
    - 'bowling-shoes-config-$BUILD_ID'
    - '--api=bowling-shoes-rental'
    - '--openapi-spec=openapi-spec.yaml'
  
  - name: 'gcr.io/cloud-builders/gcloud'
    args:
    - 'api-gateway'
    - 'gateways'
    - 'update'
    - 'bowling-shoes-gateway'
    - '--api=bowling-shoes-rental'
    - '--api-config=bowling-shoes-config-$BUILD_ID'
    - '--location=us-central1'

options:
  logging: CLOUD_LOGGING_ONLY
```

## Troubleshooting

### Common Issues

1. **API Gateway Creation Failed**:
   ```bash
   # Check API status
   gcloud api-gateway apis describe bowling-shoes-rental
   
   # Check configuration
   gcloud api-gateway api-configs describe bowling-shoes-config \
     --api=bowling-shoes-rental
   ```

2. **Backend Service Unreachable**:
   ```bash
   # Verify Cloud Run service is running
   gcloud run services describe bowling-shoes-rental --region=us-central1
   
   # Check backend URL in OpenAPI spec
   grep -A 2 "x-google-backend" openapi-spec.yaml
   ```

3. **Authentication Issues**:
   ```bash
   # Test API key
   curl -H "X-API-Key: YOUR_API_KEY" \
     https://bowling-shoes-rental-gateway-YOUR_PROJECT_ID.a.run.app/health
   
   # Check API key restrictions
   gcloud alpha services api-keys describe API_KEY_ID
   ```

### Debugging Commands

```bash
# View API Gateway logs
gcloud logging read "resource.type=api_gateway" --limit=50

# Check API Gateway metrics
gcloud monitoring metrics list --filter="metric.type:apigateway"

# Test connectivity
gcloud api-gateway operations list --filter="done:false"
```

## Cleanup

```bash
# Delete API Gateway
gcloud api-gateway gateways delete bowling-shoes-gateway \
    --location=us-central1

# Delete API configurations
gcloud api-gateway api-configs delete bowling-shoes-config \
    --api=bowling-shoes-rental

# Delete API
gcloud api-gateway apis delete bowling-shoes-rental
```

## Benefits of API Gateway

1. **Centralized Management**: Single point for API configuration
2. **Security**: Built-in authentication and authorization
3. **Monitoring**: Request metrics and logging
4. **Rate Limiting**: Protect backend services from overload
5. **Documentation**: Auto-generated API documentation
6. **Versioning**: Easy API version management
7. **CORS**: Built-in CORS support
8. **Validation**: Request/response validation

## Conclusion

This deployment guide provides a comprehensive approach to deploying your FastAPI application through Google Cloud API Gateway. The setup includes:

- ✅ OpenAPI specification with comprehensive documentation
- ✅ Authentication and authorization
- ✅ Rate limiting and quotas
- ✅ Monitoring and alerting
- ✅ Security best practices
- ✅ CI/CD integration
- ✅ Version management

Your API will be enterprise-ready with professional API management capabilities. 