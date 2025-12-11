# Grocery Store Manager (GSM) — Setup Guide

This README explains how to fully set up the database, backend, and frontend of the Grocery Store Manager web application so that the project runs identically on another machine.

## Requirements

Before starting, install:

*Backend*  :

* Python 3.10–3.12

* pip

* virtualenv 

*Database*:

* MySQL 8.x 

*Frontend*:

* Any browser

* VS Code 

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

## Project structure

Create the database on your local MySQL Workbench

1. Create the database and the required tables

Use the create script in the sql_scripts folder.

2. Seed the tables 

Use the sample data from seed script in the swl_scripts folder.

Or 

Run the seed script using:
```bash
mysql -u root -p grocery_store < backend/seed.sql
```

## Configure Backend SQL Connection

Open:
```bash
backend/db/sql_connection.py
```

Remember to update your credentials:
```bash
import mysql.connector

def get_sql_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="YOUR_PASSWORD_HERE",
        database="grocery_store"
    )
```

## Backend Setup & Run

*Step 1 — Create venv*
```bash
cd backend
python3 -m venv venv
source venv/bin/activate   # macOS/Linux
venv\Scripts\activate      # Windows
```

*Step 2 — Install requirements*
```bash
backend/requirements.txt
```

with:
```bash
flask
flask-cors
mysql-connector-python
```

Then run:
```bash
pip install -r requirements.txt
```

*Step 3 — Start the API server*
```bash
python app.py
```

*The API will now run at:*

* http://localhost:5000


## Frontend Setup & Run

The UI folder is static HTML/JS.

To run it locally, open an HTML page directly or run a lightweight server:

Option 1 - Double click index.html

* Works but JS imports may restrict CORS on some browsers.

Option 2 — Run local HTTP server 

Inside UI folder:
```bash
python3 -m http.server 8000
```

Open:

* http://localhost:8000/index.html


## Testing checklist

After setup, you should test:

* Product management

    * Add product

    * Edit product

    * Delete product

    * Quantity updates

* Order management

    * Create order

    * Edit order

    * Delete order

    * View order details

* External API

    * Weather widget loads

* Revenue analytics

    * Total revenue

    * Date range revenue

    * Revenue by product


## Common Issues & Fixes
* “Failed to load products/orders”

Backend not running → Start with
```bash
python app.py
```

* Wrong MySQL password

Update file:

```bash
backend/db/sql_connection.py
```

* CORS issues

You already enabled:
```python
CORS(app)
```

So shouldn’t be a problem.

* 404 on delete/edit

Usually caused by:

    * Wrong URL

    * Backend not restarted after changes