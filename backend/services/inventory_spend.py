from typing import List, Dict, Any
from datetime import datetime


def calculate_monthly_inventory_spend(orders: List[Dict[str, Any]], year: int, month: int) -> Dict[str, Any]:
    """
    Calculator in order to calculate the total money spent on inventory for a given month, breakdown by product catecory and highest cost driver category.

    Each order must contain date, quantity, cost and category.
    """

    total_spend = 0
    category_totals = {}

    for order in orders:
        order_date: datetime = order.get("date")
        qty = order.get("qty", 0)
        cost = order.get("cost", 0)
        category = order.get("category", "Unknown")

        if not isinstance(order_date, datetime):
            continue  # ignoring invalid input

        if order_date.year == year and order_date.month == month:
            spend = qty * cost
            total_spend += spend
            category_totals[category] = category_totals.get(category, 0) + spend

    highest_cost_driver = (
        max(category_totals.items(), key=lambda x: x[1])
        if category_totals
        else None
    )

    return {
        "total_spend": total_spend,
        "category_breakdown": category_totals,
        "highest_cost_driver": highest_cost_driver
    }