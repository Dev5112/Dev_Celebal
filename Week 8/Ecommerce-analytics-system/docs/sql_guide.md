# SQL Guide

The Analytics Engine leverages several complex SQL operations across its queries:

## Common Table Expressions (CTEs)
Used extensively for multi-step calculations, like computing monthly aggregates before bucketing into revenue segments (High, Medium, Low), or calculating an RFM base table before scoring.
- Reference: `sql/05_cte_analysis.sql`
- Reference: `sql/07_rfm_analysis.sql`

## Window Functions
- **`SUM() OVER(...)`**: Used to compute the running total of daily revenue partitioned by region.
- **`DENSE_RANK() OVER(...)` & `PERCENT_RANK()`**: Ranks products by revenue within their respective categories.
- **`LAG() OVER(...)`**: Compares a customer's current order date to their previous order date to compute order frequency gaps (Customer At Risk status) or month-over-month revenue growth.
- **`NTILE(X) OVER(...)`**: Splits customers into quintiles or quartiles based on their RFM attributes (Recency, Frequency, Monetary).

## Self-Joins (Market Basket)
Calculates product affinity by joining the `order_items` table to itself on `order_id`, matching `product_a` with `product_b`, ensuring `product_id_a < product_id_b` to avoid duplicates.

## Aggregations
Heavy use of conditional aggregations (`SUM(CASE WHEN...)`) particularly within the Cohort Retention logic to pivot rows into columns (Month 0, Month 1, Month 2, Month 3 retention percentages).
