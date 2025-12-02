from datetime import datetime
from db.sql_connection import get_sql_connection

def add_order(connection, order):
    cursor = connection.cursor()

    # Insert into orders
    order_query = """
        INSERT INTO orders (customer_name, total_price, datetime)
        VALUES (%s, %s, %s)
    """
    order_data = (
        order["customer_name"],
        float(order["grand_total"]),
        datetime.now()
    )

    cursor.execute(order_query, order_data)
    order_id = cursor.lastrowid

    # Insert into order_details
    order_details_query = """
        INSERT INTO order_details (order_id, product_id, quantity, total_price)
        VALUES (%s, %s, %s, %s)
    """

    detail_rows = []
    for item in order["order_details"]:
        detail_rows.append((
            order_id,
            int(item["product_id"]),
            float(item["quantity"]),
            float(item["total_price"])
        ))

    cursor.executemany(order_details_query, detail_rows)

    connection.commit()
    return order_id
