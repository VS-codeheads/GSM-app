from sql_connection import get_sql_connection
from datetime import datetime

def add_order(connection, order):
    cursor = connection.cursor()

    order_query = (
        "INSERT INTO orders (customer_name, total_price, datetime) "
        "VALUES (%s, %s, %s)"
    )

    order_data = (order["customer_name"], order["total_price"], order["datetime"])

    cursor.execute(order_query, order_data)

    order_id = cursor.lastrowid

    order_details_query = (
        "INSERT INTO order_details (order_id, product_id, quantity, total_price) "
        "VALUES (%s, %s, %s, %s)"
    )
    order_detail_data = []

    for order_detail_record in order["order_details"]:
        order_detail_data.append([
            order_id,
            int(order_detail_record["product_id"]),
            float(order_detail_record["quantity"]),
            float(order_detail_record["total_price"])
        ])

    connection.commit()

    return order_id



if __name__ == "__main__":
    connection = get_sql_connection()
    # Example usage:
    print(add_order(connection, {
        "customer_name": "Ida",
        "total_price": 250.0,
        "order_date": datetime.now(),
        "order_details": [
            {
                "product_id": 1, 
                "quantity": 2,
                "total_price": 60.0
             },
            {
                "product_id": 3, 
                "quantity": 10,
                "total_price": 30.0
            },
            {
                "product_id": 5, 
                "quantity": 1,
                "total_price": 100.0
             },
             {
                "product_id": 1, 
                "quantity": 2,
                "total_price": 60.0
             },
        ]
    }))