from datetime import datetime

def add_order(connection, order):
    """
    Creates or updates an order.
    If order contains 'order_id' (truthy) -> treat as update:
      - delete existing order_details for that order_id
      - update orders row
      - insert new order_details
    Otherwise create new order + details.
    Returns order_id.
    """
    cursor = connection.cursor()

    # Validate required fields
    if "customer_name" not in order or "order_details" not in order:
        raise ValueError("order must contain customer_name and order_details")

    if "order_id" in order and order.get("order_id"):
        # Edit path
        order_id = int(order["order_id"])

        # Delete previous details
        cursor.execute("DELETE FROM order_details WHERE order_id = %s", (order_id,))

        # Update orders table
        cursor.execute("""
            UPDATE orders
            SET customer_name = %s, total_price = %s, datetime = %s
            WHERE order_id = %s
        """, (order["customer_name"], float(order["total_price"]), datetime.now(), order_id))

    else:
        # Create new order
        order_query = """
            INSERT INTO orders (customer_name, total_price, datetime)
            VALUES (%s, %s, %s)
        """
        order_data = (
            order["customer_name"],
            float(order["total_price"]),
            datetime.now()
        )
        cursor.execute(order_query, order_data)
        order_id = cursor.lastrowid

    # Insert details
    detail_rows = []
    for item in order["order_details"]:
        # Per-item validation
        if "product_id" not in item or "quantity" not in item or "total_price" not in item:
            raise ValueError("Each order_details item needs product_id, quantity and total_price")

        detail_rows.append((
            order_id,
            int(item["product_id"]),
            float(item["quantity"]),
            float(item["total_price"])
        ))

    if detail_rows:
        query = """
            INSERT INTO order_details (order_id, product_id, quantity, total_price)
            VALUES (%s, %s, %s, %s)
        """
        cursor.executemany(query, detail_rows)

    connection.commit()

    return order_id
