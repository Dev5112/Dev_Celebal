-- Customer Cohort Retention
WITH customer_cohorts AS (
    SELECT 
        customer_id,
        STRFTIME('%Y-%m', MIN(order_date)) AS cohort_month
    FROM orders
    GROUP BY customer_id
),
cohort_sizes AS (
    SELECT 
        cohort_month,
        COUNT(DISTINCT customer_id) AS total_customers
    FROM customer_cohorts
    GROUP BY cohort_month
),
order_months AS (
    SELECT 
        o.customer_id,
        c.cohort_month,
        STRFTIME('%Y-%m', o.order_date) AS order_month,
        CAST(
            (CAST(STRFTIME('%Y', o.order_date) AS INTEGER) - CAST(SUBSTR(c.cohort_month, 1, 4) AS INTEGER)) * 12 + 
            (CAST(STRFTIME('%m', o.order_date) AS INTEGER) - CAST(SUBSTR(c.cohort_month, 6, 2) AS INTEGER))
        AS INTEGER) AS month_number
    FROM orders o
    JOIN customer_cohorts c ON o.customer_id = c.customer_id
),
retention_data AS (
    SELECT 
        cohort_month,
        month_number,
        COUNT(DISTINCT customer_id) AS active_customers
    FROM order_months
    WHERE month_number <= 3
    GROUP BY cohort_month, month_number
)
SELECT 
    r.cohort_month,
    s.total_customers,
    SUM(CASE WHEN r.month_number = 0 THEN r.active_customers ELSE 0 END) * 100.0 / s.total_customers AS month_0_retention,
    SUM(CASE WHEN r.month_number = 1 THEN r.active_customers ELSE 0 END) * 100.0 / s.total_customers AS month_1_retention,
    SUM(CASE WHEN r.month_number = 2 THEN r.active_customers ELSE 0 END) * 100.0 / s.total_customers AS month_2_retention,
    SUM(CASE WHEN r.month_number = 3 THEN r.active_customers ELSE 0 END) * 100.0 / s.total_customers AS month_3_retention
FROM retention_data r
JOIN cohort_sizes s ON r.cohort_month = s.cohort_month
GROUP BY r.cohort_month, s.total_customers
ORDER BY r.cohort_month;
