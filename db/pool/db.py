import asyncpg
import asyncio
from typing import Optional, List, Dict, Any
import logging
from contextlib import asynccontextmanager
import uuid

from config.settings import Settings

logger = logging.getLogger(__name__)


class DatabaseManager:
    def __init__(self):
        self._pool: Optional[asyncpg.Pool] = None
    
    async def init_pool(self) -> None:
        """Initialize database connection pool"""
        try:
            # Use individual database parameters like Node.js approach
            database_config = {
                "user": Settings.DATABASE_USER,  # Changed from DATABASE_USER
                "host": Settings.DATABASE_HOST,
                "database": Settings.DATABASE_NAME,
                "password": Settings.DATABASE_PASSWORD,
                "port": Settings.DATABASE_PORT,
                "min_size": 1,
                "max_size": 10,
                "command_timeout": 60,
                # Disable statement cache for pgbouncer compatibility
                "statement_cache_size": 0
            }
            
            logger.info(f"Connecting to database: {Settings.DATABASE_USER}@{Settings.DATABASE_HOST}:{Settings.DATABASE_PORT}/{Settings.DATABASE_NAME}")
            
            self._pool = await asyncpg.create_pool(**database_config)
            
            # Test the connection
            async with self._pool.acquire() as connection:
                result = await connection.fetchval("SELECT 1")
                logger.info(f"Database connection test successful: {result}")
            
            logger.info("Database connection pool initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize database pool: {e}")
            logger.error(f"Database config: user={Settings.DATABASE_USER}, host={Settings.DATABASE_HOST}, database={Settings.DATABASE_NAME}, port={Settings.DATABASE_PORT}")
            raise
    
    async def close_pool(self) -> None:
        """Close database connection pool"""
        if self._pool:
            await self._pool.close()
            logger.info("Database connection pool closed")
    
    @asynccontextmanager
    async def get_connection(self):
        """Get database connection from pool"""
        if not self._pool:
            raise RuntimeError("Database pool not initialized")
        
        async with self._pool.acquire() as connection:
            yield connection
    
    # Customer methods
    async def create_customer(self, customer_data) -> str:
        """Create a new customer and return the ID"""
        async with self.get_connection() as connection:
            customer_id = str(uuid.uuid4())
            await connection.execute(
                """
                INSERT INTO customers (id, name, age, contact_info, is_disabled, medical_conditions)
                VALUES ($1, $2, $3, $4, $5, $6)
                """,
                customer_id,
                customer_data.name,
                customer_data.age,
                customer_data.contact_info,
                customer_data.is_disabled,
                customer_data.medical_conditions
            )
            return customer_id
    
    async def get_customer_by_id(self, customer_id: str) -> Optional[Dict[str, Any]]:
        """Get customer by ID"""
        async with self.get_connection() as connection:
            row = await connection.fetchrow(
                "SELECT * FROM customers WHERE id = $1",
                customer_id
            )
            return dict(row) if row else None
    
    async def list_customers(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """List customers with pagination"""
        async with self.get_connection() as connection:
            rows = await connection.fetch(
                "SELECT * FROM customers ORDER BY created_at DESC OFFSET $1 LIMIT $2",
                skip, limit
            )
            return [dict(row) for row in rows]
    
    # Rental methods
    async def create_rental(self, rental_data) -> str:
        """Create a new rental and return the ID"""
        async with self.get_connection() as connection:
            rental_id = str(uuid.uuid4())
            await connection.execute(
                """
                INSERT INTO rentals (id, customer_id, shoe_size, rental_fee, discount, total_fee)
                VALUES ($1, $2, $3, $4, $5, $6)
                """,
                rental_id,
                rental_data.customer_id,
                rental_data.shoe_size,
                rental_data.rental_fee,
                rental_data.discount,
                rental_data.total_fee
            )
            return rental_id
    
    async def get_rental_by_id(self, rental_id: str) -> Optional[Dict[str, Any]]:
        """Get rental by ID"""
        async with self.get_connection() as connection:
            row = await connection.fetchrow(
                "SELECT * FROM rentals WHERE id = $1",
                rental_id
            )
            return dict(row) if row else None
    
    async def list_rentals(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """List rentals with pagination"""
        async with self.get_connection() as connection:
            rows = await connection.fetch(
                "SELECT * FROM rentals ORDER BY rental_date DESC OFFSET $1 LIMIT $2",
                skip, limit
            )
            return [dict(row) for row in rows]
    
    async def get_rentals_by_customer_id(self, customer_id: str) -> List[Dict[str, Any]]:
        """Get all rentals for a customer"""
        async with self.get_connection() as connection:
            rows = await connection.fetch(
                "SELECT * FROM rentals WHERE customer_id = $1 ORDER BY rental_date DESC",
                customer_id
            )
            return [dict(row) for row in rows]


# Global database manager instance
db_manager = DatabaseManager()
