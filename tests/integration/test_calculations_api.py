import pytest
import json

# Expected structure for Revenue calculation response
EXPECTED_REVENUE_SUMMARY_SCHEMA = {
    "total_revenue": (int, float),
    "total_cost": (int, float),
    "total_profit": (int, float),
    "profit_margin_percent": (int, float),
    "total_units_sold": int,
}

# Expected structure for Revenue detail item
EXPECTED_REVENUE_DETAIL_SCHEMA = {
    "product": str,
    "sold_units": int,
    "initial_stock": int,
    "remaining_stock": int,
    "revenue": (int, float),
    "cost": (int, float),
    "profit": (int, float),
    "profit_margin_percent": (int, float),
}

# Expected structure for Spend calculation response
EXPECTED_SPEND_RESPONSE_SCHEMA = {
    "total_spend": (int, float),
    "category_breakdown": dict,
    "highest_cost_driver": (type(None), tuple),
}


class TestRevenueCalculationEndpoint:
    """Integration tests for revenue calculation endpoint."""

    @pytest.mark.parametrize("days,seed", [
        (1, 123),
        (7, 456),
        (30, 789),
    ])
    def test_revenue_calculation_returns_valid_structure(self, client, days, seed):
        """
        Parameterized test: Checks that /api/calc/revenue returns valid structure
        with different day and seed values.
        """
        payload = {
            "product_ids": [1],
            "days": days,
            "seed": seed
        }

        response = client.post(
            "/api/calc/revenue",
            data=json.dumps(payload),
            content_type="application/json"
        )

        assert response.status_code == 200, f"Unexpected status code: {response.status_code}"

        result = response.get_json()
        assert isinstance(result, dict), "Response is not a JSON object"

        # Verify summary structure
        assert "summary" in result, "Response missing 'summary' field"
        summary = result["summary"]

        for field, expected_type in EXPECTED_REVENUE_SUMMARY_SCHEMA.items():
            assert field in summary, f"Missing field '{field}' in summary"
            assert isinstance(summary[field], expected_type), \
                f"Field '{field}' is not of type {expected_type}, got {type(summary[field])}"

        # Verify details structure
        assert "details" in result, "Response missing 'details' field"
        details = result["details"]
        assert isinstance(details, list), "Details is not a list"

        for detail in details:
            for field, expected_type in EXPECTED_REVENUE_DETAIL_SCHEMA.items():
                assert field in detail, f"Missing field '{field}' in detail"
                assert isinstance(detail[field], expected_type), \
                    f"Field '{field}' is not of type {expected_type}, got {type(detail[field])}"

    def test_revenue_calculation_with_empty_product_ids_returns_400(self, client):
        """
        Checks that /api/calc/revenue returns 400 for empty product_ids list.
        """
        payload = {
            "product_ids": [],
            "days": 7
        }

        response = client.post(
            "/api/calc/revenue",
            data=json.dumps(payload),
            content_type="application/json"
        )

        assert response.status_code == 400, "Expected 400 for empty product_ids"
        result = response.get_json()
        assert "error" in result, "Error response should contain 'error' field"

    @pytest.mark.parametrize("invalid_product_ids", [
        [0],                    # product_id = 0 (invalid)
        [-1, -2],               # negative product_ids
        ["not_int"],            # string instead of int
        [1, "two"],             # mixed types
    ])
    def test_revenue_calculation_with_invalid_product_ids_returns_400(self, client, invalid_product_ids):
        """
        Parameterized test: Checks that /api/calc/revenue handles invalid product IDs.
        """
        payload = {
            "product_ids": invalid_product_ids,
            "days": 7
        }

        response = client.post(
            "/api/calc/revenue",
            data=json.dumps(payload),
            content_type="application/json"
        )

        assert response.status_code == 400, f"Expected 400 for invalid product_ids: {invalid_product_ids}"

    @pytest.mark.parametrize("invalid_days", [
        0,          # days = 0 (boundary)
        -1,         # negative days
        366,        # days > 365 (boundary)
        "abc",      # string instead of int
    ])
    def test_revenue_calculation_with_invalid_days_returns_400(self, client, invalid_days):
        """
        Parameterized test: Checks that /api/calc/revenue validates days parameter.
        Tests boundary values and invalid types.
        """
        payload = {
            "product_ids": [1],
            "days": invalid_days
        }

        response = client.post(
            "/api/calc/revenue",
            data=json.dumps(payload),
            content_type="application/json"
        )

        assert response.status_code == 400, f"Expected 400 for invalid days: {invalid_days}"

    def test_revenue_calculation_with_invalid_seed_returns_400(self, client):
        """
        Checks that /api/calc/revenue validates seed parameter.
        """
        payload = {
            "product_ids": [1],
            "days": 7,
            "seed": -1  # negative seed
        }

        response = client.post(
            "/api/calc/revenue",
            data=json.dumps(payload),
            content_type="application/json"
        )

        assert response.status_code == 400, "Expected 400 for negative seed"

    def test_revenue_calculation_with_nonexistent_product_returns_400(self, client):
        """
        Checks that /api/calc/revenue returns 400 when product doesn't exist.
        """
        payload = {
            "product_ids": [999999],  # Non-existent product
            "days": 7
        }

        response = client.post(
            "/api/calc/revenue",
            data=json.dumps(payload),
            content_type="application/json"
        )

        assert response.status_code == 400, "Expected 400 for non-existent product"

    def test_revenue_calculation_returns_valid_structure(self, client):
        """
        Checks that revenue calculation returns valid response structure.
        """
        payload = {
            "product_ids": [1],
            "days": 7,
            "seed": 123
        }

        response = client.post(
            "/api/calc/revenue",
            data=json.dumps(payload),
            content_type="application/json"
        )

        assert response.status_code == 200

        result = response.get_json()
        summary = result["summary"]

        # Verify structure and types only
        assert "total_revenue" in summary
        assert "total_cost" in summary
        assert "total_profit" in summary
        assert "total_units_sold" in summary
        
        assert isinstance(summary["total_revenue"], (int, float)), "Revenue should be numeric"
        assert isinstance(summary["total_cost"], (int, float)), "Cost should be numeric"
        assert isinstance(summary["total_profit"], (int, float)), "Profit should be numeric"
        assert isinstance(summary["total_units_sold"], int), "Units sold should be an integer"

    def test_revenue_calculation_same_seed_produces_same_result(self, client):
        """
        Checks that using the same seed produces identical results.
        """
        payload = {
            "product_ids": [1],
            "days": 7,
            "seed": 42
        }

        response1 = client.post(
            "/api/calc/revenue",
            data=json.dumps(payload),
            content_type="application/json"
        )

        response2 = client.post(
            "/api/calc/revenue",
            data=json.dumps(payload),
            content_type="application/json"
        )

        assert response1.status_code == 200
        assert response2.status_code == 200

        result1 = response1.get_json()
        result2 = response2.get_json()

        assert result1["summary"] == result2["summary"], "Same seed should produce same results"


class TestInventorySpendCalculationEndpoint:
    """Integration tests for inventory spend calculation endpoint."""

    @pytest.mark.parametrize("spend_data", [
        {
            "year": 2025,
            "month": 1,
            "orders": [
                {"date": "2025-01-01T10:00:00", "qty": 5, "cost": 10.0, "category": "Fruit"},
                {"date": "2025-01-15T14:00:00", "qty": 3, "cost": 20.0, "category": "Vegetable"},
            ]
        },
        {
            "year": 2024,
            "month": 12,
            "orders": [
                {"date": "2024-12-01T09:00:00", "qty": 10, "cost": 5.0, "category": "Dairy"},
            ]
        },
        {
            "year": 2025,
            "month": 6,
            "orders": [
                {"date": "2025-06-10T11:00:00", "qty": 2, "cost": 15.5, "category": "Meat"},
                {"date": "2025-06-20T16:00:00", "qty": 4, "cost": 8.0, "category": "Bread"},
                {"date": "2025-06-25T12:00:00", "qty": 1, "cost": 25.0, "category": "Meat"},
            ]
        },
    ])
    def test_inventory_spend_returns_valid_structure(self, client, spend_data):
        """
        Parameterized test: Checks that /api/calc/spend returns valid structure
        with different months and order data.
        """
        response = client.post(
            "/api/calc/spend",
            data=json.dumps(spend_data),
            content_type="application/json"
        )

        assert response.status_code == 200, f"Unexpected status code: {response.status_code}"

        result = response.get_json()
        assert isinstance(result, dict), "Response is not a JSON object"

        # Verify response structure
        for field in EXPECTED_SPEND_RESPONSE_SCHEMA.keys():
            assert field in result, f"Missing field '{field}' in response"

        # Verify field types
        assert isinstance(result["total_spend"], (int, float)), "total_spend should be numeric"
        assert isinstance(result["category_breakdown"], dict), "category_breakdown should be dict"
        assert result["total_spend"] >= 0, "total_spend should be non-negative"

    @pytest.mark.parametrize("invalid_year", [
        1999,   # year < 2000 (boundary)
        2101,   # year > 2100 (boundary)
        "2025", # string instead of int
    ])
    def test_inventory_spend_with_invalid_year_returns_400(self, client, invalid_year):
        """
        Parameterized test: Checks that /api/calc/spend validates year parameter.
        """
        spend_data = {
            "year": invalid_year,
            "month": 1,
            "orders": []
        }

        response = client.post(
            "/api/calc/spend",
            data=json.dumps(spend_data),
            content_type="application/json"
        )

        assert response.status_code == 400, f"Expected 400 for invalid year: {invalid_year}"

    @pytest.mark.parametrize("invalid_month", [
        0,      # month = 0 (boundary)
        13,     # month > 12 (boundary)
        -1,     # negative month
        "06",   # string instead of int
    ])
    def test_inventory_spend_with_invalid_month_returns_400(self, client, invalid_month):
        """
        Parameterized test: Checks that /api/calc/spend validates month parameter.
        """
        spend_data = {
            "year": 2025,
            "month": invalid_month,
            "orders": []
        }

        response = client.post(
            "/api/calc/spend",
            data=json.dumps(spend_data),
            content_type="application/json"
        )

        assert response.status_code == 400, f"Expected 400 for invalid month: {invalid_month}"

    def test_inventory_spend_with_empty_orders_returns_zero_spend(self, client):
        """
        Checks that /api/calc/spend handles empty orders list and returns zero spend.
        """
        spend_data = {
            "year": 2025,
            "month": 1,
            "orders": []
        }

        response = client.post(
            "/api/calc/spend",
            data=json.dumps(spend_data),
            content_type="application/json"
        )

        assert response.status_code == 200

        result = response.get_json()
        assert result["total_spend"] == 0, "Empty orders should result in zero spend"
        assert result["category_breakdown"] == {}, "Empty orders should have empty category breakdown"

    def test_inventory_spend_filters_by_month_correctly(self, client):
        """
        Checks that /api/calc/spend correctly filters orders by month.
        Only orders in the specified month should be counted.
        """
        spend_data = {
            "year": 2025,
            "month": 6,
            "orders": [
                {"date": "2025-05-01T10:00:00", "qty": 5, "cost": 10.0, "category": "Fruit"},  # May - excluded
                {"date": "2025-06-01T10:00:00", "qty": 5, "cost": 10.0, "category": "Fruit"},  # June - included
                {"date": "2025-07-01T10:00:00", "qty": 5, "cost": 10.0, "category": "Fruit"},  # July - excluded
            ]
        }

        response = client.post(
            "/api/calc/spend",
            data=json.dumps(spend_data),
            content_type="application/json"
        )

        assert response.status_code == 200

        result = response.get_json()
        # Only June order should be counted: 5 * 10.0 = 50.0
        assert result["total_spend"] == 50.0, "Should only count June orders"
        assert result["category_breakdown"]["Fruit"] == 50.0

    def test_inventory_spend_calculates_highest_cost_driver(self, client):
        """
        Checks that /api/calc/spend correctly identifies the highest cost driver category.
        """
        spend_data = {
            "year": 2025,
            "month": 1,
            "orders": [
                {"date": "2025-01-01T10:00:00", "qty": 2, "cost": 10.0, "category": "Fruit"},  # 20.0
                {"date": "2025-01-05T10:00:00", "qty": 3, "cost": 20.0, "category": "Vegetable"},  # 60.0
                {"date": "2025-01-10T10:00:00", "qty": 1, "cost": 15.0, "category": "Dairy"},  # 15.0
            ]
        }

        response = client.post(
            "/api/calc/spend",
            data=json.dumps(spend_data),
            content_type="application/json"
        )

        assert response.status_code == 200

        result = response.get_json()
        highest = result["highest_cost_driver"]
        assert highest is not None, "highest_cost_driver should not be None"
        assert highest[0] == "Vegetable", "Vegetable should be the highest cost driver"
        assert highest[1] == 60.0, "Highest spend should be 60.0"

    def test_inventory_spend_with_multiple_same_category_aggregates(self, client):
        """
        Checks that /api/calc/spend correctly aggregates multiple orders of the same category.
        """
        spend_data = {
            "year": 2025,
            "month": 1,
            "orders": [
                {"date": "2025-01-01T10:00:00", "qty": 2, "cost": 5.0, "category": "Fruit"},
                {"date": "2025-01-10T10:00:00", "qty": 3, "cost": 10.0, "category": "Fruit"},
                {"date": "2025-01-20T10:00:00", "qty": 1, "cost": 5.0, "category": "Fruit"},
            ]
        }

        response = client.post(
            "/api/calc/spend",
            data=json.dumps(spend_data),
            content_type="application/json"
        )

        assert response.status_code == 200

        result = response.get_json()
        # Expected: (2*5) + (3*10) + (1*5) = 10 + 30 + 5 = 45
        assert result["total_spend"] == 45.0, "Should aggregate all Fruit category orders"
        assert result["category_breakdown"]["Fruit"] == 45.0, "Fruit category total should be 45.0"
