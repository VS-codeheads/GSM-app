from typing import List, Dict, Any
from datetime import datetime


def calculate_monthly_inventory_spend(orders: List[Dict[str, Any]], year: int, month: int) -> Dict[str, Any]:
    """
    Calculator in order to calculate the total money spent on inventory for a given month, breakdown by product catecory and highest cost driver category.

    Each order must contain date, quantity, cost and category.
    """

    # validate yesr and month
    if not isinstance(year, int) or not isinstance(month, int):
        raise ValueError("Year and month must be integers")
    
    if not (2000 <= year <= 2100):
        raise ValueError("Year must be between 2000 and 2100")
    
    if not (1 <= month <= 12):
        raise ValueError("Month must be in range 1-12")

    total_spend = 0
    category_totals = {}

    # process each order
    for order in orders:
        order_date: datetime = order.get("date")
        qty = order.get("qty", 0)
        cost = order.get("cost", 0)
        category = order.get("category", "Unknown")

        # validate date
        if not isinstance(order_date, datetime):
            raise ValueError("Each order must contain a valid datetime object for date")

        # Validate qty/cost
        if not isinstance(qty, (int, float)) or qty < 0:
            raise ValueError("qty must be a non-negative number")
        
        if not isinstance(cost, (int, float)) or cost < 0:
            raise ValueError("cost must be a non-negative number")

        # applying filter by year/month
        if order_date.year == year and order_date.month == month:
            spend = qty * cost
            total_spend += spend
            category_totals[category] = category_totals.get(category, 0) + spend
    
    # Determine highest cost driver
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