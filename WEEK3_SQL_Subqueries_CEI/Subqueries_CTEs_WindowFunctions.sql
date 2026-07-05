USE superstore;

CREATE TABLE customers AS
SELECT DISTINCT
    `Customer ID`,
    `Customer Name`,
    Segment,
    Country,
    City,
    State,
    Region
FROM superstore_data;

SELECT * FROM customers
LIMIT 5;

CREATE TABLE products AS
SELECT DISTINCT
    `Product ID`,
    `Product Name`,
    Category,
    `Sub-Category`
FROM superstore_data;

SELECT * FROM products
LIMIT 5;

CREATE TABLE orders AS
SELECT
    `Order ID`,
    `Order Date`,
    `Ship Date`,
    `Ship Mode`,
    `Customer ID`,
    `Product ID`,
    Sales,
    Quantity,
    Discount,
    Profit
FROM superstore_data;

SELECT * FROM orders
LIMIT 5;

SELECT COUNT(*) AS Total_Customers
FROM Customers;

SHOW TABLES;

#------- SUBQUERIES --------
#order above average sales
SELECT *
FROM orders
WHERE Sales >
(
SELECT AVG(Sales)
FROM orders
);

#Customers with order above ₹1000 sales
SELECT *
FROM customers
WHERE `Customer ID` IN
 (
    SELECT `Customer ID`
    FROM orders
    WHERE Sales > 1000
);

#customers total sales
SELECT
    `Customer ID`,
    `Customer Name`,
    (
	 SELECT SUM(Sales)
	 FROM orders
	 WHERE orders.`Customer ID` = customers.`Customer ID`
    ) 
    AS Total_Sales
FROM customers;

#customers average sales greater than 500
SELECT *
FROM (
    SELECT
        `Customer ID`,
        AVG(Sales) AS Avg_Sales
    FROM orders
    GROUP BY `Customer ID`
) AS Customer_Avg
WHERE Avg_Sales > 500; 

#Highest sales made by each customer
SELECT *
FROM orders o
WHERE Sales = (
    SELECT MAX(Sales)
    FROM orders
    WHERE `Customer ID` = o.`Customer ID`
);

#------- CTEs -------

#Total; sales by customer
WITH CustomerSales AS (
    SELECT
        `Customer ID`,
        SUM(Sales) AS Total_Sales
    FROM orders
    GROUP BY `Customer ID`
)
SELECT *
FROM CustomerSales;

#customers with total sales above average 
WITH CustomerSales AS (
    SELECT
        `Customer ID`,
        SUM(Sales) AS Total_Sales
    FROM orders
    GROUP BY `Customer ID`
)
SELECT *
FROM CustomerSales
WHERE Total_Sales >
(
    SELECT AVG(Total_Sales)
    FROM CustomerSales
);

#join customers with their total sales 
WITH CustomerSales AS (
    SELECT
        `Customer ID`,
        SUM(Sales) AS Total_Sales
    FROM orders
    GROUP BY `Customer ID`
)
SELECT
    c.`Customer Name`,
    cs.Total_Sales
FROM customers c
JOIN CustomerSales cs
ON c.`Customer ID` = cs.`Customer ID`
ORDER BY cs.Total_Sales DESC; 

#------- WINDOW FUNCTIONS ----------

#ROW NUMBER
SELECT
    `Order ID`,
    `Customer ID`,
    Sales,
    ROW_NUMBER() OVER (ORDER BY Sales DESC) AS Row_Num
FROM orders;

#RANK
SELECT
    `Order ID`,
    `Customer ID`,
    Sales,
    RANK() OVER (ORDER BY Sales DESC) AS Sales_Rank
FROM orders;

#DENSE RANK
SELECT
    `Order ID`,
    `Customer ID`,
    Sales,
    DENSE_RANK() OVER (ORDER BY Sales DESC) AS 'Dense Rank'
FROM orders;

#PARTITION BY
SELECT
    `Customer ID`,
    `Order ID`,
    Sales,
    ROW_NUMBER() OVER (
        PARTITION BY `Customer ID`
        ORDER BY Sales DESC
    ) AS Order_Rank
FROM orders;

#JOIN + CTE + WINDOW FUNCTION
WITH CustomerSales AS (
    SELECT
        `Customer ID`,
        SUM(Sales) AS Total_Sales
    FROM orders
    GROUP BY `Customer ID`
)
SELECT
    c.`Customer Name`,
    cs.Total_Sales,
    RANK() OVER (ORDER BY cs.Total_Sales DESC) AS Customer_Rank
FROM customers c
JOIN CustomerSales cs
ON c.`Customer ID` = cs.`Customer ID`;

