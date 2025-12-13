from ..db.sql_connection import get_sql_connection

def get_all_uoms(connection):
    
    cursor = connection.cursor()

    query = "SELECT uom_id, uom_name FROM uom"

    cursor.execute(query)

    response = []

    for (uom_id, uom_name) in cursor:
        response.append({
            "uom_id": uom_id,
            "uom_name": uom_name
        }
        )

    return response

if __name__ == "__main__":
    connection = get_sql_connection()
    print(get_all_uoms(connection))

