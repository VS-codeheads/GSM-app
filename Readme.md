# Grocery Store Manager (GSM) — Setup Guide

This README explains how to fully set up the database, backend, and frontend of the Grocery Store Manager web application so that the project runs identically on another machine.

## Requirements

Before starting, install:

* Python 3.10+

* MySQL Server 8+

* MySQL Workbench (optional, for visual inspection)

* pip (Python package manager)


## Install Python Environment

Inside the project folder:

```bash
python3 -m venv venv
source venv/bin/activate     # macOS / Linux
venv\Scripts\activate        # Windows
```

Install required packages:
```bash
pip install -r requirements.txt
```

## Project structure

```sql
GSM-app/
│
├── backend/
│   ├── app.py
│   ├── db/
│   │   └── sql_connection.py
│   ├── dao/
│   │   ├── products_dao.py
│   │   ├── order_dao.py
│   │   ├── order_list_dao.py
│   │   ├── order_details_dao.py
│   │   └── revenue_dao.py
│   ├── requirements.txt
│   ├── sql_scripts
│   │   ├── create.sql
│   │   └── seed_tables.sql
│
└── UI/
    ├── index.html
    ├── order.html
    ├── manage-product.html
    ├── css/
    ├── js/
    └── ...
```

## Configure MySQL Access

The database initializer uses these default settings:
```yaml
host: localhost
user: root
password: (empty)
port: 3306
database: grocery_store
```

If your MySQL user has a password, update this file:
```bash
backend/db/initialize_sql.py
```

Modify:
```python
MYSQL_USER = "root"
MYSQL_PASS = ""
```

## Initialize + Seed the Database (Automatic)

Your project includes a full database initializer:
```bash
backend/db/initialize_sql.py
```

This script will:

* Create database grocery_store
* Create all tables
* Reset all tables safely
* Insert UOMs
* Insert example products
* Insert example orders & order details

Run it:
```bash
python backend/db/initialize_sql.py
```

You should see output like:

* Connected to MySQL
* Database ready
* Tables created
* All tables cleared and counters reset
* UOMs inserted
* Products inserted
* Sample orders inserted

If you see and error, it will explain the exact issue.


##Run the Backend (Flask API)

From the project root:
```bash
python backend/app.py
```

Server starts at:

* http://localhost:5000


You should see:
```nginx
Starting Flask API on http://localhost:5000
```


## Run the Frontend

No build tools required — just open:
```bash
UI/index.html
```

or if the folder is named differently:
```bash
frontend/index.html
```

Make sure the browser is allowed to load local JS files.


## API Endpoints

Products

| Method | Endpoint              | Description           |
| ------ | --------------------- | --------------------- |
| GET    | `/getProducts`        | List all products     |
| POST   | `/addProduct`         | Add new product       |
| POST   | `/updateProduct`      | Update a product      |
| DELETE | `/deleteProduct/<id>` | Delete a product      |
| GET    | `/getUOM`             | List units of measure |

Orders

| Method | Endpoint                | Description            |
| ------ | ----------------------- | ---------------------- |
| GET    | `/getOrders`            | List all orders        |
| GET    | `/getOrder/<id>`        | Single order + items   |
| GET    | `/getOrderDetails/<id>` | Order item breakdown   |
| POST   | `/addOrder`             | Create or update order |
| DELETE | `/deleteOrder/<id>`     | Remove an order        |


## Weather Widget (External API)

In dashboard.js, replace:
```js
const API_KEY = "YOUR_API_KEY_HERE";
```

with your OpenWeather key.

Get one free from:

* https://openweathermap.org/api


## Testing Instructions (Not done)

### Black-box test scenarios

(username, product flow, order flow)

### Postman API collection

All endpoints can be tested with GET/POST/DELETE.

### Selenium E2E UI tests

Recommended:

Open dashboard

Create order

Edit order

Delete order

Add product

Edit product

Delete product

### JMeter performance test

Test GET /getOrders under load (50–200 users)