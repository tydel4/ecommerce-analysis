-- E-Commerce Database Schema
-- This schema supports comprehensive e-commerce analysis

-- Customers table
CREATE TABLE customers (
    customer_id INTEGER PRIMARY KEY,
    customer_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    registration_date DATE NOT NULL,
    location VARCHAR(50),
    age_group VARCHAR(20),
    income_level VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Products table
CREATE TABLE products (
    product_id INTEGER PRIMARY KEY,
    product_name VARCHAR(200) NOT NULL,
    category VARCHAR(100),
    subcategory VARCHAR(100),
    price DECIMAL(10,2) NOT NULL,
    cost DECIMAL(10,2) NOT NULL,
    brand VARCHAR(100),
    profit_margin DECIMAL(5,4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Transactions table
CREATE TABLE transactions (
    transaction_id INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    transaction_date TIMESTAMP NOT NULL,
    payment_method VARCHAR(50),
    shipping_method VARCHAR(50),
    total_amount DECIMAL(10,2) NOT NULL,
    total_cost DECIMAL(10,2) NOT NULL,
    profit DECIMAL(10,2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

-- Customer segments table (for storing analysis results)
CREATE TABLE customer_segments (
    customer_id INTEGER PRIMARY KEY,
    segment VARCHAR(50),
    rfm_score VARCHAR(10),
    recency INTEGER,
    frequency INTEGER,
    monetary DECIMAL(10,2),
    clv DECIMAL(10,2),
    churn_risk DECIMAL(5,4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

-- Product performance table (for storing analysis results)
CREATE TABLE product_performance (
    product_id INTEGER PRIMARY KEY,
    total_sales INTEGER,
    total_revenue DECIMAL(10,2),
    total_profit DECIMAL(10,2),
    unique_customers INTEGER,
    avg_order_quantity DECIMAL(5,2),
    revenue_per_customer DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

-- Sales analytics table (for storing daily/monthly summaries)
CREATE TABLE sales_analytics (
    date_id DATE PRIMARY KEY,
    total_transactions INTEGER,
    total_revenue DECIMAL(10,2),
    total_profit DECIMAL(10,2),
    unique_customers INTEGER,
    avg_order_value DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for better performance
CREATE INDEX idx_customers_location ON customers(location);
CREATE INDEX idx_customers_age_group ON customers(age_group);
CREATE INDEX idx_customers_income_level ON customers(income_level);
CREATE INDEX idx_customers_registration_date ON customers(registration_date);

CREATE INDEX idx_products_category ON products(category);
CREATE INDEX idx_products_brand ON products(brand);
CREATE INDEX idx_products_price ON products(price);

CREATE INDEX idx_transactions_customer_id ON transactions(customer_id);
CREATE INDEX idx_transactions_product_id ON transactions(product_id);
CREATE INDEX idx_transactions_date ON transactions(transaction_date);
CREATE INDEX idx_transactions_payment_method ON transactions(payment_method);

CREATE INDEX idx_customer_segments_segment ON customer_segments(segment);
CREATE INDEX idx_customer_segments_rfm_score ON customer_segments(rfm_score);

CREATE INDEX idx_product_performance_category ON product_performance(product_id);

-- Views for common queries

-- Customer summary view
CREATE VIEW customer_summary AS
SELECT 
    c.customer_id,
    c.customer_name,
    c.email,
    c.location,
    c.age_group,
    c.income_level,
    COUNT(t.transaction_id) as total_orders,
    SUM(t.total_amount) as total_spent,
    AVG(t.total_amount) as avg_order_value,
    SUM(t.quantity) as total_items,
    MIN(t.transaction_date) as first_purchase,
    MAX(t.transaction_date) as last_purchase,
    COUNT(DISTINCT t.product_id) as unique_products,
    SUM(t.profit) as total_profit
FROM customers c
LEFT JOIN transactions t ON c.customer_id = t.customer_id
GROUP BY c.customer_id, c.customer_name, c.email, c.location, c.age_group, c.income_level;

-- Product summary view
CREATE VIEW product_summary AS
SELECT 
    p.product_id,
    p.product_name,
    p.category,
    p.subcategory,
    p.brand,
    p.price,
    p.cost,
    p.profit_margin,
    COUNT(t.transaction_id) as total_sales,
    SUM(t.quantity) as total_units_sold,
    SUM(t.total_amount) as total_revenue,
    SUM(t.profit) as total_profit,
    COUNT(DISTINCT t.customer_id) as unique_customers,
    AVG(t.quantity) as avg_order_quantity
FROM products p
LEFT JOIN transactions t ON p.product_id = t.product_id
GROUP BY p.product_id, p.product_name, p.category, p.subcategory, p.brand, p.price, p.cost, p.profit_margin;

-- Daily sales summary view
CREATE VIEW daily_sales_summary AS
SELECT 
    DATE(transaction_date) as sale_date,
    COUNT(transaction_id) as total_transactions,
    SUM(total_amount) as total_revenue,
    SUM(profit) as total_profit,
    COUNT(DISTINCT customer_id) as unique_customers,
    AVG(total_amount) as avg_order_value
FROM transactions
GROUP BY DATE(transaction_date)
ORDER BY sale_date;

-- Monthly sales summary view
CREATE VIEW monthly_sales_summary AS
SELECT 
    DATE_FORMAT(transaction_date, '%Y-%m-01') as month_start,
    COUNT(transaction_id) as total_transactions,
    SUM(total_amount) as total_revenue,
    SUM(profit) as total_profit,
    COUNT(DISTINCT customer_id) as unique_customers,
    AVG(total_amount) as avg_order_value
FROM transactions
GROUP BY DATE_FORMAT(transaction_date, '%Y-%m-01')
ORDER BY month_start;

-- Top customers view
CREATE VIEW top_customers AS
SELECT 
    c.customer_id,
    c.customer_name,
    c.location,
    c.age_group,
    c.income_level,
    COUNT(t.transaction_id) as total_orders,
    SUM(t.total_amount) as total_spent,
    AVG(t.total_amount) as avg_order_value,
    SUM(t.profit) as total_profit,
    DATEDIFF(CURRENT_DATE, MAX(t.transaction_date)) as days_since_last_purchase
FROM customers c
LEFT JOIN transactions t ON c.customer_id = t.customer_id
GROUP BY c.customer_id, c.customer_name, c.location, c.age_group, c.income_level
HAVING total_spent > 0
ORDER BY total_spent DESC;

-- Top products view
CREATE VIEW top_products AS
SELECT 
    p.product_id,
    p.product_name,
    p.category,
    p.brand,
    p.price,
    COUNT(t.transaction_id) as total_sales,
    SUM(t.quantity) as total_units_sold,
    SUM(t.total_amount) as total_revenue,
    SUM(t.profit) as total_profit,
    COUNT(DISTINCT t.customer_id) as unique_customers
FROM products p
LEFT JOIN transactions t ON p.product_id = t.product_id
GROUP BY p.product_id, p.product_name, p.category, p.brand, p.price
HAVING total_sales > 0
ORDER BY total_revenue DESC;

-- Customer segments view
CREATE VIEW customer_segments_summary AS
SELECT 
    cs.segment,
    COUNT(*) as customer_count,
    AVG(cs.clv) as avg_clv,
    AVG(cs.churn_risk) as avg_churn_risk,
    AVG(cs.recency) as avg_recency,
    AVG(cs.frequency) as avg_frequency,
    AVG(cs.monetary) as avg_monetary
FROM customer_segments cs
GROUP BY cs.segment
ORDER BY avg_clv DESC;

-- Product category performance view
CREATE VIEW category_performance AS
SELECT 
    p.category,
    COUNT(DISTINCT p.product_id) as product_count,
    COUNT(t.transaction_id) as total_sales,
    SUM(t.quantity) as total_units_sold,
    SUM(t.total_amount) as total_revenue,
    SUM(t.profit) as total_profit,
    AVG(t.total_amount) as avg_order_value,
    COUNT(DISTINCT t.customer_id) as unique_customers
FROM products p
LEFT JOIN transactions t ON p.product_id = t.product_id
GROUP BY p.category
ORDER BY total_revenue DESC; 