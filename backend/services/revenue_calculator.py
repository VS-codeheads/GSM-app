import random
from typing import List, Dict, Any
from collections import OrderedDict

def generate_random_sales(stock: int, mean: float = 5, std: float = 2) -> int:
    """
    Simulator for random daily sales
    """
    sales = max(0, int(random.gauss(mean, std)))
    return min(sales, stock)


def calculate_revenue_and_profit(
        products: List[Dict[str, Any]],
        days: int = 7,
        seed: int | None = None
) -> Dict[str, Any]:
    """
    Products must include name, quantity (stock), price_per_unit (buying price) and selling_price (sell price)
    """

    if seed is not None:
        random.seed(seed)

    total_revenue = 0
    total_cost = 0
    total_units_sold = 0
    details = []

    for p in products:
        stock = p["quantity"]
        buy_price = p["price_per_unit"]
        sell_price = p["selling_price"]
        name = p["name"]

        sold_total = 0

        for _ in range(days):
            sales_today = generate_random_sales(stock)
            sold_total += sales_today
            stock -= sales_today

        # financial calculations
        revenue = sold_total * sell_price
        cost = sold_total * buy_price
        profit = revenue - cost

        total_revenue += revenue
        total_cost += cost
        total_units_sold += sold_total

        details.append({
            "product": name,
            "sold_units": sold_total,
            "initial_stock": p["quantity"],
            "remaining_stock": stock,
            "revenue": revenue,
            "cost": cost,
            "profit": profit,
            "profit_margin_percent": round((profit / revenue * 100), 2) if revenue > 0 else 0,
        })

    total_profit = total_revenue - total_cost
    
    summary = OrderedDict([
        ("total_revenue", round(total_revenue, 2)),
        ("total_cost", round(total_cost, 2)),
        ("total_profit", round(total_profit, 2)),
        ("profit_margin_percent", round((total_profit / total_revenue * 100), 2) if total_revenue > 0 else 0),
        ("total_units_sold", total_units_sold)
    ])

    return OrderedDict([
        ("summary", summary),
        ("details", details)
    ])