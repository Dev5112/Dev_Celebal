-- Query 1: Running Revenue Total by Region
SELECT 
    region_code,
    DATE(order_date) AS order_date,
    SUM(quantity * unit_price * (1 - discount_percent/100.0)) AS daily_revenue,
    SUM(SUM(quantity * unit_price * (1 - discount_percent/100.0))) 
        OVER (PARTITION BY region_code ORDER BY DATE(order_date)) AS running_total
FROM order_items oi
JOIN orders o ON oi.order_id = o.order_id
GROUP BY region_code, DATE(order_date)
ORDER BY region_code, order_date;

-- Query 2: Product Ranking by Category
WITH product_revenue AS (
    SELECT 
        p.category,
        p.product_name,
        SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent/100.0)) AS total_revenue
    FROM order_items oi
    JOIN products p ON oi.product_id = p.product_id
    GROUP BY p.category, p.product_name
)
SELECT 
    category,
    product_name,
    total_revenue,
    DENSE_RANK() OVER (PARTITION BY category ORDER BY total_revenue DESC) AS rank,
    PERCENT_RANK() OVER (PARTITION BY category ORDER BY total_revenue DESC) AS rank_percent
FROM product_revenue
ORDER BY category, rank;

-- Query 3: Customer Order Gap Analysis
SELECT 
    customer_id,
    order_date,
    LAG(order_date) OVER (PARTITION BY customer_id ORDER BY order_date) AS previous_order_date,
    JULIANDAY(order_date) - JULIANDAY(LAG(order_date) OVER (PARTITION BY customer_id ORDER BY order_date)) AS days_gap,
    CASE 
        WHEN JULIANDAY(order_date) - JULIANDAY(LAG(order_date) OVER (PARTITION BY customer_id ORDER BY order_date)) > 30 
        THEN 'AT RISK'
        ELSE 'ACTIVE'
    END AS status
FROM orders
ORDER BY customer_id, order_date;
