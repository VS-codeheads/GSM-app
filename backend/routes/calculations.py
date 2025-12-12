from flask import Blueprint, request, jsonify
import mysql.connector
from datetime import datetime
from db.sql_connection import get_sql_connection

from services.revenue_calculator import calculate_revenue_and_profit
from services.inventory_spend import calculate_monthly_inventory_spend

calculations_bp = Blueprint("calculations", __name__)


# ---------------------------------------------------
# REVENUE + PROFIT SIMULATION ENDPOINT
# ---------------------------------------------------

@calculations_bp.route("/calc/revenue", methods=["POST"])
def revenue_endpoint():
    """
        {
        "product_ids": [1, 2, 3],
        "days": 7,
        "seed": 123    (optional)
    }
    """

    data = request.get_json()
    product_ids = data.get("product_ids", [])
    days = data.get("days", 7)
    seed = data.get("seed")

    if not product_ids:
        return jsonify({"error": "products_ids if required"}), 400
    

    # Connect to MySQL
    conn = get_sql_connection()
    cursor = conn.cursor(dictionary=True)

    # Fetch product details from DB
    format_strings = ",".join(["%s"] * len(product_ids))
    query = f"""
        SELECT 
            product_id,
            name,
            quantity,
            price_per_unit,
            selling_price
        FROM products
        WHERE product_id IN ({format_strings})
    """
    cursor.execute(query, product_ids)
    products = cursor.fetchall()

    cursor.close()
    conn.close()

    # run calculation using the real DB data
    result = calculate_revenue_and_profit(products, days=days, seed=seed)

    return jsonify(result)


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
        OR provides no orders -> fetch from DB later
    }
    """

    data = request.get_json()

    orders_raw = data.get("orders", [])
    year = data.get("year")
    month = data.get("month")

    orders = []
    for o in orders_raw:
        try:
            o["date"] = datetime.fromisoformat(o["date"])
        except ValueError:
            continue
        orders.append(o)

    # calculate the monthly spend
    result = calculate_monthly_inventory_spend(orders, year, month)

    return jsonify(result), 200    

