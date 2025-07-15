# UUID Migration Guide

This guide explains the migration from SERIAL integer IDs to UUIDs in the Bowling Shoes Rental Service.

## 🔄 Overview

We've migrated from using `SERIAL` (auto-incrementing integers) to `UUID` (Universally Unique Identifiers) for all primary keys and foreign keys in the database.

### Benefits of UUIDs:
- **Global Uniqueness**: No conflicts when merging data from different sources
- **Security**: Harder to guess or enumerate records
- **Scalability**: Better for distributed systems and microservices
- **Privacy**: IDs don't reveal information about data volume or creation order

## 📋 What Changed

### Database Schema (`schema.sql`)
- ✅ **customers.id**: `SERIAL` → `UUID`
- ✅ **rentals.id**: `SERIAL` → `UUID`  
- ✅ **rentals.customer_id**: `INTEGER` → `UUID`
- ✅ Added `uuid-ossp` extension for UUID generation
- ✅ Updated sample data with explicit UUIDs

### Application Models
- ✅ **CustomerResponse.id**: `int` → `UUID`
- ✅ **RentalResponse.id**: `int` → `UUID`
- ✅ **RentalBase.customer_id**: `int` → `UUID`

### Database Queries
- ✅ **CustomerQueries.get_customer()**: `customer_id: int` → `customer_id: UUID`
- ✅ **RentalQueries.get_rental()**: `rental_id: int` → `rental_id: UUID`
- ✅ **RentalQueries.get_rentals_by_customer()**: `customer_id: int` → `customer_id: UUID`

### API Routes
- ✅ **GET /customers/{customer_id}**: `customer_id: int` → `customer_id: UUID`
- ✅ **GET /customers/{customer_id}/rentals**: `customer_id: int` → `customer_id: UUID`
- ✅ **GET /rentals/{rental_id}**: `rental_id: int` → `rental_id: UUID`

## 🚀 Migration Steps

### For New Installations
1. Run the updated `schema.sql` - it includes UUID support
2. Deploy the updated application code
3. All new records will automatically use UUIDs

### For Existing Installations
1. **Backup your database** (CRITICAL!)
2. Run the migration script: `db/migrations/001_migrate_to_uuid.sql`
3. Verify the migration using the included verification queries
4. Deploy the updated application code
5. Test all endpoints to ensure they work with UUIDs

## 📝 API Usage Examples

### Before (Integer IDs)
```bash
# Get customer with integer ID
GET /customers/1

# Create rental with integer customer_id
POST /rentals
{
  "customer_id": 1,
  "shoe_size": 10.5,
  "rental_fee": 15.00
}
```

### After (UUID IDs)
```bash
# Get customer with UUID
GET /customers/550e8400-e29b-41d4-a716-446655440001

# Create rental with UUID customer_id
POST /rentals
{
  "customer_id": "550e8400-e29b-41d4-a716-446655440001",
  "shoe_size": 10.5,
  "rental_fee": 15.00
}
```

## 🔍 Sample UUIDs for Testing

The schema includes sample data with these UUIDs:
- **Customer 1**: `550e8400-e29b-41d4-a716-446655440001` (John Doe)
- **Customer 2**: `550e8400-e29b-41d4-a716-446655440002` (Jane Smith)
- **Customer 3**: `550e8400-e29b-41d4-a716-446655440003` (Bob Johnson)
- **Customer 4**: `550e8400-e29b-41d4-a716-446655440004` (Alice Brown)
- **Customer 5**: `550e8400-e29b-41d4-a716-446655440005` (Charlie Wilson)

## 🧪 Testing

Run the updated test script to verify UUID support:
```bash
python test_api_key_validation.py
```

The test script now includes:
- ✅ UUID-based endpoint testing
- ✅ Customer creation with UUID response
- ✅ Customer retrieval by UUID
- ✅ Rental operations with UUID foreign keys

## ⚠️ Important Notes

### Client Applications
- **Update all client applications** to handle UUID strings instead of integers
- **Validate UUID format** in client-side code
- **Store UUIDs as strings** in client-side databases/storage

### URL Patterns
- URLs now accept UUID format: `/customers/550e8400-e29b-41d4-a716-446655440001`
- FastAPI automatically validates UUID format in path parameters
- Invalid UUID formats will return 422 Unprocessable Entity

### Database Performance
- UUIDs are slightly larger than integers (16 bytes vs 4 bytes)
- Indexes may be slightly slower due to UUID randomness
- Benefits typically outweigh performance costs for most applications

## 🆔 UUID Format

UUIDs are 128-bit identifiers typically displayed as 36-character strings:
```
550e8400-e29b-41d4-a716-446655440001
├─────┬─────┬─────┬─────┬─────────────┘
│     │     │     │     └─ 12 characters
│     │     │     └─ 4 characters  
│     │     └─ 4 characters
│     └─ 4 characters
└─ 8 characters
```

## 🔧 Troubleshooting

### Common Issues:

1. **"Invalid UUID format" errors**
   - Ensure UUIDs are properly formatted
   - Use string format, not integer

2. **Foreign key constraint violations**
   - Verify customer UUIDs exist before creating rentals
   - Check UUID format in request payloads

3. **Migration issues**
   - Always backup before migration
   - Run verification queries after migration
   - Check application logs for UUID parsing errors

### Migration Verification:
```sql
-- Check if all records have valid UUIDs
SELECT COUNT(*) FROM customers WHERE id IS NOT NULL;
SELECT COUNT(*) FROM rentals WHERE id IS NOT NULL AND customer_id IS NOT NULL;

-- Verify foreign key relationships
SELECT COUNT(*) FROM rentals r JOIN customers c ON r.customer_id = c.id;
```

## 📞 Support

If you encounter issues during migration:
1. Check the verification queries in the migration script
2. Review application logs for UUID-related errors
3. Ensure all client applications are updated for UUID support
4. Test with the provided sample UUIDs first 