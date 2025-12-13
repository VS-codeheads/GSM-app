# End-to-End Tests

## Overview

This directory contains Playwright-based end-to-end tests for the GSM (Grocery Store Manager) application. These tests validate complete user journeys through the browser UI.

## Test Structure

```
tests/e2e/
├── conftest.py              # Pytest fixtures for browser setup and backend server
├── helpers.py               # Helper functions for common UI operations
├── validation.py            # Domain-specific validation functions
├── test_dashboard.py        # Tests for dashboard functionality
├── test_product_management.py  # Tests for product CRUD operations
└── test_order_creation.py   # Tests for order creation workflow
```

## Prerequisites

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Install Playwright Browsers**:
   ```bash
   playwright install chromium
   ```

3. **Database Setup**:
   - Ensure MySQL is running
   - Database `grocery_store` should exist with proper schema
   - Seed data should be present for meaningful tests

4. **Backend Configuration**:
   - Backend should be configured to run on `http://127.0.0.1:5000`
   - Environment variables should be set (database credentials, etc.)

## Running Tests

### Run All E2E Tests
```bash
pytest tests/e2e/ -v
```

### Run Specific Test File
```bash
pytest tests/e2e/test_dashboard.py -v
pytest tests/e2e/test_product_management.py -v
pytest tests/e2e/test_order_creation.py -v
```

### Run Specific Test
```bash
pytest tests/e2e/test_dashboard.py::test_dashboard_loads -v
```

### Run with Headed Browser (see UI)
```bash
pytest tests/e2e/ -v --headed
```

### Run with Slow Motion (for debugging)
```bash
pytest tests/e2e/ -v --headed --slowmo 1000
```

### Run with Browser Traces (for debugging)
```bash
pytest tests/e2e/ -v --tracing on
```

## Test Files

### `test_dashboard.py`
Tests the main dashboard page including:
- Page loading and navigation
- Weather widget display
- Orders table rendering and data validation
- Toggle orders functionality
- Revenue modal
- Search functionality
- Navigation to other pages

### `test_product_management.py`
Tests product management features including:
- Product table display and validation
- Add product modal and form
- Product search
- Form field validation
- UOM dropdown functionality
- Adding new products
- Action buttons (edit/delete)

### `test_order_creation.py`
Tests order creation workflow including:
- Order page loading
- Customer name input
- Adding/removing product items
- Product dropdown functionality
- Quantity and price calculations
- Grand total computation
- Save order functionality
- Form validation

## Helper Functions

### `helpers.py`
- `verify_field()`: Verify element matches validation rule
- `verify_input_value()`: Verify input field value
- `wait_for_table_rows()`: Wait for table to populate
- `fill_form_field()`: Fill form input with value
- `click_button()`: Click button with wait
- `select_dropdown_option()`: Select from dropdown
- `wait_for_alert()`: Wait for alert/toast message
- `get_table_cell_text()`: Extract text from table cell
- `verify_element_exists()`: Verify element presence
- `verify_element_not_exists()`: Verify element absence

### `validation.py`
Domain validators for GSM data:
- `is_valid_product_name()`: Product name format
- `is_valid_uom()`: Unit of measurement format
- `is_valid_price()`: Price format and range
- `is_valid_quantity()`: Quantity validation
- `is_valid_date()`: Date format validation
- `is_valid_datetime()`: Datetime format validation
- `is_valid_total()`: Total amount validation
- `is_valid_order_id()`: Order ID validation
- `is_valid_product_id()`: Product ID validation
- `is_valid_temperature()`: Temperature validation (weather widget)

## Fixtures

### `browser_page` (conftest.py)
Main fixture that provides:
- Chromium browser instance (headless by default)
- Automatically starts backend server before tests
- Navigates to UI homepage (`http://127.0.0.1:5000`)
- Cleans up browser and server after tests

## Configuration

The base URL for the UI is configured in `conftest.py`:
```python
BASE_URL = "http://127.0.0.1:5000"
```

To change the URL, modify this constant.

## Best Practices

1. **Wait Strategies**: Use `page.wait_for_selector()` and `page.wait_for_timeout()` appropriately
2. **Selectors**: Prefer ID selectors (`#elementId`) over complex CSS selectors when possible
3. **Validation**: Use validators from `validation.py` for consistent data validation
4. **Cleanup**: Tests should be independent and not rely on previous test state
5. **Timeouts**: Default timeout is 3000ms, adjust as needed for slow operations

## Troubleshooting

### Backend Not Starting
- Check that backend dependencies are installed
- Verify database connection in backend config
- Check for port conflicts on 5000

### Tests Timing Out
- Increase timeout values in helper functions
- Check network connectivity to backend
- Verify backend is responding to API calls

### Element Not Found
- Use `--headed` mode to visually inspect page
- Check that selectors match current HTML structure
- Verify page has loaded completely before interacting

### Data Validation Failures
- Ensure database has proper seed data
- Check data format matches validators in `validation.py`
- Verify backend API responses are correct

## Notes

- Tests run in **headless mode** by default for CI/CD compatibility
- Backend server is automatically started and stopped per test session
- Each test gets a fresh page context
- Browser state is not shared between tests
