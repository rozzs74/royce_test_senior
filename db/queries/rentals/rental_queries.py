from typing import List, Optional, Dict, Any
from uuid import UUID


class RentalQueries:
    """Rental-related database queries"""
    
    @staticmethod
    async def create_rental(db_manager, rental_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new rental using parametrized query"""
        query = """
            INSERT INTO rentals (customer_id, shoe_size, rental_fee, discount, total_fee)
            VALUES ($1, $2, $3, $4, $5)
            RETURNING id, customer_id, shoe_size, rental_fee, discount, total_fee, rental_date
        """
        
        result = await db_manager.execute_query_one(
            query,
            rental_data['customer_id'],
            rental_data['shoe_size'],
            rental_data['rental_fee'],
            rental_data['discount'],
            rental_data['total_fee']
        )
        
        return result

    @staticmethod
    async def get_rental(db_manager, rental_id: UUID) -> Optional[Dict[str, Any]]:
        """Get a rental by UUID"""
        query = "SELECT id, customer_id, shoe_size, rental_fee, discount, total_fee, rental_date FROM rentals WHERE id = $1"
        return await db_manager.execute_query_one(query, rental_id)

    @staticmethod
    async def get_rentals(db_manager) -> List[Dict[str, Any]]:
        """Get all rentals"""
        query = "SELECT id, customer_id, shoe_size, rental_fee, discount, total_fee, rental_date FROM rentals ORDER BY rental_date DESC"
        return await db_manager.execute_query(query)

    @staticmethod
    async def get_rentals_by_customer(db_manager, customer_id: UUID) -> List[Dict[str, Any]]:
        """Get all rentals for a specific customer by UUID"""
        query = "SELECT id, customer_id, shoe_size, rental_fee, discount, total_fee, rental_date FROM rentals WHERE customer_id = $1 ORDER BY rental_date DESC"
        return await db_manager.execute_query(query, customer_id) 