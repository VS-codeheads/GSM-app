import datetime

def get_all_orders(conn):
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT 
            o.order_id,
            o.customer_name,
            o.total_price,
            o.datetime
        FROM orders o
        ORDER BY o.datetime DESC
    """

    cursor.execute(query)
    result = cursor.fetchall()
        
    return result


def get_recent_orders(conn, limit=5):
    cursor = conn.cursor(dictionary=True)

    if not isinstance(limit, int) or limit < 0:
        raise ValueError("limit must be a non-negative integer")

    # NOTE: limit = 0 must be passed directly to SQL

    query = """
        SELECT 
            o.order_id,
            o.customer_name,
            o.total_price,
            o.datetime
        FROM orders o
        ORDER BY o.datetime DESC
        LIMIT %s
    """

    cursor.execute(query, (limit,))
    result = cursor.fetchall()

    return result