# Integration Tests

This directory contains integration tests for the GSM (Grocery Store Manager) application. These tests verify that the Flask API endpoints work correctly with the database and handle various scenarios.

## Test Files

### `conftest.py`
Pytest configuration file that provides shared fixtures for all integration tests:

- **`client`**: Flask test client for making HTTP requests to endpoints
- **`db_conn`**: Database connection for direct database verification
- **`cleanup_products`**: Fixture to clean up test products after each test
- **`cleanup_orders`**: Fixture to clean up test orders after each test

### `test_products_api.py`
Tests for product management endpoints:

- `GET /getProducts` - Retrieve all products
- `POST /addProduct` - Create new product
- `POST /updateProduct` - Update existing product
- `DELETE /deleteProduct/<id>` - Delete a product
- `GET /getUOM` - Retrieve units of measure

**Test Patterns Used:**
- Schema validation (checking response structure and types)
- Database-backed assertions (verifying data persists in DB)
- Parameterized tests with multiple test cases
- Error handling (400, 404 responses)

### `test_orders_api.py`
Tests for order management endpoints:

- `GET /getOrders` - Retrieve all orders
- `GET /getRecentOrders` - Get last 5 orders
- `POST /addOrder` - Create new order
- `GET /getOrder/<id>` - Retrieve specific order with details
- `DELETE /deleteOrder/<id>` - Delete an order

**Test Patterns Used:**
- Schema validation for orders and order details
- Database-backed verification
- Parameterized tests for multiple order scenarios
- Cascading delete verification (order details cleanup)

### `test_calculations_api.py`
Tests for business logic endpoints:

#### Revenue Calculation (`POST /api/calc/revenue`)
- Validates response structure (summary and details)
- Tests parameterized inputs (different days and seeds)
- Verifies deterministic results with same seed
- Validates input parameters (product IDs, days, seed bounds)

**Parameterized Tests:**
- Multiple day values: 1, 7, 30
- Multiple seed values for reproducibility
- Invalid product IDs (empty, negative, wrong type)
- Boundary testing for days (0, 1, 365, 366)

#### Inventory Spend Calculation (`POST /api/calc/spend`)
- Validates response structure (total_spend, category_breakdown, highest_cost_driver)
- Tests month filtering (only counts orders in specified month)
- Verifies category aggregation (multiple orders same category)
- Identifies highest cost driver correctly

**Parameterized Tests:**
- Multiple months and years
- Different order combinations
- Invalid year/month bounds (1999, 2101, 0, 13)
- Empty orders handling

### `test_weather_api.py`
Tests for external weather API integration (OpenWeather API):

- Validates OpenWeather API response structure
- Tests error handling (404, 401, timeout, connection errors)
- Verifies temperature is in Celsius (units=metric)
- Tests icon format for display
- Parameterized tests for multiple cities
- Mocked external API calls (no actual HTTP requests)

**Test Patterns Used:**
- `@patch` decorator to mock external API
- Error simulation (timeout, connection errors)
- Response structure validation
- Format validation (icon codes, temperature ranges)

## Running Tests

### Run all integration tests:
```bash
pytest tests/integration/
```

### Run specific test file:
```bash
pytest tests/integration/test_products_api.py
```

### Run with verbose output:
```bash
pytest -v tests/integration/
```

### Run with detailed output:
```bash
pytest -s tests/integration/
```

### Run specific test class:
```bash
pytest tests/integration/test_products_api.py::TestProductsEndpoint
```

### Run specific test:
```bash
pytest tests/integration/test_products_api.py::TestProductsEndpoint::test_get_products_returns_valid_structure
```

### Run with coverage:
```bash
pytest --cov=backend tests/integration/
```

## Test Assertions

Tests use comprehensive assertions based on these patterns:

### Schema Validation
Checks that responses match expected structure and types:
```python
EXPECTED_PRODUCT_SCHEMA = {
    "product_id": int,
    "name": str,
    "uom_id": int,
    "price_per_unit": float,
    "quantity": int,
    "uom_name": str,
}
```

### Database Verification
Confirms that API results are backed by actual database data:
```python
cursor.execute(
    "SELECT 1 FROM products WHERE product_id = %s LIMIT 1",
    (first_product["product_id"],)
)
matching_row = cursor.fetchone()
assert matching_row is not None
```

### Parameterized Testing
Tests multiple input variations using `@pytest.mark.parametrize`:
```python
@pytest.mark.parametrize("product_data", [
    {"name": "Test Apple", "uom_id": 1, ...},
    {"name": "Test Banana", "uom_id": 2, ...},
])
def test_add_product_creates_valid_record(self, client, product_data):
    # Test runs once for each product_data variant
```

### Error Handling
Validates proper HTTP status codes and error messages:
```python
response = client.post("/addProduct", data={"data": "invalid json"})
assert response.status_code == 400
assert "error" in response.get_json()
```

## Environment Setup

Integration tests require:

1. **MySQL Database**: Tests connect to the database configured in `.env`
2. **Python Dependencies**: `pip install -r requirements.txt`
3. **Environment Variables**: `.env` file with:
   - `MYSQL_USER`
   - `MYSQL_PASSWORD`
   - `MYSQL_DB`
   - `MYSQL_HOST` (optional, defaults to localhost)

## Key Features

✓ **Comprehensive Assertions**: Each test validates multiple aspects of the response
✓ **Parameterized Tests**: Data-driven tests covering multiple scenarios with minimal code
✓ **Database Integration**: Tests verify data persistence and retrieval
✓ **Error Scenarios**: Tests check proper error handling and HTTP status codes
✓ **External API Mocking**: Weather API tests use mocks to avoid external dependencies
✓ **Cleanup**: Auto-cleanup of test data after each test
✓ **Type Checking**: All fields validated for correct types
✓ **Boundary Testing**: Edge cases like empty inputs, minimum/maximum values

## Notes

- Tests use fixtures for setup/teardown to ensure clean state
- Database transactions are committed to allow verification
- Mock decorators are used for external API tests to avoid network dependencies
- Each test is independent and can run in any order
