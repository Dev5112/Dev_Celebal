-- Query 1: Revenue by Category
SELECT 
    p.category,
    SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent/100.0)) AS total_revenue,
    SUM(oi.quantity) AS units_sold,
    AVG(oi.discount_percent) AS avg_discount_percent
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
JOIN orders o ON oi.order_id = o.order_id
WHERE o.status IN ('DELIVERED', 'SHIPPED')
GROUP BY p.category
ORDER BY total_revenue DESC;

-- Query 2: Top 10 Customers by Order Value
SELECT 
    c.customer_name,
    c.email,
    COUNT(DISTINCT o.order_id) AS order_count,
    SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent/100.0)) AS total_spend,
    SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent/100.0)) / COUNT(DISTINCT o.order_id) AS avg_order_value
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.status IN ('DELIVERED', 'SHIPPED')
GROUP BY c.customer_id, c.customer_name, c.email
HAVING COUNT(DISTINCT o.order_id) > 1
ORDER BY total_spend DESC
LIMIT 10;

-- Query 3: Monthly Order Count (Last 12 Months)
SELECT 
    STRFTIME('%Y-%m', o.order_date) AS month,
    COUNT(DISTINCT o.order_id) AS order_count,
    SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent/100.0)) AS revenue,
    CAST(SUM(oi.quantity) AS FLOAT) / COUNT(DISTINCT o.order_id) AS avg_items_per_order
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.order_date >= DATETIME('now', '-12 months')
GROUP BY STRFTIME('%Y-%m', o.order_date)
ORDER BY month DESC;
