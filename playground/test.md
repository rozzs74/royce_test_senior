Take-home Exam for Senior Engineer
Bowling Shoes Rental Service with LLM Integration and Prompt Engineering
Expected Deliverables:
Source code for the FastAPI application, including:
API endpoint implementations.
Database models and CRUD operations.
LLM integration for discount calculation.
Docker setup files (Dockerfile and docker-compose.yml).
SQL schema or migration scripts for setting up the Supabase database.
Documentation (README) covering setup instructions, API usage, and design choices.
Evaluation Criteria:
Code Quality: Clarity, organization, and maintainability of the codebase.
API Design: Adherence to RESTful principles, clarity of API endpoints, and appropriate error handling.
Database Design: Efficiency and scalability of the database schema.
LLM Integration: Effectiveness of the LLM model in determining discounts and its integration with the application.
Containerization: Completeness and correctness of the Docker setup.
Documentation: Completeness, clarity, and usefulness of the provided documentation.
Submission Instructions:
Upload your source code to a GitHub repository.
Give viewing access to: dev@kodeacross.com
Ensure your repository includes all required deliverables.
Submit the GitHub repository URL for review.
By focusing on the core functionalities and integrating a basic LLM model for discount calculations, this simplified version should be feasible to complete within 2-3 hours.
Project Overview:
Develop a minimal backend service for managing a bowling shoe rental operation. This service will handle basic customer registrations, shoe rentals, and fee calculations, including discounts based on customer age. An LLM model will be used to determine applicable discounts based on customer information. Use Supabase as the database and Docker for containerization.
Simplified Requirements:
Customer Management:
Implement functionality to add and retrieve customer records.
Customer records should include: id, name, age, contact_info, is_disabled, and medical_conditions.
Shoe Rental Management:
Implement functionality to manage shoe rentals, including recording the rental date and rental fee.
Calculate the total rental fee after applying any applicable discounts.
Rental records should include: id, customer_id, rental_date, shoe_size, rental_fee, discount, and total_fee.
Discount Calculation:
Use an LLM model to determine if a customer is eligible for a discount based on their age, disability status, and pre-existing medical conditions.
Implement prompt engineering to craft effective queries to the LLM for accurate discount determination.
Implement logic to apply the discount to the rental fee and calculate the total fee.
Database Setup with Supabase:
Use Supabase to create and manage the necessary database tables for customers and rentals.
API Endpoints:
Design and implement RESTful API endpoints to:
Create and retrieve customer records.
Create and retrieve shoe rental records.
Calculate and apply discounts using the LLM model.
Containerization with Docker:
Containerize the application using Docker.
Ensure the application can be easily built and run using Docker.
Discount Model
The discount model for the bowling shoe rental service will be based on the following criteria:
Age:
Age 0-12: 20% discount
Age 13-18: 10% discount
Age 65 and above: 15% discount
Disability Status:
Disabled: 25% discount
Pre-existing Medical Conditions:
Diabetes: 10% discount
Hypertension: 10% discount
Chronic Condition: 10% discount
Sample Discount Model TableKey Functional Requirements:

Criteria
Condition
Discount Percentage
Age
0-12
20%
Age
13-18
10%
Age
65 and above
15%
Disability Status
Disabled
25%
Pre-existing Medical Condition
Diabetes
10%
Pre-existing Medical Condition
Hypertension
10%
Pre-existing Medical Condition
Chronic Condition
10%

Customer Management:
Create Customer: Endpoint to add a new customer.
Get Customers: Endpoint to list all customers.
Shoe Rental Management:
Create Rental: Endpoint to create a new rental, calculate the rental fee, apply the discount using the LLM, and compute the total fee.
Get Rentals: Endpoint to list all rentals.
Discount Calculation:
Use the LLM model to determine discounts based on customer age, disability status, and pre-existing medical conditions.
Implement prompt engineering to craft effective queries to the LLM for accurate discount determination.
Apply the highest eligible discount to the rental fee.
Environment Variables:
Set up environment variables for Supabase URL, Supabase API key, and LLM API key for integration.
Example Calculation:
Consider a customer with the following attributes:
Age: 70
Disability Status: Disabled
Pre-existing Medical Conditions: Diabetes
Age-based Discount:
Age 70 falls under the "65 and above" category, which qualifies for a 15% discount.
Disability Status Discount:
The customer is disabled, which qualifies for a 25% discount.
Pre-existing Medical Conditions Discount:
The customer has diabetes, which qualifies for a 10% discount.
Combining Discounts:
The customer qualifies for multiple discounts. The LLM model will decide on the appropriate discount to apply. For simplicity, you can choose the highest discount percentage (25% in this case).
The final discount to be applied would be 25% in this example.


