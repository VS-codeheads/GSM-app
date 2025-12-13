from flask import Blueprint, request, jsonify
import mysql.connector
from datetime import datetime
from ..db.sql_connection import get_sql_connection

from ..services.revenue_calculator import calculate_revenue_and_profit
from ..services.inventory_spend import calculate_monthly_inventory_spend

calculations_bp = Blueprint("calculations", __name__)



# ---------------------------------------------------
# REVENUE + PROFIT SIMULATION ENDPOINT
# ---------------------------------------------------
@calculations_bp.route("/calc/revenue", methods=["POST"])
def revenue_endpoint():
    """
    Expected payload:
    {
        "product_ids": [1, 2, 3],
        "days": 7,
        "seed": 123   (optional)
    }
    """

    data = request.get_json() or {}


    # Validate product_ids
    product_ids = data.get("product_ids")
    if not isinstance(product_ids, list) or len(product_ids) == 0:
        return jsonify({"error": "'product_ids' must be a non-empty list"}), 400

    if not all(isinstance(x, int) and x > 0 for x in product_ids):
        return jsonify({"error": "'product_ids' must contain positive integers only"}), 400

    # Validate days
    days = data.get("days", 7)
    if not isinstance(days, int) or days < 1 or days > 365:
        return jsonify({"error": "'days' must be an integer between 1 and 365"}), 400


    # Validate seed
    seed = data.get("seed")
    if seed is not None:
        if not isinstance(seed, int) or seed < 0:
            return jsonify({"error": "'seed' must be a positive integer"}), 400


    # Fetch product data
    conn = get_sql_connection()
    cursor = conn.cursor(dictionary=True)

    placeholders = ",".join(["%s"] * len(product_ids))
    query = f"""
        SELECT 
            product_id,
            name,
            quantity,
            price_per_unit,
            selling_price
        FROM products
        WHERE product_id IN ({placeholders})
    """

    cursor.execute(query, product_ids)
    products = cursor.fetchall()

    cursor.close()
    conn.close()

    if not products:
        return jsonify({"error": "No matching products found"}), 400

    # Run calculation
    result = calculate_revenue_and_profit(products, days=days, seed=seed)

    return jsonify(result), 200


# ---------------------------------------------------
# MONTHLY INVENTORY SPEND ENDPOINT
# ---------------------------------------------------
@calculations_bp.route("/calc/spend", methods=["POST"])
def spend_endpoint():
    """
    {
        "year": 2025,
        "month": 1,
        "orders": [
            {"date": "2025-01-01", "qty": 5, "cost": 3.5, "category": "Fruit"}
        ]
    }
    """

    data = request.get_json() or {}

    year = data.get("year")
    month = data.get("month")

    # Validate year
    if not isinstance(year, int) or year < 2000 or year > 2100:
        return jsonify({"error": "'year' must be a valid integer (2000–2100)"}), 400

    # Validate month
    if not isinstance(month, int) or month < 1 or month > 12:
        return jsonify({"error": "'month' must be an integer between 1 and 12"}), 400

    # Validate orders list
    orders_raw = data.get("orders", [])
    if not isinstance(orders_raw, list):
        return jsonify({"error": "'orders' must be a list"}), 400

    orders = []
    for o in orders_raw:
        try:
            o["date"] = datetime.fromisoformat(o["date"])
            orders.append(o)
        except Exception:
            continue  # skip invalid date formats

    result = calculate_monthly_inventory_spend(orders, year, month)

    return jsonify(result), 200