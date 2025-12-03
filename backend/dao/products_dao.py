from db.sql_connection import get_sql_connection

# -------------------------------------------------------
# GET ALL PRODUCTS
# -------------------------------------------------------
def get_all_products(connection):

    cursor = connection.cursor()

    query = (
        """
        SELECT 
            p.product_id,
            p.name,
            p.uom_id,
            p.price_per_unit,
            u.uom_name
        FROM products p
        INNER JOIN uom u ON p.uom_id = u.uom_id
        ORDER BY p.product_id ASC
        """
    )

    cursor.execute(query)

    response = []
    for (product_id, name, uom_id, price_per_unit, uom_name) in cursor:
        response.append({
            "product_id": product_id,
            "name": name,
            "uom_id": uom_id,
            "price_per_unit": float(price_per_unit),
            "uom_name": uom_name
        })

    return response


# -------------------------------------------------------
# INSERT NEW PRODUCT
# -------------------------------------------------------
def insert_new_product(connection, product):
    cursor = connection.cursor()

    query = """
        INSERT INTO products (name, uom_id, price_per_unit)
        VALUES (%s, %s, %s)
    """

    data = (
        product["name"],
        int(product["uom_id"]),
        float(product["price_per_unit"])
    )

    cursor.execute(query, data)
    connection.commit()

    return cursor.lastrowid


# -------------------------------------------------------
# DELETE PRODUCT
# -------------------------------------------------------
def delete_product(connection, product_id):
    cursor = connection.cursor()

    # Delete product — order_details cleanup happens in app.py
    query = "DELETE FROM products WHERE product_id = %s"
    cursor.execute(query, (product_id,))

    connection.commit()
    return cursor.rowcount


# -------------------------------------------------------
# UPDATE PRODUCT
# -------------------------------------------------------
def update_product(connection, product):
    cursor = connection.cursor()

    query = """
        UPDATE products
        SET 
            name = %s,
            uom_id = %s,
            price_per_unit = %s
        WHERE product_id = %s
    """

    data = (
        product["name"],
        int(product["uom_id"]),
        float(product["price_per_unit"]),
        int(product["product_id"])
    )

    cursor.execute(query, data)
    connection.commit()

    return cursor.rowcount


# -------------------------------------------------------
# DEBUG RUN
# -------------------------------------------------------
if __name__ == "__main__":
    connection = get_sql_connection()

    # Test: get all
    # print(get_all_products(connection))

    # Test: insert
    # print(insert_new_product(connection, {
    #     "name": "Test Product",
    #     "uom_id": 1,
    #     "price_per_unit": 99.99
    # }))
