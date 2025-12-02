from flask import Flask, jsonify, request
from flask_cors import CORS
import json

from dao.products_dao import get_all_products, insert_new_product, delete_product
from dao.uom_dao import get_all_uoms
from dao.order_dao import add_order
from db.sql_connection import get_sql_connection

app = Flask(__name__)
CORS(app)  # Enables cross-origin API access

# Always create a fresh connection per request
def connection():
    return get_sql_connection()


# -----------------------
#       PRODUCTS
# -----------------------

@app.route("/getProducts", methods=["GET"])
def api_get_products():
    conn = connection()
    products = get_all_products(conn)
    return jsonify(products)


@app.route("/addProduct", methods=["POST"])
def api_add_product():
    """
    UI sends form-data containing:
    data: JSON-string
    """
    raw_data = request.form.get("data")
    if not raw_data:
        return jsonify({"error": "Missing 'data' in form payload"}), 400

    product = json.loads(raw_data)
    conn = connection()
    new_id = insert_new_product(conn, product)

    return jsonify({"product_id": new_id})


@app.route("/deleteProduct/<int:product_id>", methods=["DELETE"])
def api_delete_product(product_id):
    conn = connection()
    deleted = delete_product(conn, product_id)
    return jsonify({"deleted": deleted})


# -----------------------
#         UOM
# -----------------------

@app.route("/getUOM", methods=["GET"])
def api_get_uom():
    conn = connection()
    uoms = get_all_uoms(conn)
    return jsonify(uoms)


# -----------------------
#        ORDERS
# -----------------------

@app.route("/addOrder", methods=["POST"])
def api_add_order():
    """
    UI sends:
    data: JSON-string:
    {
      "customer_name": "...",
      "total_price": ...,
      "datetime": "...",
      "order_details": [
         {"product_id":..., "quantity":..., "total_price":...},
         ...
      ]
    }
    """
    raw = request.form.get("data")
    if not raw:
        return jsonify({"error": "Missing 'data'"}), 400

    order_json = json.loads(raw)
    conn = connection()
    order_id = add_order(conn, order_json)

    return jsonify({"order_id": order_id})


# -----------------------
#        SERVER
# -----------------------

if __name__ == "__main__":
    print("Starting Flask API on http://localhost:5000")
    app.run(debug=True, port=5000)