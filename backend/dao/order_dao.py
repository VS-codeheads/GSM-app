from datetime import datetime

def add_order(connection, order):
    cursor = connection.cursor(dictionary=True)

    # -----------------------------------------------------
    # EDITING ORDER → RESTORE previous stock + delete items
    # -----------------------------------------------------
    if order.get("order_id"):
        order_id = int(order["order_id"])

        # Get previous items for quantity restore
        cursor.execute(
            "SELECT product_id, quantity FROM order_details WHERE order_id = %s",
            (order_id,)
        )
        old_items = cursor.fetchall()

        # Restore previous stock
        for item in old_items:
            cursor.execute(
                "UPDATE products SET quantity = quantity + %s WHERE product_id = %s",
                (item["quantity"], item["product_id"])
            )

        # Delete old order details
        cursor.execute("DELETE FROM order_details WHERE order_id = %s", (order_id,))

        # Update main order
        cursor.execute("""
            UPDATE orders
            SET customer_name=%s, total_price=%s, datetime=%s
            WHERE order_id=%s
        """, (
            order["customer_name"],
            float(order["total_price"]),
            datetime.now(),
            order_id
        ))

    else:
        # -----------------------------------------------------
        # NEW ORDER
        # -----------------------------------------------------
        cursor.execute("""
            INSERT INTO orders (customer_name, total_price, datetime)
            VALUES (%s, %s, %s)
        """, (
            order["customer_name"],
            float(order["total_price"]),
            datetime.now()
        ))
        order_id = cursor.lastrowid

    # -----------------------------------------------------
    # INSERT NEW ITEMS + REDUCE STOCK
    # -----------------------------------------------------
    for item in order["order_details"]:
        cursor.execute("""
            INSERT INTO order_details (order_id, product_id, quantity, total_price)
            VALUES (%s, %s, %s, %s)
        """, (
            order_id,
            int(item["product_id"]),
            float(item["quantity"]),
            float(item["total_price"])
        ))

        # Reduce stock
        cursor.execute("""
            UPDATE products
            SET quantity = quantity - %s
            WHERE product_id = %s
        """, (
            float(item["quantity"]),
            int(item["product_id"])
        ))

    connection.commit()
    return order_id
