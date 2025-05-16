# Medspa Appointment System

A simple appointment management system for medical spas built with Python and PostgreSQL.

## Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/medspa.git
cd medspa
```

2. Start the application using Docker:
```bash
cd docker
docker compose build
docker compose up
```

The application will be available at `http://localhost:8000`

## Acceptance Criteria

1. Design a database schema
   - The database schema can be found in [schema.sql](db/schema.sql). It defines the following tables:
      - `medspas`: Basic information about each medical spa location
      - `services`: Individual services offered by medspas with pricing and duration
      - `appointments`: Customer appointments with date/time and status
         - `total_duration` and `total_price` are calculated using SQL queries to sum the duration and price of all services in an appointment. While SQL triggers could maintain these totals automatically, direct queries provide a simpler approach that's easier to work in a time constraint assignment.
      - `appointment_services`: Many-to-many relationship between appointments and services
      - `service_categories`: High-level categories of services (e.g. Injectables)
      - `service_types`: Specific types of services within categories (e.g. Chemical Peel)
      - `service_products`: Specific products used for services (e.g. VI Peel)
1. RESTful CRUD endpoints
   1. Service CRUD
      1. Create a service
         ```bash
         curl -X POST http://localhost:8000/services \
           -H "Content-Type: application/json" \
           -d '{
             "medspa_id": 1,
             "category_id": 1,
             "type_id": 1,
             "product_id": 1,
             "name": "VI Peel Treatment", 
             "description": "Medical-grade chemical peel that improves skin tone and texture",
             "price": 299.99,
             "duration": 45
           }'
         ```
      1. Update a service
         ```bash
         curl -X PUT http://localhost:8000/services/1 \
           -H "Content-Type: application/json" \
           -d '{
             "name": "Premium VI Peel Treatment",
             "description": "Advanced medical-grade chemical peel with enhanced formulation", 
             "price": 349.99,
             "duration": 60
           }'
         ```
      1. Read service by id
         ```bash
         curl http://localhost:8000/services/1
         ```
      1. Read all services from a specific Medspa
         ```bash
         curl http://localhost:8000/medspas/1/services
         ```
   1. Appointments CRUD
      1. Create appointment
         ```bash
         curl -X POST http://localhost:8000/appointments \
           -H "Content-Type: application/json" \
           -d '{
             "medspa_id": 1,
             "start_time": "2024-01-15T14:30:00",
             "service_ids": [1, 2]
           }'
         ```
      1. Read appointment by id
         ```bash
         curl http://localhost:8000/appointments/1
         ```
      1. Update appointment's status
         ```bash
         curl -X PUT http://localhost:8000/appointments/1 \
           -H "Content-Type: application/json" \
           -d '{
             "status": "completed"
           }'
         ```
      1. List all appointments
         1. Filter by status
            ```bash
            curl http://localhost:8000/appointments?status=scheduled
            ```
         1. Filter by date
            ```bash
            curl http://localhost:8000/appointments?start_date=2024-01-15
            ```
         1. Filter by both
            ```bash
            curl http://localhost:8000/appointments?start_date=scheduled&date=2024-01-15
            ```
