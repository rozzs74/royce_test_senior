# Supabase Setup Guide

This guide explains how to connect the Bowling Shoes Rental Service RESTful API to Supabase.

## What is Supabase?

Supabase is an open-source Firebase alternative that provides:
- PostgreSQL database
- Real-time subscriptions
- Authentication
- Auto-generated APIs
- Dashboard for database management

## Setting up Supabase

### 1. Create a Supabase Account

1. Go to [https://supabase.com](https://supabase.com)
2. Sign up for a free account
3. Create a new project

### 2. Get Your Supabase Credentials

After creating a project, you'll need:

1. **Project URL**: Found in Settings → API
   - Format: `https://your-project-id.supabase.co`
   
2. **Anon Key**: Found in Settings → API
   - This is your public API key for client-side access
   
3. **Service Role Key**: Found in Settings → API (optional)
   - This is for server-side operations with elevated privileges

### 3. Database Connection

Our application connects to Supabase in two ways:

#### Option A: Direct PostgreSQL Connection (Recommended)
```python
# Uses asyncpg for direct PostgreSQL connection
DATABASE_URL=postgresql://postgres:[password]@db.your-project-id.supabase.co:5432/postgres
```

#### Option B: Supabase Client Library
```python
# Uses the Supabase Python client
from supabase import create_client, Client

supabase: Client = create_client(supabase_url, supabase_key)
```

## Configuration Steps

### 1. Environment Variables

Create a `.env` file with your Supabase credentials:

```bash
# Supabase Configuration
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your_anon_key_here
OPENAI_API_KEY=your_openai_api_key_here

# Direct PostgreSQL connection (for asyncpg)
DATABASE_URL=postgresql://postgres:your_password@db.your-project-id.supabase.co:5432/postgres
```

### 2. Database Schema Setup

1. Go to your Supabase dashboard
2. Navigate to the SQL Editor
3. Copy and paste the contents of `schema.sql` from this project
4. Execute the SQL to create tables and sample data

### 3. Database Password

To get your database password:
1. Go to Settings → Database in your Supabase dashboard
2. Find the "Connection string" section
3. Reset the database password if needed
4. Use this password in your `DATABASE_URL`

## How the Application Connects

### Database Manager (`app/database.py`)

The `DatabaseManager` class handles connections:

```python
class DatabaseManager:
    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")
        self.database_url = os.getenv("DATABASE_URL")
        
        # Supabase client for REST API operations
        self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
        
        # Direct PostgreSQL connection for custom queries
        self.pool = None

    async def init_pool(self):
        """Initialize asyncpg connection pool for direct SQL queries"""
        if self.database_url:
            self.pool = await asyncpg.create_pool(self.database_url)
```

### Why Two Connection Methods?

1. **Supabase Client**: 
   - Good for simple CRUD operations
   - Handles authentication automatically
   - Built-in real-time features

2. **Direct PostgreSQL (asyncpg)**:
   - Better performance for complex queries
   - Full control over SQL
   - Parametrized queries for security
   - Required for this project (no SQLAlchemy)

## Security Features

### 1. Parametrized Queries

All database operations use parametrized queries to prevent SQL injection:

```python
async def create_customer(self, customer_data: Dict[str, Any]) -> Dict[str, Any]:
    query = """
        INSERT INTO customers (name, age, contact_info, is_disabled, medical_conditions)
        VALUES ($1, $2, $3, $4, $5)
        RETURNING id, name, age, contact_info, is_disabled, medical_conditions, created_at
    """
    
    result = await self.execute_query_one(
        query,
        customer_data['name'],
        customer_data['age'],
        customer_data['contact_info'],
        customer_data['is_disabled'],
        medical_conditions
    )
```

### 2. Row Level Security (RLS)

You can enable RLS in Supabase for additional security:

```sql
-- Enable RLS on tables
ALTER TABLE customers ENABLE ROW LEVEL SECURITY;
ALTER TABLE rentals ENABLE ROW LEVEL SECURITY;

-- Create policies (example)
CREATE POLICY "Enable read access for all users" ON customers FOR SELECT USING (true);
CREATE POLICY "Enable insert access for all users" ON customers FOR INSERT WITH CHECK (true);
```

## Testing the Connection

### 1. Health Check

The application includes a health check endpoint:
```bash
curl http://localhost:8000/health
```

### 2. Database Connection Test

Test database connectivity:
```bash
# Test customer creation
curl -X POST "http://localhost:8000/customers" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Customer",
    "age": 25,
    "contact_info": "test@example.com",
    "is_disabled": false,
    "medical_conditions": []
  }'
```

### 3. Run Test Suite

Use the provided test script:
```bash
python3 test_api.py
```

## Common Issues and Solutions

### 1. Connection Refused

**Problem**: `Connection refused` error
**Solution**: 
- Check if your Supabase project is active
- Verify the DATABASE_URL format
- Ensure your IP is not blocked

### 2. Authentication Failed

**Problem**: `Authentication failed` error
**Solution**:
- Check your database password
- Verify the username (usually `postgres`)
- Reset password in Supabase dashboard

### 3. SSL Certificate Issues

**Problem**: SSL certificate errors
**Solution**:
- Add `?sslmode=require` to your DATABASE_URL
- Or use `?sslmode=disable` for testing (not recommended for production)

### 4. Connection Pool Issues

**Problem**: Connection pool exhaustion
**Solution**:
- Increase pool size in asyncpg configuration
- Implement connection pooling limits
- Monitor connection usage

## Monitoring and Debugging

### 1. Supabase Dashboard

Monitor your database through the Supabase dashboard:
- Database → Tables: View and edit data
- Database → Logs: Check query logs
- Settings → API: Monitor API usage

### 2. Application Logs

Check application logs for connection issues:
```bash
# Docker logs
docker-compose logs app

# Direct logs
uvicorn app.main:app --log-level debug
```

### 3. Database Queries

Monitor database performance:
```sql
-- Check active connections
SELECT * FROM pg_stat_activity;

-- Check table sizes
SELECT schemaname,tablename,attname,n_distinct,correlation FROM pg_stats;
```

## Production Considerations

### 1. Connection Pooling

For production, configure proper connection pooling:

```python
# In database.py
self.pool = await asyncpg.create_pool(
    self.database_url,
    min_size=5,
    max_size=20,
    max_queries=50000,
    max_inactive_connection_lifetime=300
)
```

### 2. Environment Variables

Use proper environment variable management:
- Use Docker secrets for sensitive data
- Implement environment-specific configurations
- Use external secret management services

### 3. Database Optimization

- Create proper indexes
- Monitor query performance
- Implement query caching
- Use read replicas for scaling

## Conclusion

This setup provides a robust connection between your FastAPI application and Supabase, combining the ease of use of Supabase's managed PostgreSQL with the performance and flexibility of direct SQL queries. The dual connection approach ensures you can leverage both Supabase's features and have full control over your database operations. 