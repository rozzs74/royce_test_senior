# Bowling Shoes Rental Service

A FastAPI-based backend service for managing bowling shoe rentals with LLM-powered discount calculations. This service integrates with Supabase for database management and uses OpenAI's GPT models for intelligent discount determination.

## Features

- **Customer Management**: Create and retrieve customer records with personal information
- **Rental Management**: Handle shoe rentals with automatic discount calculation
- **LLM Integration**: Uses OpenAI GPT for intelligent discount determination with fallback to rule-based system
- **Supabase Integration**: PostgreSQL database with parametrized queries for security
- **FastAPI**: Modern, fast web framework with automatic API documentation
- **Docker Support**: Containerized application for easy deployment
- **Input Validation**: Comprehensive validation using Pydantic
- **Health Checks**: Built-in health monitoring endpoints

## Architecture

### Technology Stack

- **Backend**: FastAPI (Python 3.11)
- **Database**: PostgreSQL via Supabase
- **LLM**: OpenAI GPT-3.5-turbo
- **Validation**: Pydantic with custom validators
- **Database Access**: Raw SQL with parametrized queries (asyncpg)
- **Containerization**: Docker & Docker Compose

### Design Choices

1. **No SQLAlchemy**: Used raw SQL with parametrized queries for better control and security
2. **Pydantic Validation**: Comprehensive input validation with custom validators
3. **LLM with Fallback**: OpenAI for discount calculation with rule-based fallback
4. **Supabase Integration**: Direct PostgreSQL connection for performance
5. **Async Architecture**: Full async/await support for better performance

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

- Docker and Docker Compose
- Supabase account
- OpenAI API key

### Environment Variables

1. Copy the environment template:
   ```bash
   cp env.example .env
   ```

2. Fill in your environment variables:
   ```bash
   SUPABASE_URL=your_supabase_project_url
   SUPABASE_KEY=your_supabase_anon_key
   OPENAI_API_KEY=your_openai_api_key
   DATABASE_URL=postgresql://postgres:postgres@db:5432/bowling_rental
   ```

### Database Setup

1. **Option A: Using Supabase (Recommended)**
   - Create a new Supabase project
   - Go to SQL Editor in Supabase dashboard
   - Execute the contents of `schema.sql`

2. **Option B: Using Local PostgreSQL**
   - The docker-compose.yml includes a PostgreSQL container
   - Schema will be automatically applied on first run

### Running the Application

1. **Using Docker Compose (Recommended)**:
   ```bash
   docker-compose up --build
   ```

2. **Local Development**:
   ```bash
   pip install -r requirements.txt
   uvicorn app.main:app --reload
   ```

### Accessing the Application

- **API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Database Admin** (if using local DB): http://localhost:8080

## API Endpoints

### Customer Management

#### Create Customer
- **POST** `/customers`
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
- **GET** `/customers`

#### Get Customer by ID
- **GET** `/customers/{customer_id}`

### Rental Management

#### Create Rental
- **POST** `/rentals`
- **Body**:
  ```json
  {
    "customer_id": 1,
    "shoe_size": 10.5,
    "rental_fee": 25.00
  }
  ```

#### Get All Rentals
- **GET** `/rentals`

#### Get Rental by ID
- **GET** `/rentals/{rental_id}`

#### Get Customer Rentals
- **GET** `/customers/{customer_id}/rentals`

### Discount Calculation

#### Calculate Discount
- **POST** `/calculate-discount`
- **Body**:
  ```json
  {
    "age": 70,
    "is_disabled": true,
    "medical_conditions": ["diabetes", "hypertension"]
  }
  ```

#### Validate Discount Logic
- **POST** `/validate-discount`
- Compares LLM and rule-based results

### System Endpoints

#### Health Check
- **GET** `/health`

#### Root Information
- **GET** `/`

## Database Schema

### Customers Table
```sql
CREATE TABLE customers (
    id SERIAL PRIMARY KEY,
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
    id SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(id),
    shoe_size DECIMAL(3,1) NOT NULL CHECK (shoe_size > 0),
    rental_fee DECIMAL(10,2) NOT NULL CHECK (rental_fee > 0),
    discount DECIMAL(3,2) NOT NULL DEFAULT 0.00,
    total_fee DECIMAL(10,2) NOT NULL CHECK (total_fee >= 0),
    rental_date TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

## LLM Integration

### Prompt Engineering

The system uses carefully crafted prompts to ensure accurate discount calculations:

1. **Clear Instructions**: Detailed discount rules and constraints
2. **Structured Output**: JSON format for consistent parsing
3. **Fallback System**: Rule-based calculation if LLM fails
4. **Validation**: Comparison between LLM and rule-based results

### Example Prompt
```
You are a discount calculation expert for a bowling shoe rental service.
Your task is to determine the appropriate discount percentage based on customer information.

DISCOUNT RULES:
1. Age-based discounts:
   - Age 0-12: 20% discount
   - Age 13-18: 10% discount  
   - Age 65 and above: 15% discount

2. Disability status:
   - Disabled customers: 25% discount

3. Medical conditions:
   - Diabetes: 10% discount
   - Hypertension: 10% discount
   - Chronic condition: 10% discount

IMPORTANT RULES:
- If multiple discounts apply, choose the HIGHEST discount percentage
- Only apply ONE discount (the highest one)
```

## Security Features

1. **Parametrized Queries**: All SQL queries use parameters to prevent injection
2. **Input Validation**: Comprehensive validation with Pydantic custom validators
3. **Environment Variables**: Sensitive data in environment variables
4. **Health Checks**: Built-in monitoring endpoints
5. **CORS Configuration**: Configurable cross-origin resource sharing

## Testing

### Automated Test Scripts

Run the provided test scripts to verify the application:

```bash
# Test API endpoints (requires running application)
python3 test_api.py

# Test Pydantic validation (standalone)
python3 test_validation.py
```

### Example Customer Creation
```bash
curl -X POST "http://localhost:8000/customers" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Jane Smith",
    "age": 70,
    "contact_info": "jane.smith@example.com",
    "is_disabled": true,
    "medical_conditions": ["diabetes", "hypertension"]
  }'
```

### Example Rental Creation
```bash
curl -X POST "http://localhost:8000/rentals" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": 1,
    "shoe_size": 8.5,
    "rental_fee": 25.00
  }'
```

### Example Discount Calculation
```bash
curl -X POST "http://localhost:8000/calculate-discount" \
  -H "Content-Type: application/json" \
  -d '{
    "age": 70,
    "is_disabled": true,
    "medical_conditions": ["diabetes"]
  }'
```

## Deployment

### Production Deployment

1. **Environment Setup**:
   - Set production environment variables
   - Configure Supabase production database
   - Set up OpenAI API key

2. **Docker Deployment**:
   ```bash
   docker-compose -f docker-compose.yml up -d
   ```

3. **Database Migration**:
   - Execute `schema.sql` in your Supabase production database

### Monitoring

- Health checks available at `/health`
- Application logs via Docker logs
- Database monitoring via Supabase dashboard

## Troubleshooting

### Common Issues

1. **Database Connection Issues**:
   - Check Supabase URL and key
   - Verify network connectivity
   - Check database permissions

2. **LLM API Issues**:
   - Verify OpenAI API key
   - Check API rate limits
   - System falls back to rule-based calculation

3. **Docker Issues**:
   - Ensure Docker and Docker Compose are installed
   - Check port availability (8000, 5432, 8080)
   - Verify environment variables

### Logs

```bash
# View application logs
docker-compose logs app

# View database logs
docker-compose logs db

# View all logs
docker-compose logs
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is part of a take-home examination for a Senior Engineer position.

---

**Note**: This implementation focuses on core functionality and can be extended with additional features like authentication, rate limiting, caching, and more sophisticated error handling for production use. 