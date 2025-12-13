import pytest
import json

# Expected structure for Product response
EXPECTED_PRODUCT_SCHEMA = {
    "product_id": int,
    "name": str,
    "uom_id": int,
    "price_per_unit": float,
    "quantity": int,
    "uom_name": str,
}


class TestProductsEndpoint:
    """Integration tests for products endpoints."""

    def test_get_products_returns_valid_structure(self, client):
        """
        Checks that /getProducts returns a valid list of products with correct types.
        """
        response = client.get("/getProducts")
        assert response.status_code == 200, f"Unexpected status code: {response.status_code}"

        products = response.get_json()
        assert isinstance(products, list), "Response is not a JSON list"

        # If there are products, check structure
        if len(products) > 0:
            for product in products:
                assert isinstance(product, dict), "Product item is not a JSON object"

                # Check all required fields exist and have correct types
                for field, expected_type in EXPECTED_PRODUCT_SCHEMA.items():
                    assert field in product, f"Missing field '{field}' in product"
                    assert isinstance(product[field], expected_type), \
                        f"Field '{field}' is not of type {expected_type}, got {type(product[field])}"

    def test_get_products_returns_db_backed_data(self, client, db_conn):
        """
        Confirms that /getProducts returns data that exists in the database.
        """
        response = client.get("/getProducts")
        assert response.status_code == 200

        products = response.get_json()
        assert isinstance(products, list)

        if len(products) > 0:
            # Verify first product exists in DB
            first_product = products[0]
            cursor = db_conn.cursor()

            cursor.execute(
                "SELECT 1 FROM products WHERE product_id = %s LIMIT 1",
                (first_product["product_id"],)
            )
            matching_row = cursor.fetchone()
            cursor.close()

            assert matching_row is not None, f"Product {first_product['product_id']} not found in database"

    @pytest.mark.parametrize("product_data", [
        {
            "name": "Test Apple",
            "uom_id": 1,
            "price_per_unit": 0.50,
            "quantity": 100
        },
        {
            "name": "Test Banana",
            "uom_id": 2,
            "price_per_unit": 1.25,
            "quantity": 50
        },
        {
            "name": "Test Orange",
            "uom_id": 3,
            "price_per_unit": 2.00,
            "quantity": 200
        },
    ])
    def test_add_product_creates_valid_record(self, client, db_conn, cleanup_products, product_data):
        """
        Parameterized test: Checks that /addProduct creates a valid product record in the DB.
        Tests multiple product variations.
        """
        # Send POST request with form data
        response = client.post(
            "/addProduct",
            data={"data": json.dumps(product_data)},
            content_type="application/x-www-form-urlencoded"
        )

        assert response.status_code == 200, f"Failed to add product: {response.get_json()}"

        result = response.get_json()
        assert "product_id" in result, "Response missing 'product_id'"

        product_id = result["product_id"]
        cleanup_products([product_id])

        # Verify in database
        cursor = db_conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM products WHERE product_id = %s",
            (product_id,)
        )
        db_product = cursor.fetchone()
        cursor.close()

        assert db_product is not None, f"Product {product_id} not found in database"
        assert db_product["name"] == product_data["name"], "Product name mismatch"
        assert db_product["quantity"] == product_data["quantity"], "Product quantity mismatch"
        assert float(db_product["price_per_unit"]) == product_data["price_per_unit"], \
            "Product price mismatch"

    def test_add_product_with_invalid_json_returns_400(self, client):
        """
        Checks that /addProduct handles invalid JSON and returns 400 error.
        """
        response = client.post(
            "/addProduct",
            data={"data": "not valid json"},
            content_type="application/x-www-form-urlencoded"
        )

        assert response.status_code == 400, "Expected 400 for invalid JSON"
        result = response.get_json()
        assert "error" in result, "Error response should contain 'error' field"

    def test_add_product_with_missing_data_returns_400(self, client):
        """
        Checks that /addProduct returns 400 when 'data' parameter is missing.
        """
        response = client.post("/addProduct", content_type="application/x-www-form-urlencoded")

        assert response.status_code == 400, "Expected 400 when data is missing"

    def test_update_product_modifies_existing_product(self, client, db_conn, cleanup_products):
        """
        Checks that /updateProduct modifies a product correctly.
        """
        # First, add a product
        product_data = {
            "name": "Original Name",
            "uom_id": 1,
            "price_per_unit": 1.00,
            "quantity": 100
        }

        response = client.post(
            "/addProduct",
            data={"data": json.dumps(product_data)},
            content_type="application/x-www-form-urlencoded"
        )

        product_id = response.get_json()["product_id"]
        cleanup_products([product_id])

        # Update the product
        updated_data = {
            "product_id": product_id,
            "name": "Updated Name",
            "uom_id": 2,
            "price_per_unit": 2.50,
            "quantity": 250
        }

        response = client.post(
            "/updateProduct",
            data={"data": json.dumps(updated_data)},
            content_type="application/x-www-form-urlencoded"
        )

        assert response.status_code == 200, f"Failed to update product: {response.get_json()}"

        # Verify update in database
        cursor = db_conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM products WHERE product_id = %s",
            (product_id,)
        )
        db_product = cursor.fetchone()
        cursor.close()

        assert db_product["name"] == "Updated Name", "Product name was not updated"
        assert db_product["quantity"] == 250, "Product quantity was not updated"

    def test_delete_product_removes_valid_product(self, client, db_conn):
        """
        Parameterized test: Checks that /deleteProduct properly removes a product.
        Tests with different product IDs.
        """
        # First, add a product to delete
        product_data = {
            "name": "Product to Delete",
            "uom_id": 1,
            "price_per_unit": 1.00,
            "quantity": 10
        }

        response = client.post(
            "/addProduct",
            data={"data": json.dumps(product_data)},
            content_type="application/x-www-form-urlencoded"
        )

        product_id = response.get_json()["product_id"]

        # Delete it
        response = client.delete(f"/deleteProduct/{product_id}")
        assert response.status_code == 200, f"Failed to delete product: {response.get_json()}"

        result = response.get_json()
        assert result["deleted"] == product_id, "Response doesn't confirm deletion"

        # Verify deletion in database
        cursor = db_conn.cursor()
        cursor.execute(
            "SELECT 1 FROM products WHERE product_id = %s LIMIT 1",
            (product_id,)
        )
        assert cursor.fetchone() is None, "Product still exists in database after deletion"
        cursor.close()

    def test_get_uom_returns_valid_structure(self, client):
        """
        Checks that /getUOM returns valid UOM (Unit of Measure) list.
        """
        response = client.get("/getUOM")
        assert response.status_code == 200

        uoms = response.get_json()
        assert isinstance(uoms, list), "Response is not a JSON list"

        if len(uoms) > 0:
            for uom in uoms:
                assert isinstance(uom, dict), "UOM item is not a JSON object"
                assert "uom_id" in uom, "Missing 'uom_id' field"
                assert "uom_name" in uom, "Missing 'uom_name' field"
                assert isinstance(uom["uom_id"], int), "uom_id is not an integer"
                assert isinstance(uom["uom_name"], str), "uom_name is not a string"
