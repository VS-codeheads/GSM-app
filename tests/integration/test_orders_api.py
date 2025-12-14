import pytest
import json
from datetime import datetime

# Expected structure for Order response
EXPECTED_ORDER_SCHEMA = {
    "order_id": int,
    "customer_name": str,
    "total_price": (int, float),
    "datetime": str,
}

# Expected structure for Order Details item
EXPECTED_ORDER_DETAIL_SCHEMA = {
    "product_id": int,
    "quantity": (int, float),
    "total_price": (int, float),
    "product_name": str,
    "uom_name": str,
}


class TestOrdersEndpoint:
    """Integration tests for orders endpoints."""

    def test_get_all_orders_returns_valid_structure(self, client):
        """
        Checks that /getOrders returns a valid list of orders with correct types.
        """
        response = client.get("/getOrders")
        assert response.status_code == 200, f"Unexpected status code: {response.status_code}"

        orders = response.get_json()
        assert isinstance(orders, list), "Response is not a JSON list"

        # If there are orders, check structure
        if len(orders) > 0:
            for order in orders:
                assert isinstance(order, dict), "Order item is not a JSON object"

                # Check all required fields exist and have correct types
                for field, expected_type in EXPECTED_ORDER_SCHEMA.items():
                    assert field in order, f"Missing field '{field}' in order"
                    assert isinstance(order[field], expected_type), \
                        f"Field '{field}' is not of type {expected_type}, got {type(order[field])}"

                # Additional validations
                assert order["customer_name"], "Customer name is empty"
                assert order["total_price"] >= 0, "Total price should be non-negative"

    def test_get_recent_orders_returns_limited_results(self, client):
        """
        Checks that /getRecentOrders returns at most 5 recent orders.
        """
        response = client.get("/getRecentOrders")
        assert response.status_code == 200

        orders = response.get_json()
        assert isinstance(orders, list)
        assert len(orders) <= 5, "Should return at most 5 recent orders"

        # Validate structure of returned orders
        for order in orders:
            assert "order_id" in order
            assert "customer_name" in order
            assert "total_price" in order
            assert "datetime" in order

    @pytest.mark.parametrize("order_data", [
        {
            "customer_name": "John Doe",
            "total_price": 10.00,
            "datetime": "2025-12-03 12:00:00",
            "order_details": [
                {"product_id": 1, "quantity": 2, "total_price": 10.00},
            ]
        },
        {
            "customer_name": "Jane Smith",
            "total_price": 15.00,
            "order_details": [
                {"product_id": 1, "quantity": 5, "total_price": 50.00},
            ]
        },
        {
            "customer_name": "Bob Johnson",
            "total_price": 30.00,
            "datetime": "2025-12-03 14:00:00",
            "order_details": [
                {"product_id": 1, "quantity": 10, "total_price": 30.00},
            ]
        },
    ])
    def test_add_order_creates_valid_record(self, client, db_conn, cleanup_orders, order_data):
        """
        Parameterized test: Checks that /addOrder creates a valid order record in the DB.
        Tests multiple order variations with different customer names and order details.
        """
        response = client.post(
            "/addOrder",
            data={"data": json.dumps(order_data)},
            content_type="application/x-www-form-urlencoded"
        )

        assert response.status_code == 200, f"Failed to add order: {response.get_json()}"

        result = response.get_json()
        assert "order_id" in result, "Response missing 'order_id'"

        order_id = result["order_id"]
        cleanup_orders([order_id])

        # Verify order in database
        cursor = db_conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM orders WHERE order_id = %s",
            (order_id,)
        )
        db_order = cursor.fetchone()
        cursor.close()

        assert db_order is not None, f"Order {order_id} not found in database"
        assert db_order["customer_name"] == order_data["customer_name"], "Customer name mismatch"
        assert float(db_order["total_price"]) == order_data["total_price"], "Order total price mismatch"

    def test_add_order_with_missing_customer_name_returns_400(self, client):
        """
        Checks that /addOrder returns 400 when customer_name is missing.
        """
        invalid_order = {
            "total_price": 50.00,
            "order_details": [{"product_id": 1, "quantity": 2, "total_price": 50.00}]
        }

        response = client.post(
            "/addOrder",
            data={"data": json.dumps(invalid_order)},
            content_type="application/x-www-form-urlencoded"
        )

        assert response.status_code == 400, "Expected 400 for missing customer_name"

    def test_add_order_with_missing_order_details_returns_400(self, client):
        """
        Checks that /addOrder returns 400 when order_details is missing.
        """
        invalid_order = {
            "customer_name": "John Doe",
            "total_price": 50.00
        }

        response = client.post(
            "/addOrder",
            data={"data": json.dumps(invalid_order)},
            content_type="application/x-www-form-urlencoded"
        )

        assert response.status_code == 400, "Expected 400 for missing order_details"

    def test_add_order_with_invalid_json_returns_400(self, client):
        """
        Checks that /addOrder handles invalid JSON and returns 400 error.
        """
        response = client.post(
            "/addOrder",
            data={"data": "not valid json"},
            content_type="application/x-www-form-urlencoded"
        )

        assert response.status_code == 400, "Expected 400 for invalid JSON"

    def test_get_order_details_returns_valid_structure(self, client, db_conn):
        """
        Checks that /getOrder/<order_id> returns order with items and correct structure.
        Tests against existing orders in the database.
        """
        # Get an existing order
        cursor = db_conn.cursor(dictionary=True)
        cursor.execute("SELECT order_id FROM orders LIMIT 1")
        order = cursor.fetchone()
        cursor.close()

        if order is None:
            pytest.skip("No orders in database to test")

        order_id = order["order_id"]
        response = client.get(f"/getOrder/{order_id}")
        assert response.status_code == 200

        order_data = response.get_json()
        assert isinstance(order_data, dict)

        # Verify order fields
        assert "order_id" in order_data
        assert "customer_name" in order_data
        assert "total_price" in order_data
        assert "items" in order_data

        # Verify items structure
        items = order_data["items"]
        assert isinstance(items, list)

        for item in items:
            for field in ["order_id", "product_id", "quantity", "product_name", "uom_name"]:
                assert field in item, f"Missing field '{field}' in order item"

    def test_get_nonexistent_order_returns_404(self, client):
        """
        Checks that /getOrder/<non_existent_id> returns 404.
        """
        response = client.get("/getOrder/999999")
        assert response.status_code == 404, "Expected 404 for non-existent order"

    def test_delete_order_removes_valid_order(self, client, db_conn):
        """
        Checks that /deleteOrder/<order_id> properly removes an order and its details.
        """
        # First, add an order to delete
        order_data = {
            "customer_name": "Order to Delete",
            "total_price": 25.00,
            "datetime": "2025-12-03 15:00:00",
            "order_details": [
                {"product_id": 1, "quantity": 5, "total_price": 25.00},
            ]
        }

        response = client.post(
            "/addOrder",
            data={"data": json.dumps(order_data)},
            content_type="application/x-www-form-urlencoded"
        )

        order_id = response.get_json()["order_id"]

        # Delete it
        response = client.delete(f"/deleteOrder/{order_id}")
        assert response.status_code == 200, f"Failed to delete order: {response.get_json()}"

        result = response.get_json()
        assert result["deleted"] == order_id, "Response doesn't confirm deletion"

        # Verify deletion in database
        cursor = db_conn.cursor()
        cursor.execute(
            "SELECT 1 FROM orders WHERE order_id = %s LIMIT 1",
            (order_id,)
        )
        assert cursor.fetchone() is None, "Order still exists in database after deletion"

        # Verify order_details were also deleted
        cursor.execute(
            "SELECT 1 FROM order_details WHERE order_id = %s LIMIT 1",
            (order_id,)
        )
        assert cursor.fetchone() is None, "Order details still exist in database after order deletion"
        cursor.close()

    def test_get_order_details_endpoint_returns_valid_data(self, client, db_conn):
        """
        Checks that /getOrderDetails/<order_id> returns order details with correct structure.
        """
        # Get an existing order
        cursor = db_conn.cursor(dictionary=True)
        cursor.execute("SELECT order_id FROM orders LIMIT 1")
        order = cursor.fetchone()
        cursor.close()

        if order is None:
            pytest.skip("No orders in database to test")

        order_id = order["order_id"]
        response = client.get(f"/getOrderDetails/{order_id}")
        assert response.status_code == 200

        details = response.get_json()
        assert isinstance(details, list)

        # Validate structure of order details
        for detail in details:
            assert "product_id" in detail
            assert "quantity" in detail
            assert isinstance(detail["quantity"], (int, float))
