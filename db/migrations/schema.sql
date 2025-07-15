-- Bowling Shoes Rental Service Database Schema
-- This schema should be executed in your Supabase SQL editor

-- Enable UUID extension (required for UUID generation)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create customers table with UUID primary key
CREATE TABLE IF NOT EXISTS customers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    age INTEGER NOT NULL CHECK (age >= 0 AND age <= 120),
    contact_info VARCHAR(200) NOT NULL,
    is_disabled BOOLEAN DEFAULT FALSE,
    medical_conditions TEXT[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create rentals table with UUID primary key and foreign key
CREATE TABLE IF NOT EXISTS rentals (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id UUID NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    shoe_size DECIMAL(3,1) NOT NULL CHECK (shoe_size > 0 AND shoe_size <= 20),
    rental_fee DECIMAL(10,2) NOT NULL CHECK (rental_fee > 0),
    discount DECIMAL(3,2) NOT NULL DEFAULT 0.00 CHECK (discount >= 0 AND discount <= 1),
    total_fee DECIMAL(10,2) NOT NULL CHECK (total_fee >= 0),
    rental_date TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_customers_name ON customers(name);
CREATE INDEX IF NOT EXISTS idx_customers_age ON customers(age);
CREATE INDEX IF NOT EXISTS idx_rentals_customer_id ON rentals(customer_id);
CREATE INDEX IF NOT EXISTS idx_rentals_rental_date ON rentals(rental_date);

-- Insert sample data with explicit UUIDs (optional)
-- Note: In production, let the database generate UUIDs automatically
INSERT INTO customers (id, name, age, contact_info, is_disabled, medical_conditions) VALUES
('550e8400-e29b-41d4-a716-446655440001', 'John Doe', 25, 'john.doe@example.com', false, NULL),
('550e8400-e29b-41d4-a716-446655440002', 'Jane Smith', 70, 'jane.smith@example.com', true, ARRAY['diabetes', 'hypertension']),
('550e8400-e29b-41d4-a716-446655440003', 'Bob Johnson', 15, 'bob.johnson@example.com', false, NULL),
('550e8400-e29b-41d4-a716-446655440004', 'Alice Brown', 8, 'alice.brown@example.com', false, NULL),
('550e8400-e29b-41d4-a716-446655440005', 'Charlie Wilson', 45, 'charlie.wilson@example.com', false, ARRAY['chronic condition'])
ON CONFLICT (id) DO NOTHING;

-- Create a view for rental summaries
CREATE OR REPLACE VIEW rental_summaries AS
SELECT 
    r.id,
    r.customer_id,
    c.name as customer_name,
    c.age,
    c.is_disabled,
    c.medical_conditions,
    r.shoe_size,
    r.rental_fee,
    r.discount,
    r.total_fee,
    r.rental_date
FROM rentals r
JOIN customers c ON r.customer_id = c.id
ORDER BY r.rental_date DESC;

-- Migration queries to convert existing SERIAL data to UUID (if needed)
-- WARNING: Run these only if you have existing data and want to migrate
-- These are commented out for safety - uncomment and modify as needed

/*
-- Step 1: Add new UUID columns
ALTER TABLE customers ADD COLUMN new_id UUID DEFAULT uuid_generate_v4();
ALTER TABLE rentals ADD COLUMN new_id UUID DEFAULT uuid_generate_v4();
ALTER TABLE rentals ADD COLUMN new_customer_id UUID;

-- Step 2: Update foreign key references
UPDATE rentals 
SET new_customer_id = customers.new_id 
FROM customers 
WHERE rentals.customer_id = customers.id;

-- Step 3: Drop old constraints and columns, rename new columns
ALTER TABLE rentals DROP CONSTRAINT rentals_customer_id_fkey;
ALTER TABLE customers DROP CONSTRAINT customers_pkey;
ALTER TABLE rentals DROP CONSTRAINT rentals_pkey;

ALTER TABLE customers DROP COLUMN id;
ALTER TABLE rentals DROP COLUMN id;
ALTER TABLE rentals DROP COLUMN customer_id;

ALTER TABLE customers RENAME COLUMN new_id TO id;
ALTER TABLE rentals RENAME COLUMN new_id TO id;
ALTER TABLE rentals RENAME COLUMN new_customer_id TO customer_id;

-- Step 4: Add back constraints
ALTER TABLE customers ADD PRIMARY KEY (id);
ALTER TABLE rentals ADD PRIMARY KEY (id);
ALTER TABLE rentals ADD CONSTRAINT rentals_customer_id_fkey 
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE;
*/ 