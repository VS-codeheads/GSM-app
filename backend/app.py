from flask import Flask, jsonify, request
from flask_cors import CORS
import json

from dao.products_dao import get_all_products, insert_new_product, delete_product, update_product
from dao.uom_dao import get_all_uoms
from dao.order_dao import add_order
from dao.order_list_dao import get_all_orders, get_recent_orders
from dao.order_details_dao import get_order_details
from db.sql_connection import get_sql_connection
from routes.calculations import calculations_bp

app = Flask(__name__)

CORS(
    app,
    supports_credentials=True,
    resources={r"/*": {"origins": ["http://localhost:8000", "http://127.0.0.1:8000"]}}
)

app.register_blueprint(calculations_bp, url_prefix="/api")


def connection():
    return get_sql_connection()

def parse_incoming_json():
    """
    Accept either:
      - form-encoded with key 'data' (stringified JSON)
      - raw JSON body
    Returns dict or None
    """
    # Try form first (legacy UI)
    raw_data = request.form.get("data")
    if raw_data:
        try:
            return json.loads(raw_data)
        except Exception:
            return None

    # Try JSON body
    try:
        body = request.get_json(silent=True)
        if body:
            return body
    except Exception:
        return None

    return None

# -----------------------
#       PRODUCTS
# -----------------------
@app.route("/getProducts", methods=["GET"])
def api_get_products():
    conn = connection()
    products = get_all_products(conn)
    conn.close()
    return jsonify(products)


@app.route("/addProduct", methods=["POST"])
def api_add_product():
    product = parse_incoming_json()
    if not product:
        return jsonify({"error": "Invalid JSON"}), 400

    conn = connection()
    new_id = insert_new_product(conn, product)
    conn.close()
    return jsonify({"product_id": new_id})


@app.route("/deleteProduct/<int:product_id>", methods=["DELETE"])
def api_delete_product(product_id):
    conn = connection()
    cursor = conn.cursor()

    # First delete rows referencing the product
    cursor.execute("DELETE FROM order_details WHERE product_id = %s", (product_id,))

    # Then delete the product
    cursor.execute("DELETE FROM products WHERE product_id = %s", (product_id,))

    conn.commit()
    conn.close()
    return jsonify({"deleted": product_id})


@app.route("/updateProduct", methods=["POST"])
def api_update_product():
    raw = request.form.get("data")
    if not raw:
        return jsonify({"error": "Missing data"}), 400

    product = json.loads(raw)
    conn = connection()
    conn.close()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE products
        SET name=%s, uom_id=%s, price_per_unit=%s, quantity=%s
        WHERE product_id=%s
    """, (
        product["name"],
        product["uom_id"],
        product["price_per_unit"],
        product["quantity"],
        product["product_id"]
    ))

    conn.commit()
    conn.close()
    return jsonify({"updated": True})


# -----------------------
#         UOM
# -----------------------
@app.route("/getUOM", methods=["GET"])
def api_get_uom():
    conn = connection()
    uoms = get_all_uoms(conn)
    conn.close()
    return jsonify(uoms)


# -----------------------
#        ORDERS
# -----------------------
@app.route("/addOrder", methods=["POST"])
def api_add_order():
    """
    Accepts form 'data' (JSON-string) OR raw JSON body.
    Payload shape:
    {
      "order_id": optional (for editing),
      "customer_name": "...",
      "total_price": ...,
      "datetime": "...",
      "order_details": [
         {"product_id":..., "quantity":..., "total_price":...},
         ...
      ]
    }
    """
    order_json = parse_incoming_json()
    if not order_json:
        return jsonify({"error": "Missing or invalid 'data'"}), 400

    # adding basic validation
    if "customer_name" not in order_json or "order_details" not in order_json:
        return jsonify({"error": "Missing required fields"}), 400

    conn = connection()
    try:
        order_id = add_order(conn, order_json)
    except Exception as e:
        # Debug info while developing
        app.logger.exception("Failed to add order")
        return jsonify({"error": "Failed to add order", "detail": str(e)}), 500

    conn.close()
    return jsonify({"order_id": order_id})


@app.route("/getOrders", methods=["GET"])
def api_get_orders():
    conn = connection()
    orders = get_all_orders(conn)
    conn.close()
    return jsonify(orders)


@app.route("/getRecentOrders", methods=["GET"])
def api_get_recent_orders():
    conn = connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT order_id, customer_name, total_price, datetime
        FROM orders
        ORDER BY datetime DESC
        LIMIT 5
    """)

    orders = cursor.fetchall()
    conn.close()
    return jsonify(orders)


@app.route("/getOrder/<int:order_id>", methods=["GET"])
def api_get_order(order_id):
    conn = connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM orders WHERE order_id = %s", (order_id,))
    order = cursor.fetchone()
    if not order:
        return jsonify({"error": "Order not found"}), 404

    cursor.execute("""
        SELECT od.order_id, od.product_id, od.quantity, od.total_price AS item_total,
               p.name AS product_name, u.uom_name
        FROM order_details od
        JOIN products p ON od.product_id = p.product_id
        JOIN uom u ON p.uom_id = u.uom_id
        WHERE od.order_id = %s
    """, (order_id,))

    items = cursor.fetchall()
    order["items"] = items
    conn.close()
    return jsonify(order)


@app.route("/getOrderDetails/<int:order_id>", methods=["GET"])
def api_order_details(order_id):
    conn = connection()
    details = get_order_details(conn, order_id)
    conn.close()
    return jsonify(details)


@app.route("/deleteOrder/<int:order_id>", methods=["DELETE"])
def api_delete_order(order_id):
    conn = connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM order_details WHERE order_id = %s", (order_id,))
    cursor.execute("DELETE FROM orders WHERE order_id = %s", (order_id,))
    conn.commit()
    conn.close()
    return jsonify({"deleted": order_id})


# -----------------------
#        SERVER
# -----------------------
if __name__ == "__main__":
    print("Starting Flask API on http://localhost:5000")
    app.run(debug=True, port=5000)
