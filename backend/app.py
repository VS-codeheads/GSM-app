from flask import Flask, jsonify, request
from flask_cors import CORS
import json

from .dao.products_dao import get_all_products, insert_new_product, update_product, delete_product
from .dao.uom_dao import get_all_uoms
from .dao.order_dao import add_order
from .dao.order_list_dao import get_all_orders, get_recent_orders
from .dao.order_details_dao import get_order_details
from .db.sql_connection import get_sql_connection
from .routes.calculations import calculations_bp

# -------------------------------------------------------
# Flask App Setup
# -------------------------------------------------------
app = Flask(__name__)

CORS(
    app,
    supports_credentials=True,
    resources={
        r"/*": {
            "origins": [
                "http://localhost:8000",
                "http://127.0.0.1:8000"
            ]
        }
    }
)

app.register_blueprint(calculations_bp, url_prefix="/api")


# -------------------------------------------------------
# Helpers
# -------------------------------------------------------
def connection():
    """Return a new SQL connection."""
    return get_sql_connection()


def parse_incoming_json():
    """
    Handles:
      - raw JSON body
      - form-data with 'data' key containing JSON

    Returns dict or None.
    """
    # JSON body
    body = request.get_json(silent=True)
    if body:
        return body

    # Form fallback
    raw_data = request.form.get("data")
    if raw_data:
        try:
            return json.loads(raw_data)
        except Exception:
            return None

    return None


# -------------------------------------------------------
# PRODUCTS
# -------------------------------------------------------
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

    required = ["name", "uom_id", "price_per_unit", "quantity"]
    if not all(k in product for k in required):
        return jsonify({"error": "Missing required fields"}), 400

    conn = connection()
    new_id = insert_new_product(conn, product)
    conn.close()
    return jsonify({"product_id": new_id}), 200

@app.route("/deleteProduct/<int:product_id>", methods=["DELETE"])
def api_delete_product(product_id):
    conn = connection()
    try:
        delete_product(conn, product_id)
    except Exception as e:
        conn.close()
        return jsonify({"error": "Failed to delete product", "detail": str(e)}), 500

    conn.close()
    return jsonify({"deleted": product_id}), 200

@app.route("/updateProduct", methods=["POST"])
def api_update_product():
    product = parse_incoming_json()
    if not product:
        return jsonify({"error": "Invalid JSON"}), 400

    required = ["name", "uom_id", "price_per_unit", "quantity", "product_id"]
    if not all(k in product for k in required):
        return jsonify({"error": "Missing required fields"}), 400

    conn = connection()
    try:
        update_product(conn, product)
    except Exception as e:
        conn.close()
        return jsonify({"error": "Failed to update product", "detail": str(e)}), 500

    conn.close()
    return jsonify({"updated": True}), 200


# -------------------------------------------------------
# UOM
# -------------------------------------------------------
@app.route("/getUOM", methods=["GET"])
def api_get_uom():
    conn = connection()
    uoms = get_all_uoms(conn)
    conn.close()
    return jsonify(uoms)


# -------------------------------------------------------
# ORDERS
# -------------------------------------------------------
@app.route("/addOrder", methods=["POST"])
def api_add_order():
    order_json = parse_incoming_json()
    if not order_json:
        return jsonify({"error": "Missing or invalid JSON"}), 400

    # Validation
    if "customer_name" not in order_json or "order_details" not in order_json:
        return jsonify({"error": "Missing required fields"}), 400

    conn = connection()
    try:
        order_id = add_order(conn, order_json)
    except Exception as e:
        app.logger.exception("Failed to add order")
        conn.close()
        return jsonify({"error": "Failed to add order", "detail": str(e)}), 500

    conn.close()
    return jsonify({"order_id": order_id}), 200


@app.route("/getOrders", methods=["GET"])
def api_get_orders():
    conn = connection()
    orders = get_all_orders(conn)
    conn.close()
    return jsonify(orders)


@app.route("/getRecentOrders", methods=["GET"])
def api_get_recent_orders():
    conn = connection()
    orders = get_recent_orders(conn, limit=5)
    conn.close()
    return jsonify(orders)


@app.route("/getOrder/<int:order_id>", methods=["GET"])
def api_get_order(order_id):
    conn = connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM orders WHERE order_id = %s", (order_id,))
    order = cursor.fetchone()
    if not order:
        conn.close()
        return jsonify({"error": "Order not found"}), 404

    cursor.execute(
        """
        SELECT od.order_id, od.product_id, od.quantity, od.total_price AS item_total,
               p.name AS product_name, u.uom_name
        FROM order_details od
        JOIN products p ON od.product_id = p.product_id
        JOIN uom u ON p.uom_id = u.uom_id
        WHERE od.order_id = %s
        """,
        (order_id,)
    )

    order["items"] = cursor.fetchall()
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


# -------------------------------------------------------
# SERVER
# -------------------------------------------------------
if __name__ == "__main__":
    print("Starting Flask API on http://localhost:5050")
    app.run(host="0.0.0.0", port=5050, debug=False)
