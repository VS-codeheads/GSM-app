def get_order_details(conn, order_id):
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT 
            o.order_id,
            o.customer_name,
            o.total_price,
            o.datetime,
            p.name AS product_name,
            p.uom_id,
            u.uom_name,
            od.quantity,
            od.total_price AS item_total
        FROM orders o
        JOIN order_details od ON o.order_id = od.order_id
        JOIN products p ON od.product_id = p.product_id
        JOIN uom u ON p.uom_id = u.uom_id
        WHERE o.order_id = %s
    """

    cursor.execute(query, (order_id,))
    rows = cursor.fetchall()
    return rows
