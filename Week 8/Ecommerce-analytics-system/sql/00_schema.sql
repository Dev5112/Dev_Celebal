-- Customers Table
CREATE TABLE customers (
    customer_id INTEGER PRIMARY KEY CHECK (customer_id > 0),
    customer_name TEXT NOT NULL CHECK (LENGTH(customer_name) > 0),
    email TEXT NOT NULL UNIQUE,
    registration_date DATETIME NOT NULL,
    customer_type TEXT NOT NULL CHECK (customer_type IN ('REGULAR', 'PREMIUM', 'VIP')),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Products Table
CREATE TABLE products (
    product_id INTEGER PRIMARY KEY CHECK (product_id > 0),
    product_name TEXT NOT NULL CHECK (LENGTH(product_name) > 0),
    category TEXT NOT NULL CHECK (category IN ('Electronics', 'Clothing', 'Home', 'Books')),
    subcategory TEXT NOT NULL,
    cost_price DECIMAL(10, 2) NOT NULL CHECK (cost_price > 0),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Orders Table
CREATE TABLE orders (
    order_id INTEGER PRIMARY KEY CHECK (order_id > 0),
    customer_id INTEGER NOT NULL,
    order_date DATETIME NOT NULL CHECK (order_date <= CURRENT_TIMESTAMP),
    status TEXT NOT NULL CHECK (status IN ('PLACED', 'SHIPPED', 'DELIVERED', 'CANCELLED', 'RETURNED')),
    region_code TEXT NOT NULL CHECK (region_code IN ('US-EAST', 'US-WEST', 'EU', 'APAC', 'UNKNOWN')),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE RESTRICT
);

-- Order Items Table
CREATE TABLE order_items (
    item_id INTEGER PRIMARY KEY CHECK (item_id > 0),
    order_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price DECIMAL(10, 2) NOT NULL CHECK (unit_price > 0),
    discount_percent DECIMAL(5, 2) NOT NULL CHECK (discount_percent >= 0 AND discount_percent <= 100),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE RESTRICT
);
