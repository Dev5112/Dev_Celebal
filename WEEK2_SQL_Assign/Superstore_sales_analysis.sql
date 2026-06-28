CREATE DATABASE superstore;
USE superstore;
SELECT * FROM superstore_data
LIMIT 10;

#total rows
SELECT COUNT(*) AS total_rows
FROM superstore_data;

DESCRIBE superstore_data;

#total sales by region 
SELECT Region,
SUM(Sales) AS Total_Sales
FROM superstore_data
GROUP BY Region
ORDER BY Total_Sales DESC;

#Sales in West Region
SELECT *
FROM superstore_data
WHERE Region = 'West';

#total sales by category
SELECT Category,
SUM(Sales) AS Total_Sales
FROM superstore_data
GROUP BY Category
ORDER BY Total_Sales DESC;

#Furniture Category
SELECT *
FROM superstore_data
WHERE Category = 'Furniture';

#average sales by category
SELECT Category,
AVG(Sales) AS Average_Sales
FROM superstore_data
GROUP BY Category;

#Sales greater than 500
SELECT *
FROM superstore_data
WHERE Sales > 500;

#top 10 products
SELECT `Product Name`,
SUM(Sales) AS Total_Sales
FROM superstore_data
GROUP BY `Product Name`
ORDER BY Total_Sales DESC
LIMIT 10;

#top 10 customers
SELECT `Customer Name`,
SUM(Sales) AS Total_Sales
FROM superstore_data
GROUP BY `Customer Name`
ORDER BY Total_Sales DESC
LIMIT 10;

#orders from 2016
SELECT *
FROM superstore_data
WHERE STR_TO_DATE(`Order Date`, '%m/%d/%Y')
BETWEEN '2016-01-01' AND '2016-12-31';

#monthly sales
SELECT
YEAR(`Order Date`) AS Year,
MONTH(`Order Date`) AS Month,
SUM(Sales) AS Total_Sales
FROM superstore_data
GROUP BY Year, Month
ORDER BY Year, Month;

#quantity sold by category
SELECT Category,
SUM(Quantity) AS Total_Quantity
FROM superstore_data
GROUP BY Category;

#duplicate order id's
SELECT `Order ID`,
COUNT(*) AS Duplicate_Count
FROM superstore_data
GROUP BY `Order ID`
HAVING COUNT(*) > 1;

#null customer names
SELECT *
FROM superstore_data
WHERE Customer_Name IS NULL;

#total number of records
SELECT COUNT(*) AS Total_Rows
FROM superstore_data;

SHOW TABLES;
DESCRIBE superstore_data;
