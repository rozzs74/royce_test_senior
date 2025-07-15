# Bowling Shoes Rental Service

A FastAPI-based backend service for managing bowling shoe rentals with LLM-powered discount calculations. This service integrates with Supabase for database management and uses Google's Gemini AI for intelligent discount determination.

## Features

- **Customer Management**: Create and retrieve customer records with personal information
- **Rental Management**: Handle shoe rentals with automatic discount calculation
- **LLM Integration**: Uses Google Gemini 2.0 Flash for intelligent discount determination with fallback to rule-based system
- **Supabase Integration**: PostgreSQL database with parametrized queries for security
- **FastAPI**: Modern, fast web framework with automatic API documentation
- **Docker Support**: Containerized application for easy deployment
- **Input Validation**: Comprehensive validation using Pydantic
- **Health Checks**: Built-in health monitoring endpoints
- **Makefile Commands**: Streamlined development workflow with make commands

## Architecture

### Technology Stack

- **Backend**: FastAPI (Python 3.11)
- **Database**: PostgreSQL via Supabase
- **LLM**: Google Gemini 2.0 Flash
- **Validation**: Pydantic with custom validators
- **Database Access**: Raw SQL with parametrized queries (asyncpg)
- **Containerization**: Docker & Docker Compose
- **Build Tool**: Makefile for development workflow

### Design Choices

1. **SQL**: Used raw SQL with parametrized queries for better control and security
2. **Pydantic Validation**: Comprehensive input validation with custom validators
3. **LLM with Fallback**: Google Gemini for discount calculation with rule-based fallback
4. **Supabase Integration**: Direct PostgreSQL connection for performance
5. **Async Architecture**: Full async/await support for better performance
6. **Make Commands**: Simplified development workflow with Makefile

## Discount Model

The system applies discounts based on the following criteria:

| Criteria | Condition | Discount |
|----------|-----------|----------|
| Age | 0-12 years | 20% |
| Age | 13-18 years | 10% |
| Age | 65+ years | 15% |
| Disability | Disabled | 25% |
| Medical | Diabetes | 10% |
| Medical | Hypertension | 10% |
| Medical | Chronic Condition | 10% |

**Note**: Only the highest applicable discount is applied.

## Setup Instructions

### Prerequisites
- Fint the API KEY under config/settings.py
- Docker and Docker Compose
- Python 3.11+ (for local development)
- Google API Key for Gemini AI
- Supabase account and database

### Environment Setup

1. **Create environment file**:
   ```bash
   mkdir -p environments
   cp env.example environments/.env.dev
   ```

2. **Configure `environments/.env.dev`**:
   ```env
   # Google AI Configuration
   GOOGLE_API_KEY=your_google_ai_api_key
   
   # Database Configuration
   DATABASE_USERNAME=postgres.your_project_ref
   DATABASE_HOST=aws-0-ap-southeast-1.pooler.supabase.com
   DATABASE_NAME=postgres
   DATABASE_PASSWORD=your_database_password
   DATABASE_PORT=6543
   
   # Environment
   ENVIRONMENT=development
   DEBUG=true
   ```

### Running the Application

#### Using Makefile (Recommended)

```bash
# Start the application
make start

# Stop the application
make stop

# Build Docker image
make build

# Run with Docker Compose
make run

# View help
make help

# Clean Docker containers and images
make clean
```

#### Manual Docker Commands

```bash
# Build and run with Docker Compose
docker-compose up --build

# Run in background
docker-compose up --build -d
```

### Accessing the Application

- **API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## Available Make Commands

| Command | Description |
|---------|-------------|
| `make help` | Show available commands |
| `make start` | Start application with environment setup |
| `make stop` | Stop the FastAPI application |
| `make build` | Build Docker image |
| `make run` | Run with Docker Compose |
| `make test` | Run tests |
| `make clean` | Clean Docker containers and images |
| `make deploy` | Deploy to Google Cloud Run |

## API Authentication

All API endpoints require authentication using a Bearer token:

```bash
# In API documentation, click "Authorize" and enter:
hBGZPVk5MPNX7hrU3Ut2akE4

# Or use curl with Authorization header:
curl -H "Authorization: Bearer hBGZPVk5MPNX7hrU3Ut2akE4" \
     http://localhost:8000/customers/
```

## API Endpoints

### Customer Management

#### Create Customer
- **POST** `/customers/`
- **Authorization**: Required
- **Body**:
  ```json
  {
    "name": "John Doe",
    "age": 25,
    "contact_info": "john.doe@example.com",
    "is_disabled": false,
    "medical_conditions": ["diabetes"]
  }
  ```

#### Get All Customers
- **GET** `/customers/`
- **Authorization**: Required

#### Get Customer by ID
- **GET** `/customers/{customer_id}`
- **Authorization**: Required

#### Get Customer Rentals
- **GET** `/customers/{customer_id}/rentals`
- **Authorization**: Required

### Rental Management

#### Create Rental
- **POST** `/rentals/`
- **Authorization**: Required
- **Body**:
  ```json
  {
    "customer_id": "550e8400-e29b-41d4-a716-446655440001",
    "shoe_size": 10.5,
    "rental_fee": 25.00,
    "discount": 0.0,
    "total_fee": 25.00
  }
  ```

#### Get All Rentals
- **GET** `/rentals/`
- **Authorization**: Required

#### Get Rental by ID
- **GET** `/rentals/{rental_id}`
- **Authorization**: Required

### Discount Calculation (Gemini AI)

#### Calculate Discount
- **POST** `/discount/calculate`
- **Authorization**: Required
- **Body**:
  ```json
  {
    "age": 70,
    "is_disabled": true,
    "medical_conditions": ["diabetes", "hypertension"]
  }
  ```

#### Validate Discount Logic
- **POST** `/discount/validate`
- **Authorization**: Required
- Compares Gemini AI and rule-based results

### System Endpoints

#### Health Check
- **GET** `/health`
- **Authorization**: Not required

#### Root Information
- **GET** `/`
- **Authorization**: Not required

## Database Schema

### Customers Table
```sql
CREATE TABLE customers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    age INTEGER NOT NULL CHECK (age >= 0 AND age <= 120),
    contact_info VARCHAR(200) NOT NULL,
    is_disabled BOOLEAN DEFAULT FALSE,
    medical_conditions TEXT[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Rentals Table
```sql
CREATE TABLE rentals (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id UUID NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    shoe_size DECIMAL(3,1) NOT NULL CHECK (shoe_size > 0 AND shoe_size <= 20),
    rental_fee DECIMAL(10,2) NOT NULL CHECK (rental_fee > 0),
    discount DECIMAL(3,2) NOT NULL DEFAULT 0.00 CHECK (discount >= 0 AND discount <= 1),
    total_fee DECIMAL(10,2) NOT NULL CHECK (total_fee >= 0),
    rental_date TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

## Google Gemini AI Integration

### Model Configuration

- **Model**: Google Gemini 2.0 Flash Experimental
- **Temperature**: 0.1 (for consistent results)
- **Max Tokens**: 150
- **Fallback**: Rule-based calculation system

### Prompt Engineering

The system uses carefully crafted prompts to ensure accurate discount calculations:

```
You are a discount calculation
``` 