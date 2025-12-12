import pytest
from datetime import datetime
from backend.services.inventory_spend import calculate_monthly_inventory_spend


# ------------------------------------------------------
# Helper that builds a valid order dictionary
# ------------------------------------------------------
def make_order(date, qty, cost, category="General"):
    return {"date": date, "qty": qty, "cost": cost, "category": category}


# ------------------------------------------------------
# EP + BVA: Valid year/month
# ------------------------------------------------------

@pytest.mark.parametrize("year, month", [
    (2025, 1),   # normal valid case
    (2000, 12),  # boundary min year
    (2100, 1),  # boundary max year
])
def test_valid_year_month(year, month):
    orders = [make_order(datetime(year, month, 1), 1, 10)]
    result = calculate_monthly_inventory_spend(orders, year, month)
    assert result["total_spend"] == 10


# ------------------------------------------------------
# EP: Invalid year/month = ValueError
# ------------------------------------------------------

@pytest.mark.parametrize("year, month", [
    ("2025", 1),    # non-integer year
    (2025, "1"),    # non-integer month
    (1999, 5),      # year too low
    (2101, 5),      # year too high
    (2025, 0),      # month < 1
    (2025, 13),     # month > 12
])
def test_invalid_year_month(year, month):
    with pytest.raises(ValueError):
        calculate_monthly_inventory_spend([], year, month)


# ------------------------------------------------------
# EP + Decision Table:
# Valid orders included only if date matches target month/year
# ------------------------------------------------------
def test_filter_orders_by_month_year():
    orders = [
        make_order(datetime(2025, 1, 1), 2, 5),  # included
        make_order(datetime(2025, 2, 1), 2, 5),  # excluded
        make_order(datetime(2024, 1, 1), 2, 5),  # excluded
    ]

    result = calculate_monthly_inventory_spend(orders, 2025, 1)
    assert result["total_spend"] == 10
    assert result["category_breakdown"]["General"] == 10


# ------------------------------------------------------
# EP + BVA on qty and cost
# ------------------------------------------------------
@pytest.mark.parametrize("qty, cost, expected", [
    (0, 10, 0),     # qty = boundary 0
    (5, 0, 0),      # cost = boundary 0
    (1, 1, 1),      # normal case
    (999999, 1, 999999),        # high boundary qty
])
def test_valid_qty_cost(qty, cost, expected):
    orders = [make_order(datetime(2025, 1, 1), qty, cost)]
    result = calculate_monthly_inventory_spend(orders, 2025, 1)
    assert result["total_spend"] == expected


# ------------------------------------------------------
# EP: Invalid qty or cost = ValueError
# ------------------------------------------------------
@pytest.mark.parametrize("qty, cost", [
    (-1, 10),     # negative qty
    (5, -3),      # negative cost
    ("5", 10),    # qty not numeric
    (3, "x"),     # cost not numeric
])
def test_invalid_qty_cost(qty, cost):
    orders = [make_order(datetime(2025, 1, 1), qty, cost)]
    with pytest.raises(ValueError):
        calculate_monthly_inventory_spend(orders, 2025, 1)


# ------------------------------------------------------
# EP: Invalid date = ValueError
# ------------------------------------------------------
def test_invalid_date_type():
    orders = [{
        "date": "2025-01-01",
        "qty": 2,
        "cost": 5
    }]
    with pytest.raises(ValueError):
        calculate_monthly_inventory_spend(orders, 2025, 1)


# ------------------------------------------------------
# Category breakdown + highest cost driver
# ------------------------------------------------------
def test_category_breakdown_and_highest_driver():
    orders = [
        make_order(datetime(2025, 1, 1), 2, 10, category="Fruit"),    # spend = 20
        make_order(datetime(2025, 1, 2), 1, 50, category="Dairy"),    # spend = 50
        make_order(datetime(2025, 1, 3), 3, 5,  category="Fruit"),    # spend = 15 → total fruit = 35
    ]

    result = calculate_monthly_inventory_spend(orders, 2025, 1)

    assert result["total_spend"] == 85
    assert result["category_breakdown"]["Fruit"] == 35
    assert result["category_breakdown"]["Dairy"] == 50
    assert result["highest_cost_driver"] == ("Dairy", 50)


# ------------------------------------------------------
# Empty order list = valid edge case
# ------------------------------------------------------
def test_empty_orders():
    result = calculate_monthly_inventory_spend([], 2025, 1)
    assert result["total_spend"] == 0
    assert result["category_breakdown"] == {}
    assert result["highest_cost_driver"] is None