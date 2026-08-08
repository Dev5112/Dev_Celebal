# Data Dictionary

## Table: customers
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| customer_id | INT | PK, > 0 | Unique customer identifier |
| customer_name | TEXT | NOT NULL | Customer full name (Title Case) |
| email | TEXT | UNIQUE | Validated email address format |
| registration_date | DATETIME | NOT NULL | Date and time of registration |
| customer_type | TEXT | IN (REGULAR, PREMIUM, VIP) | Loyalty segmentation |

## Table: products
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| product_id | INT | PK, > 0 | Unique product identifier |
| product_name | TEXT | NOT NULL | Cleaned product description |
| category | TEXT | NOT NULL | Main product classification |
| subcategory | TEXT | NOT NULL | Secondary classification |
| cost_price | DECIMAL | > 0 | Unit cost to business |

## Table: orders
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| order_id | INT | PK, > 0 | Unique order identifier |
| customer_id | INT | FK to customers | Who placed the order |
| order_date | DATETIME | <= NOW() | Date the order was placed |
| status | TEXT | NOT NULL | Order status tracking |
| region_code | TEXT | NOT NULL | Geographic region mapping |

## Table: order_items
| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| item_id | INT | PK, > 0 | Unique line item identifier |
| order_id | INT | FK to orders | Associated order |
| product_id | INT | FK to products | Product purchased |
| quantity | INT | > 0 | Number of units purchased |
| unit_price | DECIMAL | > 0 | Selling price per unit |
| discount_percent | DECIMAL | 0-100 | Percentage discount applied |
