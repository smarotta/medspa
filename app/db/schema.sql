-- Create enum type for appointment status
CREATE TYPE appointment_status AS ENUM ('scheduled', 'completed', 'canceled');

CREATE TABLE IF NOT EXISTS medspas (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    address TEXT NOT NULL,
    phone_number TEXT NOT NULL,
    email_address TEXT NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Service Categories
CREATE TABLE IF NOT EXISTS service_categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);

-- Service Types
CREATE TABLE IF NOT EXISTS service_types (
    id SERIAL PRIMARY KEY,
    category_id INTEGER NOT NULL REFERENCES service_categories(id),
    name VARCHAR(255) NOT NULL
);

-- Service Product Suppliers
CREATE TABLE IF NOT EXISTS service_product_suppliers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);

-- Service Products
CREATE TABLE IF NOT EXISTS service_products (
    id SERIAL PRIMARY KEY,
    type_id INTEGER NOT NULL REFERENCES service_types(id),
    supplier_id INTEGER REFERENCES service_product_suppliers(id),
    name VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS services (
    id SERIAL PRIMARY KEY,
    medspa_id INTEGER NOT NULL REFERENCES medspas(id),
    category_id INTEGER NOT NULL REFERENCES service_categories(id),
    type_id INTEGER NOT NULL REFERENCES service_types(id),
    product_id INTEGER NOT NULL REFERENCES service_products(id),
    name TEXT NOT NULL,
    description TEXT,
    price DECIMAL(10,2) NOT NULL,
    duration INTEGER NOT NULL, -- duration in minutes
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS appointments (
    id SERIAL PRIMARY KEY,
    medspa_id INTEGER NOT NULL REFERENCES medspas(id),
    start_time TIMESTAMP NOT NULL,
    status appointment_status NOT NULL DEFAULT 'scheduled',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Join table for appointments and services (many-to-many)
CREATE TABLE IF NOT EXISTS appointment_services (
    appointment_id INTEGER REFERENCES appointments(id) ON DELETE CASCADE,
    service_id INTEGER REFERENCES services(id) ON DELETE CASCADE,
    PRIMARY KEY (appointment_id, service_id)
); 