WITH product_pairs AS (
    SELECT 
        oi1.product_id AS product_a,
        oi2.product_id AS product_b,
        COUNT(DISTINCT oi1.order_id) AS times_bought_together
    FROM order_items oi1
    JOIN order_items oi2 ON oi1.order_id = oi2.order_id
    WHERE oi1.product_id < oi2.product_id
    GROUP BY oi1.product_id, oi2.product_id
    HAVING times_bought_together > 2
)
SELECT 
    p1.product_name AS product_a,
    p2.product_name AS product_b,
    pp.times_bought_together,
    ROUND((CAST(pp.times_bought_together AS FLOAT) / (SELECT COUNT(DISTINCT order_id) FROM orders) * 100), 2) AS percent_of_orders
FROM product_pairs pp
JOIN products p1 ON pp.product_a = p1.product_id
JOIN products p2 ON pp.product_b = p2.product_id
ORDER BY pp.times_bought_together DESC;
