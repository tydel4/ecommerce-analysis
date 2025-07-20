-- E-Commerce Analytics Queries
-- Comprehensive SQL queries for business intelligence and analysis

-- ============================================================================
-- CUSTOMER ANALYSIS QUERIES
-- ============================================================================

-- 1. Customer Lifetime Value Analysis
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
    DATEDIFF(CURRENT_DATE, MAX(t.transaction_date)) as days_since_last_purchase,
    -- Calculate CLV
    (SUM(t.total_amount) * COUNT(t.transaction_id) / 
     GREATEST(DATEDIFF(CURRENT_DATE, MIN(t.transaction_date)), 1)) as clv
FROM customers c
LEFT JOIN transactions t ON c.customer_id = t.customer_id
GROUP BY c.customer_id, c.customer_name, c.location, c.age_group, c.income_level
HAVING total_spent > 0
ORDER BY clv DESC
LIMIT 20;

-- 2. RFM Analysis Query
WITH rfm_calc AS (
    SELECT 
        customer_id,
        DATEDIFF(CURRENT_DATE, MAX(transaction_date)) as recency,
        COUNT(transaction_id) as frequency,
        SUM(total_amount) as monetary
    FROM transactions
    GROUP BY customer_id
),
rfm_scores AS (
    SELECT 
        customer_id,
        recency,
        frequency,
        monetary,
        NTILE(5) OVER (ORDER BY recency DESC) as r_score,
        NTILE(5) OVER (ORDER BY frequency) as f_score,
        NTILE(5) OVER (ORDER BY monetary) as m_score
    FROM rfm_calc
)
SELECT 
    c.customer_id,
    c.customer_name,
    c.location,
    r.recency,
    r.frequency,
    r.monetary,
    r.r_score,
    r.f_score,
    r.m_score,
    CONCAT(r.r_score, r.f_score, r.m_score) as rfm_score,
    CASE 
        WHEN r.r_score >= 4 AND r.f_score >= 4 AND r.m_score >= 4 THEN 'Champions'
        WHEN r.r_score >= 3 AND r.f_score >= 3 AND r.m_score >= 3 THEN 'Loyal Customers'
        WHEN r.r_score >= 3 AND r.f_score >= 1 AND r.m_score >= 1 THEN 'At Risk'
        WHEN r.r_score >= 4 AND r.f_score >= 1 AND r.m_score >= 1 THEN 'Can\'t Lose'
        WHEN r.r_score >= 4 AND r.f_score >= 1 AND r.m_score >= 1 THEN 'New Customers'
        ELSE 'Lost'
    END as segment
FROM customers c
JOIN rfm_scores r ON c.customer_id = r.customer_id
ORDER BY r.monetary DESC;

-- 3. Customer Churn Analysis
SELECT 
    c.customer_id,
    c.customer_name,
    c.location,
    c.age_group,
    COUNT(t.transaction_id) as total_orders,
    SUM(t.total_amount) as total_spent,
    MAX(t.transaction_date) as last_purchase_date,
    DATEDIFF(CURRENT_DATE, MAX(t.transaction_date)) as days_since_last_purchase,
    CASE 
        WHEN DATEDIFF(CURRENT_DATE, MAX(t.transaction_date)) > 90 THEN 'Churned'
        WHEN DATEDIFF(CURRENT_DATE, MAX(t.transaction_date)) > 60 THEN 'At Risk'
        WHEN DATEDIFF(CURRENT_DATE, MAX(t.transaction_date)) > 30 THEN 'Active'
        ELSE 'Very Active'
    END as churn_status
FROM customers c
LEFT JOIN transactions t ON c.customer_id = t.customer_id
GROUP BY c.customer_id, c.customer_name, c.location, c.age_group
HAVING total_orders > 0
ORDER BY days_since_last_purchase DESC;

-- 4. Customer Demographics Analysis
SELECT 
    location,
    age_group,
    income_level,
    COUNT(*) as customer_count,
    AVG(total_spent) as avg_total_spent,
    AVG(total_orders) as avg_total_orders,
    AVG(avg_order_value) as avg_order_value
FROM customer_summary
GROUP BY location, age_group, income_level
ORDER BY avg_total_spent DESC;

-- ============================================================================
-- PRODUCT ANALYSIS QUERIES
-- ============================================================================

-- 5. Top Performing Products
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
    COUNT(DISTINCT t.customer_id) as unique_customers,
    AVG(t.quantity) as avg_order_quantity,
    (SUM(t.profit) / SUM(t.total_amount)) * 100 as profit_margin_percent
FROM products p
LEFT JOIN transactions t ON p.product_id = t.product_id
GROUP BY p.product_id, p.product_name, p.category, p.brand, p.price
HAVING total_sales > 0
ORDER BY total_revenue DESC
LIMIT 20;

-- 6. Product Category Performance
SELECT 
    p.category,
    COUNT(DISTINCT p.product_id) as product_count,
    COUNT(t.transaction_id) as total_sales,
    SUM(t.quantity) as total_units_sold,
    SUM(t.total_amount) as total_revenue,
    SUM(t.profit) as total_profit,
    AVG(t.total_amount) as avg_order_value,
    COUNT(DISTINCT t.customer_id) as unique_customers,
    (SUM(t.profit) / SUM(t.total_amount)) * 100 as profit_margin_percent
FROM products p
LEFT JOIN transactions t ON p.product_id = t.product_id
GROUP BY p.category
ORDER BY total_revenue DESC;

-- 7. Product Profitability Analysis
SELECT 
    p.product_id,
    p.product_name,
    p.category,
    p.price,
    p.cost,
    p.profit_margin,
    COUNT(t.transaction_id) as total_sales,
    SUM(t.total_amount) as total_revenue,
    SUM(t.profit) as total_profit,
    (SUM(t.profit) / SUM(t.total_amount)) * 100 as actual_profit_margin
FROM products p
LEFT JOIN transactions t ON p.product_id = t.product_id
GROUP BY p.product_id, p.product_name, p.category, p.price, p.cost, p.profit_margin
HAVING total_sales > 0
ORDER BY actual_profit_margin DESC;

-- 8. Brand Performance Analysis
SELECT 
    p.brand,
    COUNT(DISTINCT p.product_id) as product_count,
    COUNT(t.transaction_id) as total_sales,
    SUM(t.total_amount) as total_revenue,
    SUM(t.profit) as total_profit,
    COUNT(DISTINCT t.customer_id) as unique_customers,
    AVG(t.total_amount) as avg_order_value
FROM products p
LEFT JOIN transactions t ON p.product_id = t.product_id
WHERE p.brand IS NOT NULL
GROUP BY p.brand
ORDER BY total_revenue DESC;

-- ============================================================================
-- SALES ANALYSIS QUERIES
-- ============================================================================

-- 9. Daily Sales Trend
SELECT 
    DATE(transaction_date) as sale_date,
    COUNT(transaction_id) as total_transactions,
    SUM(total_amount) as total_revenue,
    SUM(profit) as total_profit,
    COUNT(DISTINCT customer_id) as unique_customers,
    AVG(total_amount) as avg_order_value,
    SUM(quantity) as total_units_sold
FROM transactions
GROUP BY DATE(transaction_date)
ORDER BY sale_date;

-- 10. Monthly Sales Analysis
SELECT 
    DATE_FORMAT(transaction_date, '%Y-%m-01') as month_start,
    COUNT(transaction_id) as total_transactions,
    SUM(total_amount) as total_revenue,
    SUM(profit) as total_profit,
    COUNT(DISTINCT customer_id) as unique_customers,
    AVG(total_amount) as avg_order_value,
    -- Month-over-month growth
    LAG(SUM(total_amount)) OVER (ORDER BY DATE_FORMAT(transaction_date, '%Y-%m-01')) as prev_month_revenue,
    ((SUM(total_amount) - LAG(SUM(total_amount)) OVER (ORDER BY DATE_FORMAT(transaction_date, '%Y-%m-01'))) / 
     LAG(SUM(total_amount)) OVER (ORDER BY DATE_FORMAT(transaction_date, '%Y-%m-01'))) * 100 as revenue_growth_percent
FROM transactions
GROUP BY DATE_FORMAT(transaction_date, '%Y-%m-01')
ORDER BY month_start;

-- 11. Payment Method Analysis
SELECT 
    payment_method,
    COUNT(transaction_id) as total_transactions,
    SUM(total_amount) as total_revenue,
    AVG(total_amount) as avg_order_value,
    COUNT(DISTINCT customer_id) as unique_customers
FROM transactions
GROUP BY payment_method
ORDER BY total_revenue DESC;

-- 12. Seasonal Sales Analysis
SELECT 
    MONTH(transaction_date) as month,
    MONTHNAME(transaction_date) as month_name,
    COUNT(transaction_id) as total_transactions,
    SUM(total_amount) as total_revenue,
    SUM(profit) as total_profit,
    COUNT(DISTINCT customer_id) as unique_customers,
    AVG(total_amount) as avg_order_value
FROM transactions
GROUP BY MONTH(transaction_date), MONTHNAME(transaction_date)
ORDER BY month;

-- ============================================================================
-- ADVANCED ANALYTICS QUERIES
-- ============================================================================

-- 13. Customer Cohort Analysis
WITH customer_cohorts AS (
    SELECT 
        customer_id,
        DATE_FORMAT(MIN(transaction_date), '%Y-%m-01') as cohort_month,
        DATE_FORMAT(transaction_date, '%Y-%m-01') as order_month,
        DATEDIFF(
            DATE_FORMAT(transaction_date, '%Y-%m-01'),
            DATE_FORMAT(MIN(transaction_date) OVER (PARTITION BY customer_id), '%Y-%m-01')
        ) / 30 as cohort_period
    FROM transactions
    GROUP BY customer_id, transaction_date
)
SELECT 
    cohort_month,
    cohort_period,
    COUNT(DISTINCT customer_id) as customer_count
FROM customer_cohorts
GROUP BY cohort_month, cohort_period
ORDER BY cohort_month, cohort_period;

-- 14. Product Cross-Selling Analysis
WITH product_pairs AS (
    SELECT 
        t1.customer_id,
        t1.product_id as product1,
        t2.product_id as product2,
        COUNT(*) as pair_count
    FROM transactions t1
    JOIN transactions t2 ON t1.customer_id = t2.customer_id 
        AND t1.transaction_id != t2.transaction_id
        AND t1.product_id < t2.product_id
    GROUP BY t1.customer_id, t1.product_id, t2.product_id
)
SELECT 
    p1.product_name as product1_name,
    p2.product_name as product2_name,
    p1.category as category1,
    p2.category as category2,
    COUNT(*) as pair_frequency
FROM product_pairs pp
JOIN products p1 ON pp.product1 = p1.product_id
JOIN products p2 ON pp.product2 = p2.product_id
GROUP BY pp.product1, pp.product2, p1.product_name, p2.product_name, p1.category, p2.category
ORDER BY pair_frequency DESC
LIMIT 20;

-- 15. Customer Segmentation by Spending Patterns
SELECT 
    customer_id,
    customer_name,
    location,
    total_spent,
    total_orders,
    avg_order_value,
    CASE 
        WHEN total_spent >= 1000 AND total_orders >= 10 THEN 'High-Value Frequent'
        WHEN total_spent >= 1000 AND total_orders < 10 THEN 'High-Value Occasional'
        WHEN total_spent >= 500 AND total_spent < 1000 THEN 'Medium-Value'
        WHEN total_spent >= 100 AND total_spent < 500 THEN 'Low-Value'
        ELSE 'Minimal'
    END as spending_segment
FROM customer_summary
ORDER BY total_spent DESC;

-- 16. Product Recommendation Query (Based on Category Preferences)
SELECT 
    c.customer_id,
    c.customer_name,
    p.category as preferred_category,
    COUNT(t.transaction_id) as category_purchases,
    AVG(t.total_amount) as avg_category_spend,
    -- Recommend products from preferred category not yet purchased
    (SELECT COUNT(*) 
     FROM products p2 
     WHERE p2.category = p.category 
     AND p2.product_id NOT IN (
         SELECT DISTINCT product_id 
         FROM transactions t2 
         WHERE t2.customer_id = c.customer_id
     )) as recommended_products_count
FROM customers c
JOIN transactions t ON c.customer_id = t.customer_id
JOIN products p ON t.product_id = p.product_id
GROUP BY c.customer_id, c.customer_name, p.category
HAVING category_purchases >= 2
ORDER BY category_purchases DESC, avg_category_spend DESC;

-- ============================================================================
-- PERFORMANCE METRICS QUERIES
-- ============================================================================

-- 17. Key Performance Indicators (KPIs)
SELECT 
    'Total Revenue' as metric,
    SUM(total_amount) as value
FROM transactions
UNION ALL
SELECT 
    'Total Profit' as metric,
    SUM(profit) as value
FROM transactions
UNION ALL
SELECT 
    'Total Customers' as metric,
    COUNT(DISTINCT customer_id) as value
FROM transactions
UNION ALL
SELECT 
    'Total Products Sold' as metric,
    COUNT(DISTINCT product_id) as value
FROM transactions
UNION ALL
SELECT 
    'Average Order Value' as metric,
    AVG(total_amount) as value
FROM transactions
UNION ALL
SELECT 
    'Profit Margin %' as metric,
    (SUM(profit) / SUM(total_amount)) * 100 as value
FROM transactions;

-- 18. Customer Retention Rate
WITH customer_activity AS (
    SELECT 
        customer_id,
        DATE_FORMAT(transaction_date, '%Y-%m-01') as activity_month,
        COUNT(DISTINCT DATE_FORMAT(transaction_date, '%Y-%m-01')) as active_months
    FROM transactions
    GROUP BY customer_id, DATE_FORMAT(transaction_date, '%Y-%m-01')
),
retention_calc AS (
    SELECT 
        activity_month,
        COUNT(DISTINCT customer_id) as active_customers,
        LAG(COUNT(DISTINCT customer_id)) OVER (ORDER BY activity_month) as prev_month_customers
    FROM customer_activity
    GROUP BY activity_month
)
SELECT 
    activity_month,
    active_customers,
    prev_month_customers,
    CASE 
        WHEN prev_month_customers > 0 THEN 
            (active_customers / prev_month_customers) * 100
        ELSE NULL 
    END as retention_rate_percent
FROM retention_calc
ORDER BY activity_month; 