"""
Creates the grocery_store database, tables, and seeds initial data.
"""

import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

load_dotenv()

# -----------------------------------
# CONFIGURE CONNECTION
# -----------------------------------
MYSQL_CONFIG = {
    "host": os.getenv("MYSQL_HOST", "localhost"),
    "user": os.getenv("MYSQL_USER", "root"),
    "password": os.getenv("MYSQL_PASSWORD"),
    "port": int(os.getenv("MYSQL_PORT", 3306))
}


# -----------------------------------
# SEED DATA
# -----------------------------------
UOMS = [
    ("kg",),
    ("each",),
    ("litre",)
]

PRODUCTS = [
    ("Apple", 1, 1.50, 3.00, 100),
    ("Orange", 1, 3.00, 6.00, 80),
    ("Toothpaste", 2, 10.00, 20.00, 40),
    ("Milk", 3, 6.00, 12.00, 50)
]

ORDERS = [
    ("Børge Nielsen", 90.00, "2025-01-01 10:00:00"),
    ("Sine Olafson", 45.00, "2025-01-02 14:30:00")
]

ORDER_DETAILS = [
    # Order 1
    (1, 1, 10, 30.00),   # Apples → 10 × 3 = 30
    (1, 2, 10, 60.00),   # Oranges → 10 × 6 = 60

    # Order 2
    (2, 3, 1, 20.00),    # Toothpaste → 1 × 20 = 20
    (2, 4, 2, 24.00)     # Milk → 2 × 12 = 24
]


# -----------------------------------
# MAIN SCRIPT
# -----------------------------------
def main():
    print("Connecting to MySQL...")

    conn = None
    cursor = None
    
    try:
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        cursor = conn.cursor()
        print("Connected to MySQL")

        # -----------------------------------
        # Create database
        # -----------------------------------
        print("Ensuring database `grocery_store` exists...")
        cursor.execute("CREATE DATABASE IF NOT EXISTS grocery_store")
        cursor.execute("USE grocery_store")
        print("Database ready\n")

        # -----------------------------------
        # Create tables
        # -----------------------------------
        print("Creating tables...")

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS uom (
                uom_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                uom_name VARCHAR(45) NOT NULL
            );
        """)
        print("Table `uom` ready")

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                product_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                uom_id INT NOT NULL,
                price_per_unit DOUBLE NOT NULL,
                selling_price DOUBLE NOT NULL DEFAULT 0,
                quantity INT NOT NULL DEFAULT 0,
                FOREIGN KEY (uom_id) REFERENCES uom(uom_id)
            );
        """)
        print("Table `products` ready")

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                order_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                customer_name VARCHAR(100),
                total_price DOUBLE NOT NULL,
                datetime DATETIME NOT NULL
            );
        """)
        print("Table `orders` ready")

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS order_details (
                id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                order_id INT NOT NULL,
                product_id INT NOT NULL,
                quantity DOUBLE NOT NULL,
                total_price DOUBLE NOT NULL,
                FOREIGN KEY (order_id) REFERENCES orders(order_id),
                FOREIGN KEY (product_id) REFERENCES products(product_id)
            );
        """)
        print("Table `order_details` ready\n")

        conn.commit()

        # -----------------------------------
        # CLEAR existing data (reset)
        # -----------------------------------
        print("Resetting tables (safe)...")

        cursor.execute("DELETE FROM order_details")
        cursor.execute("DELETE FROM orders")
        cursor.execute("DELETE FROM products")
        cursor.execute("DELETE FROM uom")
        conn.commit()

        # RESET AUTO_INCREMENT
        cursor.execute("ALTER TABLE uom AUTO_INCREMENT = 1")
        cursor.execute("ALTER TABLE products AUTO_INCREMENT = 1")
        cursor.execute("ALTER TABLE orders AUTO_INCREMENT = 1")
        cursor.execute("ALTER TABLE order_details AUTO_INCREMENT = 1")
        conn.commit()

        print("All tables cleared and counters reset\n")


        # -----------------------------------
        # SEED UOMs
        # -----------------------------------
        print("Seeding UOMs...")
        cursor.executemany("INSERT INTO uom (uom_name) VALUES (%s)", UOMS)
        conn.commit()
        print("UOMs inserted")

        # -----------------------------------
        # SEED Products
        # -----------------------------------
        print("Seeding products...")
        cursor.executemany("""
            INSERT INTO products (name, uom_id, price_per_unit, selling_price, quantity)
            VALUES (%s, %s, %s, %s, %s)
        """, PRODUCTS)
        conn.commit()
        print("Products inserted")

        # -----------------------------------
        # SEED Orders
        # -----------------------------------
        print("Seeding orders...")
        cursor.executemany("""
            INSERT INTO orders (customer_name, total_price, datetime)
            VALUES (%s, %s, %s)
        """, ORDERS)
        conn.commit()
        print("Orders inserted")

        # -----------------------------------
        # SEED Order Details
        # -----------------------------------
        print("Seeding order details...")
        cursor.executemany("""
            INSERT INTO order_details (order_id, product_id, quantity, total_price)
            VALUES (%s, %s, %s, %s)
        """, ORDER_DETAILS)
        conn.commit()
        print("Order details inserted")

        print("\n🎉 DATABASE INITIALIZATION COMPLETE — everything is ready!")

    except Error as e:
        print("\n❌ ERROR initializing database:")
        print(e)

    finally:
        if conn is not None and conn.is_connected():
            cursor.close()
            conn.close()
            print("✔ MySQL connection closed")


if __name__ == "__main__":
    main()
