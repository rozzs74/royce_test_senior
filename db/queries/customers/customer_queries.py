from typing import List, Optional, Dict, Any
from uuid import UUID


class CustomerQueries:
    """Customer-related database queries"""
    
    @staticmethod
    async def create_customer(db_manager, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new customer using parametrized query"""
        query = """
            INSERT INTO customers (name, age, contact_info, is_disabled, medical_conditions)
            VALUES ($1, $2, $3, $4, $5)
            RETURNING id, name, age, contact_info, is_disabled, medical_conditions, created_at
        """
        
        medical_conditions = customer_data.get('medical_conditions', [])
        if medical_conditions:
            medical_conditions = '{' + ','.join(f'"{condition}"' for condition in medical_conditions) + '}'
        else:
            medical_conditions = None
        
        result = await db_manager.execute_query_one(
            query,
            customer_data['name'],
            customer_data['age'],
            customer_data['contact_info'],
            customer_data['is_disabled'],
            medical_conditions
        )
        
        if result and result['medical_conditions']:
            # Convert PostgreSQL array back to Python list
            result['medical_conditions'] = result['medical_conditions'].strip('{}').split(',') if result['medical_conditions'] else []
        
        return result

    @staticmethod
    async def get_customer(db_manager, customer_id: UUID) -> Optional[Dict[str, Any]]:
        """Get a customer by UUID"""
        query = "SELECT id, name, age, contact_info, is_disabled, medical_conditions, created_at FROM customers WHERE id = $1"
        result = await db_manager.execute_query_one(query, customer_id)
        
        if result and result['medical_conditions']:
            # Convert PostgreSQL array back to Python list
            result['medical_conditions'] = result['medical_conditions'].strip('{}').split(',') if result['medical_conditions'] else []
        
        return result

    @staticmethod
    async def get_customers(db_manager) -> List[Dict[str, Any]]:
        """Get all customers"""
        query = "SELECT id, name, age, contact_info, is_disabled, medical_conditions, created_at FROM customers ORDER BY created_at DESC"
        results = await db_manager.execute_query(query)
        
        for result in results:
            if result['medical_conditions']:
                # Convert PostgreSQL array back to Python list
                result['medical_conditions'] = result['medical_conditions'].strip('{}').split(',') if result['medical_conditions'] else []
        
        return results 