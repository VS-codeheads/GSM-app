import pytest
import random
from backend.services.revenue_calculator import generate_random_sales, calculate_revenue_and_profit


# ---------------------------------------------------------
# EP & BVA for generate_random_sales()
# ---------------------------------------------------------

def test_sales_never_negative():
    """EP - Result can't be negative"""
    for _ in range(50):
        assert generate_random_sales(10) >= 0

def test_sales_never_exceed_stock():
    "EP - Sales can't be more than stock"
    for stock in [1, 5, 10, 100]:
        for _ in range(20):
            assert generate_random_sales(stock) <= stock

def test_zero_stock_always_zero():
    """BVA - stock = 0 is a boundary, it should always return 0"""
    assert generate_random_sales(0) == 0

def test_large_stock_boundary():
    """BVA - large stock case should still return within range"""
    result = generate_random_sales(10000)
    assert 0 <= result <= 10000

def test_sees_makes_random_predefined():
    """Desicion table - random generator behaves consistantly with seed"""
    random.seed(123)
    first_run = generate_random_sales(50)

    random.seed(123)
    second_run = generate_random_sales(50)

    assert first_run == second_run


# ---------------------------------------------------------
# Tests for calculate_revenue_and_profit()
# ---------------------------------------------------------  

def test_no_products_return_empty_summary():
    """EP - empty product list should return zeros"""
    result = calculate_revenue_and_profit([], days=7, seed=1)

    assert result["summary"]["total_revenue"] == 0
    assert result["summary"]["total_cost"] == 0
    assert result["summary"]["total_profit"] == 0
    assert result["details"] == []

def test_single_product_zero_stock():
    """BVA - boundary case stock=0 = no sales and no revenue"""
    products = [{
        "name": "Test",
        "quantity": 0,
        "price_per_unit": 2.0,
        "selling_price": 5.0,
    }]

    res = calculate_revenue_and_profit(products, days=5, seed=1)
    detail = res["details"][0]

    assert detail["sold_units"] == 0
    assert detail["revenue"] == 0
    assert detail["profit"] == 0

def test_profit_prositive_case():
    """Decision table - sell price > buy price = positive profit"""
    products = [{
        "name": "Apple",
        "quantity": 10,
        "price_per_unit": 1.0,
        "selling_price": 3.0,
    }]

    res = calculate_revenue_and_profit(products, days=1, seed=1)
    detail = res["details"][0]

    assert detail["profit"] >= 0  # some units could sell
    assert res["summary"]["total_profit"] == detail["profit"]

def test_profit_negative_case():
    """Decision table - buy price > sell price = negative profit expected"""
    products = [{
        "name": "Banana",
        "quantity": 10,
        "price_per_unit": 5.0,
        "selling_price": 3.0,
    }]

    res = calculate_revenue_and_profit(products, days=2, seed=2)
    detail = res["details"][0]

    assert detail["profit"] <= 0

@pytest.mark.parametrize("days", [1, 2, 7, 30])
def test_days_parameter_affects_result(days):
    """BVA - days is a boundary value driver for sales colume"""
    products = [{
        "name": "Milk",
        "quantity": 50,
        "price_per_unit": 1.0,
        "selling_price": 2.0,
    }]

    res = calculate_revenue_and_profit(products, days=days, seed=123)
    summary = res["summary"]

    assert summary["total_revenue"] >= 0
    assert summary["total_cost"] >= 0


# -----------------------------
# EP + BVA: VALID days
# -----------------------------

@pytest.mark.parametrize("days", [1, 7, 30, 365])
def test_valid_days(days):
    """EP - valid days are accepted and respond normally"""
    products = [{
        "name": "Test",
        "quantity": 100,
        "price_per_unit": 1,
        "selling_price": 2,       
    }]

    result = calculate_revenue_and_profit(products, days=days, seed=10)
    assert "summary" in result


# -----------------------------
# INVALID days = ValueError
# -----------------------------
@pytest.mark.parametrize("days", [0, -1, -10, 1.5, "abc", None])
def test_invalid_days_raises(days):
    """EP - invalid days input should raise ValueError."""
    products = [{
        "name": "Test",
        "quantity": 10,
        "price_per_unit": 1,
        "selling_price": 2,
    }]

    with pytest.raises(ValueError):
        calculate_revenue_and_profit(products, days=days, seed=5)


# -----------------------------
# EP + BVA: Valid seed values
# -----------------------------
@pytest.mark.parametrize("seed", [None, 1, 5, 99999])
def test_valid_seeds(seed):
    """EP/BVA - valid seeds accepted."""
    products = [{
        "name": "Test",
        "quantity": 10,
        "price_per_unit": 1,
        "selling_price": 2,
    }]

    result = calculate_revenue_and_profit(products, days=3, seed=seed)
    assert "summary" in result  # call succeeded



# -----------------------------
# Invalid seed = ValueError
# -----------------------------
@pytest.mark.parametrize("seed", [-1, -5, "abc", 3.14, [], {}])
def test_invalid_seed_raises(seed):
    """EP - invalid seed input must raise ValueError."""
    products = [{
        "name": "Test",
        "quantity": 10,
        "price_per_unit": 1,
        "selling_price": 2,
    }]

    with pytest.raises(ValueError):
        calculate_revenue_and_profit(products, days=5, seed=seed)


# -----------------------------
# Decision Table Test:
# days (valid/invalid) × seed (valid/invalid)
# -----------------------------
@pytest.mark.parametrize("days,seed,should_pass", [
    (7, 10, True),      # valid days, valid seed
    (7, None, True),    # valid days, seed excluded
    (7, -1, False),     # valid days, invalid seed
    (0, 10, False),     # invalid days, valid seed
    (0, -1, False),     # both invalid
])
def test_decision_table_days_seed(days, seed, should_pass):
    products = [{
        "name": "Example",
        "quantity": 20,
        "price_per_unit": 1,
        "selling_price": 3,
    }]

    if should_pass:
        result = calculate_revenue_and_profit(products, days=days, seed=seed)
        assert "summary" in result
    else:
        with pytest.raises(ValueError):
            calculate_revenue_and_profit(products, days=days, seed=seed)