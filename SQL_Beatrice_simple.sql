
SET NAMES utf8mb4;

CREATE TABLE IF NOT EXISTS clinic_info (
    id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    name VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    address VARCHAR(500) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    whatsapp VARCHAR(20),
    instagram VARCHAR(255),
    working_hours VARCHAR(255) NOT NULL,
    map_url VARCHAR(500),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS users (
    id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    full_name VARCHAR(255) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    email VARCHAR(255),
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('patient', 'doctor', 'admin') NOT NULL DEFAULT 'patient',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT uq_users_phone UNIQUE (phone),
    CONSTRAINT uq_users_email UNIQUE (email)
);

CREATE TABLE IF NOT EXISTS refresh_tokens (
    id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    user_id CHAR(36) NOT NULL,
    token_hash VARCHAR(255) NOT NULL,
    expires_at DATETIME NOT NULL,
    revoked_at DATETIME,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_refresh_tokens_user
        FOREIGN KEY (user_id) REFERENCES users(id)
        ON DELETE CASCADE,
    CONSTRAINT uq_refresh_tokens_token_hash UNIQUE (token_hash)
);

CREATE TABLE IF NOT EXISTS service_categories (
    id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    title VARCHAR(255) NOT NULL,
    slug VARCHAR(255) NOT NULL,
    description TEXT,
    image_url VARCHAR(500),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT uq_service_categories_slug UNIQUE (slug)
);

CREATE TABLE IF NOT EXISTS services (
    id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    category_id CHAR(36) NOT NULL,
    title VARCHAR(255) NOT NULL,
    slug VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    duration_minutes INT,
    image_url VARCHAR(500),
    contraindications TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_services_category
        FOREIGN KEY (category_id) REFERENCES service_categories(id),
    CONSTRAINT uq_services_slug UNIQUE (slug),
    CONSTRAINT chk_services_price CHECK (price >= 0),
    CONSTRAINT chk_services_duration CHECK (duration_minutes IS NULL OR duration_minutes > 0)
);

CREATE TABLE IF NOT EXISTS specialists (
    id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    user_id CHAR(36),
    full_name VARCHAR(255) NOT NULL,
    position VARCHAR(255) NOT NULL,
    specialization VARCHAR(255) NOT NULL,
    experience_years INT,
    photo_url VARCHAR(500),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_specialists_user
        FOREIGN KEY (user_id) REFERENCES users(id)
        ON DELETE SET NULL,
    CONSTRAINT uq_specialists_user UNIQUE (user_id),
    CONSTRAINT chk_specialists_experience CHECK (experience_years IS NULL OR experience_years >= 0)
);

CREATE TABLE IF NOT EXISTS specialist_services (
    specialist_id CHAR(36) NOT NULL,
    service_id CHAR(36) NOT NULL,
    PRIMARY KEY (specialist_id, service_id),
    CONSTRAINT fk_specialist_services_specialist
        FOREIGN KEY (specialist_id) REFERENCES specialists(id)
        ON DELETE CASCADE,
    CONSTRAINT fk_specialist_services_service
        FOREIGN KEY (service_id) REFERENCES services(id)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS appointments (
    id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    patient_id CHAR(36),
    patient_name VARCHAR(255) NOT NULL,
    patient_phone VARCHAR(20) NOT NULL,
    service_id CHAR(36) NOT NULL,
    specialist_id CHAR(36) NOT NULL,
    appointment_date DATE NOT NULL,
    appointment_time TIME NOT NULL,
    status ENUM('pending', 'confirmed', 'completed', 'cancelled') NOT NULL DEFAULT 'pending',
    comment TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_appointments_patient
        FOREIGN KEY (patient_id) REFERENCES users(id)
        ON DELETE SET NULL,
    CONSTRAINT fk_appointments_service
        FOREIGN KEY (service_id) REFERENCES services(id),
    CONSTRAINT fk_appointments_specialist
        FOREIGN KEY (specialist_id) REFERENCES specialists(id),
    CONSTRAINT uq_appointments_specialist_slot UNIQUE (specialist_id, appointment_date, appointment_time)
);

CREATE TABLE IF NOT EXISTS doctor_schedule (
    id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    specialist_id CHAR(36) NOT NULL,
    schedule_date DATE NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    is_available BOOLEAN NOT NULL DEFAULT TRUE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_doctor_schedule_specialist
        FOREIGN KEY (specialist_id) REFERENCES specialists(id)
        ON DELETE CASCADE,
    CONSTRAINT uq_doctor_schedule_slot UNIQUE (specialist_id, schedule_date, start_time, end_time),
    CONSTRAINT chk_doctor_schedule_time CHECK (start_time < end_time)
);

CREATE TABLE IF NOT EXISTS product_categories (
    id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    title VARCHAR(255) NOT NULL,
    slug VARCHAR(255) NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT uq_product_categories_slug UNIQUE (slug)
);

CREATE TABLE IF NOT EXISTS products (
    id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    category_id CHAR(36) NOT NULL,
    title VARCHAR(255) NOT NULL,
    slug VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    image_url VARCHAR(500),
    stock INT NOT NULL DEFAULT 0,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_products_category
        FOREIGN KEY (category_id) REFERENCES product_categories(id),
    CONSTRAINT uq_products_slug UNIQUE (slug),
    CONSTRAINT chk_products_price CHECK (price >= 0),
    CONSTRAINT chk_products_stock CHECK (stock >= 0)
);

CREATE TABLE IF NOT EXISTS wishlist_items (
    id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    user_id CHAR(36) NOT NULL,
    product_id CHAR(36) NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_wishlist_items_user
        FOREIGN KEY (user_id) REFERENCES users(id)
        ON DELETE CASCADE,
    CONSTRAINT fk_wishlist_items_product
        FOREIGN KEY (product_id) REFERENCES products(id)
        ON DELETE CASCADE,
    CONSTRAINT uq_wishlist_items_user_product UNIQUE (user_id, product_id)
);

CREATE TABLE IF NOT EXISTS cart_items (
    id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    user_id CHAR(36) NOT NULL,
    product_id CHAR(36) NOT NULL,
    quantity INT NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    subtotal DECIMAL(10,2) GENERATED ALWAYS AS (quantity * price) STORED,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_cart_items_user
        FOREIGN KEY (user_id) REFERENCES users(id)
        ON DELETE CASCADE,
    CONSTRAINT fk_cart_items_product
        FOREIGN KEY (product_id) REFERENCES products(id),
    CONSTRAINT uq_cart_items_user_product UNIQUE (user_id, product_id),
    CONSTRAINT chk_cart_items_quantity CHECK (quantity >= 1),
    CONSTRAINT chk_cart_items_price CHECK (price >= 0)
);

CREATE TABLE IF NOT EXISTS orders (
    id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    order_number VARCHAR(30) NOT NULL,
    user_id CHAR(36) NOT NULL,
    total_price DECIMAL(10,2) NOT NULL,
    payment_status ENUM('pending', 'paid', 'failed', 'refunded') NOT NULL DEFAULT 'pending',
    order_status ENUM('created', 'paid', 'processing', 'delivered', 'cancelled') NOT NULL DEFAULT 'created',
    payment_method ENUM('card_online', 'cash_on_delivery') NOT NULL DEFAULT 'card_online',
    delivery_method ENUM('courier', 'pickup') NOT NULL DEFAULT 'courier',
    delivery_address VARCHAR(500) NOT NULL,
    recipient_name VARCHAR(255) NOT NULL,
    recipient_phone VARCHAR(20) NOT NULL,
    comment TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_orders_user
        FOREIGN KEY (user_id) REFERENCES users(id),
    CONSTRAINT uq_orders_order_number UNIQUE (order_number),
    CONSTRAINT chk_orders_total_price CHECK (total_price >= 0)
);

CREATE TABLE IF NOT EXISTS order_items (
    id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    order_id CHAR(36) NOT NULL,
    product_id CHAR(36),
    product_title VARCHAR(255) NOT NULL,
    product_slug VARCHAR(255) NOT NULL,
    quantity INT NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    subtotal DECIMAL(10,2) NOT NULL,
    CONSTRAINT fk_order_items_order
        FOREIGN KEY (order_id) REFERENCES orders(id)
        ON DELETE CASCADE,
    CONSTRAINT fk_order_items_product
        FOREIGN KEY (product_id) REFERENCES products(id)
        ON DELETE SET NULL,
    CONSTRAINT chk_order_items_quantity CHECK (quantity >= 1),
    CONSTRAINT chk_order_items_price CHECK (price >= 0),
    CONSTRAINT chk_order_items_subtotal CHECK (subtotal >= 0)
);

CREATE TABLE IF NOT EXISTS payments (
    id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    order_id CHAR(36) NOT NULL,
    payment_url VARCHAR(1000) NOT NULL,
    provider_payment_id VARCHAR(255),
    status ENUM('pending', 'paid', 'failed', 'refunded') NOT NULL DEFAULT 'pending',
    expires_at DATETIME,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_payments_order
        FOREIGN KEY (order_id) REFERENCES orders(id)
        ON DELETE CASCADE,
    CONSTRAINT uq_payments_provider_payment_id UNIQUE (provider_payment_id)
);

CREATE TABLE IF NOT EXISTS reviews (
    id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    author_name VARCHAR(255) NOT NULL,
    rating INT NOT NULL,
    text TEXT NOT NULL,
    source VARCHAR(50) NOT NULL DEFAULT '2gis',
    source_url VARCHAR(1000),
    is_published BOOLEAN NOT NULL DEFAULT TRUE,
    sort_order INT NOT NULL DEFAULT 0,
    published_at DATETIME,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT chk_reviews_rating CHECK (rating >= 1 AND rating <= 5),
    CONSTRAINT chk_reviews_sort_order CHECK (sort_order >= 0)
);

CREATE TABLE IF NOT EXISTS recommendations (
    id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    patient_id CHAR(36),
    doctor_id CHAR(36) NOT NULL,
    appointment_id CHAR(36),
    text TEXT NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_recommendations_patient
        FOREIGN KEY (patient_id) REFERENCES users(id),
    CONSTRAINT fk_recommendations_doctor
        FOREIGN KEY (doctor_id) REFERENCES users(id),
    CONSTRAINT fk_recommendations_appointment
        FOREIGN KEY (appointment_id) REFERENCES appointments(id)
        ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS recommendation_products (
    recommendation_id CHAR(36) NOT NULL,
    product_id CHAR(36) NOT NULL,
    PRIMARY KEY (recommendation_id, product_id),
    CONSTRAINT fk_recommendation_products_recommendation
        FOREIGN KEY (recommendation_id) REFERENCES recommendations(id)
        ON DELETE CASCADE,
    CONSTRAINT fk_recommendation_products_product
        FOREIGN KEY (product_id) REFERENCES products(id)
        ON DELETE CASCADE
);

CREATE INDEX ix_services_category_id ON services(category_id);
CREATE INDEX ix_services_title ON services(title);
CREATE INDEX ix_specialists_full_name ON specialists(full_name);
CREATE INDEX ix_appointments_patient_id ON appointments(patient_id);
CREATE INDEX ix_appointments_specialist_date ON appointments(specialist_id, appointment_date);
CREATE INDEX ix_products_category_id ON products(category_id);
CREATE INDEX ix_products_title ON products(title);
CREATE INDEX ix_orders_user_id ON orders(user_id);
CREATE INDEX ix_reviews_published_sort ON reviews(is_published, sort_order);
CREATE INDEX ix_recommendations_patient_id ON recommendations(patient_id);
CREATE INDEX ix_recommendations_doctor_id ON recommendations(doctor_id);
