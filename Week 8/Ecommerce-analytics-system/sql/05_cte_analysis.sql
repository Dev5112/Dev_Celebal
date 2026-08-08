-- Query 1: Monthly Revenue Segmentation
WITH monthly_customer_revenue AS (
    SELECT 
        c.customer_id,
        c.customer_name,
        STRFTIME('%Y-%m', o.order_date) AS month,
        SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent/100.0)) AS monthly_revenue
    FROM customers c
    JOIN orders o ON c.customer_id = o.customer_id
    JOIN order_items oi ON o.order_id = oi.order_id
    GROUP BY c.customer_id, c.customer_name, STRFTIME('%Y-%m', o.order_date)
),
revenue_segments AS (
    SELECT 
        month,
        CASE 
            WHEN monthly_revenue > 1000 THEN 'High'
            WHEN monthly_revenue BETWEEN 500 AND 1000 THEN 'Medium'
            ELSE 'Low'
        END AS segment,
        COUNT(*) AS customer_count
    FROM monthly_customer_revenue
    GROUP BY month, segment
)
SELECT * FROM revenue_segments ORDER BY month, segment;

-- Query 2: Customer Quartile Segmentation (RFM)
WITH rfm_metrics AS (
    SELECT 
        c.customer_id,
        c.customer_name,
        JULIANDAY('now') - JULIANDAY(MAX(o.order_date)) AS recency_days,
        COUNT(DISTINCT o.order_id) AS frequency,
        SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent/100.0)) AS monetary
    FROM customers c
    LEFT JOIN orders o ON c.customer_id = o.customer_id AND o.status = 'DELIVERED'
    LEFT JOIN order_items oi ON o.order_id = oi.order_id
    GROUP BY c.customer_id, c.customer_name
),
quartile_segments AS (
    SELECT 
        customer_id,
        customer_name,
        NTILE(4) OVER (ORDER BY recency_days DESC) AS recency_quartile,
        NTILE(4) OVER (ORDER BY frequency ASC) AS frequency_quartile,
        NTILE(4) OVER (ORDER BY monetary DESC) AS monetary_quartile,
        CASE 
            WHEN NTILE(4) OVER (ORDER BY frequency DESC, monetary DESC) = 1 THEN 'Platinum'
            WHEN NTILE(4) OVER (ORDER BY frequency DESC, monetary DESC) = 2 THEN 'Gold'
            WHEN NTILE(4) OVER (ORDER BY frequency DESC, monetary DESC) = 3 THEN 'Silver'
            ELSE 'Bronze'
        END AS segment_label
    FROM rfm_metrics
)
SELECT * FROM quartile_segments ORDER BY segment_label, customer_id;

-- Query 3: Year-over-Year Revenue Comparison
WITH yearly_monthly_revenue AS (
    SELECT 
        STRFTIME('%Y', o.order_date) AS year,
        STRFTIME('%m', o.order_date) AS month,
        SUM(oi.quantity * oi.unit_price * (1 - oi.discount_percent/100.0)) AS revenue
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    WHERE o.status IN ('DELIVERED', 'SHIPPED')
    GROUP BY STRFTIME('%Y', o.order_date), STRFTIME('%m', o.order_date)
)
SELECT 
    year,
    month,
    revenue,
    LAG(revenue) OVER (PARTITION BY month ORDER BY year) AS previous_year_revenue,
    ROUND(((revenue - LAG(revenue) OVER (PARTITION BY month ORDER BY year)) / LAG(revenue) OVER (PARTITION BY month ORDER BY year) * 100), 2) AS growth_percent
FROM yearly_monthly_revenue
ORDER BY year DESC, month;
