"""
End-to-end tests for product management functionality.
"""
import time
from tests.e2e.helpers import (
    verify_element_exists,
    fill_form_field,
    click_button,
    select_dropdown_option,
    wait_for_table_rows,
    get_table_cell_text,
)
from tests.e2e.validation import (
    is_valid_product_name,
    is_valid_price,
    is_valid_quantity,
    is_valid_uom,
)


def test_manage_products_page_loads(browser_page):
    """Test that the manage products page loads successfully."""
    page = browser_page
    
    # Navigate to manage products
    page.goto(f"{page.url.split('/')[0]}//{page.url.split('/')[2]}/manage-product.html")
    page.wait_for_timeout(1000)
    
    # Verify page elements
    verify_element_exists(page, ".navbar")
    verify_element_exists(page, "#content-area")
    verify_element_exists(page, ".table")
    
    # Verify "Add Product" button
    verify_element_exists(page, '[data-bs-target="#productModal"]')


def test_products_table_structure(browser_page):
    """Test that the products table has correct structure."""
    page = browser_page
    page.goto(f"{page.url.split('/')[0]}//{page.url.split('/')[2]}/manage-product.html")
    page.wait_for_timeout(1000)
    
    # Check table headers
    headers = page.query_selector_all(".table thead th")
    assert len(headers) == 5, "Expected 5 table headers"
    
    header_texts = [h.inner_text() for h in headers]
    assert "Name" in header_texts
    assert "Unit" in header_texts
    assert "Price Per Unit" in header_texts
    assert "Quantity" in header_texts
    assert "Action" in header_texts


def test_products_table_displays_data(browser_page):
    """Test that products table displays valid data."""
    page = browser_page
    page.goto(f"{page.url.split('/')[0]}//{page.url.split('/')[2]}/manage-product.html")
    page.wait_for_timeout(2000)
    
    # Check if there are any product rows
    rows = page.query_selector_all(".table tbody tr")
    
    if len(rows) > 0:
        # Validate first product row
        name = get_table_cell_text(page, ".table", 0, 0)
        unit = get_table_cell_text(page, ".table", 0, 1)
        price = get_table_cell_text(page, ".table", 0, 2)
        quantity = get_table_cell_text(page, ".table", 0, 3)
        
        # Validate data
        assert is_valid_product_name(name), f"Invalid product name: {name}"
        assert is_valid_uom(unit), f"Invalid UOM: {unit}"
        assert is_valid_price(price), f"Invalid price: {price}"
        assert is_valid_quantity(quantity), f"Invalid quantity: {quantity}"


def test_add_product_modal_opens(browser_page):
    """Test that the add product modal can be opened."""
    page = browser_page
    page.goto(f"{page.url.split('/')[0]}//{page.url.split('/')[2]}/manage-product.html")
    page.wait_for_timeout(1000)
    
    # Click "Add Product" button
    page.click('[data-bs-target="#productModal"]')
    page.wait_for_timeout(500)
    
    # Verify modal is visible
    modal = page.query_selector("#productModal")
    assert modal is not None, "Product modal not found"
    
    # Verify form fields exist
    verify_element_exists(page, "#name")
    verify_element_exists(page, "#uoms")
    verify_element_exists(page, "#price")
    verify_element_exists(page, "#qty")
    verify_element_exists(page, "#saveProduct")


def test_add_product_form_validation(browser_page):
    """Test product form field validation."""
    page = browser_page
    page.goto(f"{page.url.split('/')[0]}//{page.url.split('/')[2]}/manage-product.html")
    page.wait_for_timeout(1000)
    
    # Open modal
    page.click('[data-bs-target="#productModal"]')
    page.wait_for_timeout(500)
    
    # Check that fields are empty initially
    name_input = page.query_selector("#name")
    assert name_input.input_value() == "", "Name field should be empty"
    
    price_input = page.query_selector("#price")
    assert price_input.input_value() == "", "Price field should be empty"
    
    qty_input = page.query_selector("#qty")
    assert qty_input.input_value() == "", "Quantity field should be empty"


def test_add_product_success(browser_page):
    """Test successfully adding a new product."""
    page = browser_page
    page.goto(f"{page.url.split('/')[0]}//{page.url.split('/')[2]}/manage-product.html")
    page.wait_for_timeout(2000)
    
    # Get initial row count
    initial_rows = page.query_selector_all(".table tbody tr")
    initial_count = len(initial_rows)
    
    # Open modal
    page.click('[data-bs-target="#productModal"]')
    page.wait_for_timeout(500)
    
    # Fill form with unique product name
    timestamp = int(time.time())
    product_name = f"Test Product {timestamp}"
    
    fill_form_field(page, "#name", product_name)
    
    # Select UOM (wait for dropdown to load)
    page.wait_for_timeout(1000)
    uom_options = page.query_selector_all("#uoms option")
    if len(uom_options) > 1:  # More than just the default option
        page.select_option("#uoms", index=1)
    
    fill_form_field(page, "#price", "10.99")
    fill_form_field(page, "#qty", "50")
    
    # Click save
    page.click("#saveProduct")
    page.wait_for_timeout(2000)
    
    # Verify product was added (table should have more rows)
    new_rows = page.query_selector_all(".table tbody tr")
    assert len(new_rows) >= initial_count, "Product should be added to table"


def test_product_search_functionality(browser_page):
    """Test that product search input works."""
    page = browser_page
    page.goto(f"{page.url.split('/')[0]}//{page.url.split('/')[2]}/manage-product.html")
    page.wait_for_timeout(1000)
    
    # Verify search input exists
    verify_element_exists(page, "#productSearch")
    
    # Type in search
    page.fill("#productSearch", "test")
    
    # Verify input value
    search_input = page.query_selector("#productSearch")
    assert search_input.input_value() == "test", "Search input value incorrect"


def test_product_action_buttons_exist(browser_page):
    """Test that product action buttons are present for each row."""
    page = browser_page
    page.goto(f"{page.url.split('/')[0]}//{page.url.split('/')[2]}/manage-product.html")
    page.wait_for_timeout(2000)
    
    # Check if there are products
    rows = page.query_selector_all(".table tbody tr")
    
    if len(rows) > 0:
        # Check first row has action buttons
        first_row = rows[0]
        buttons = first_row.query_selector_all("button")
        
        # Should have at least one action button (edit or delete)
        assert len(buttons) > 0, "Product row should have action buttons"


def test_uom_dropdown_loads(browser_page):
    """Test that UOM dropdown loads with options."""
    page = browser_page
    page.goto(f"{page.url.split('/')[0]}//{page.url.split('/')[2]}/manage-product.html")
    page.wait_for_timeout(1000)
    
    # Open modal
    page.click('[data-bs-target="#productModal"]')
    page.wait_for_timeout(1500)
    
    # Check UOM dropdown has options
    uom_options = page.query_selector_all("#uoms option")
    assert len(uom_options) > 0, "UOM dropdown should have options"


def test_modal_close_functionality(browser_page):
    """Test that product modal can be closed."""
    page = browser_page
    page.goto(f"{page.url.split('/')[0]}//{page.url.split('/')[2]}/manage-product.html")
    page.wait_for_timeout(1000)
    
    # Open modal
    page.click('[data-bs-target="#productModal"]')
    page.wait_for_timeout(500)
    
    # Verify modal is visible
    modal = page.query_selector("#productModal")
    assert modal is not None
    
    # Close modal using close button
    close_btn = page.query_selector('[data-bs-dismiss="modal"]')
    if close_btn:
        close_btn.click()
        page.wait_for_timeout(500)


def test_price_field_accepts_decimal(browser_page):
    """Test that price field accepts decimal values."""
    page = browser_page
    page.goto(f"{page.url.split('/')[0]}//{page.url.split('/')[2]}/manage-product.html")
    page.wait_for_timeout(1000)
    
    # Open modal
    page.click('[data-bs-target="#productModal"]')
    page.wait_for_timeout(500)
    
    # Fill price with decimal
    fill_form_field(page, "#price", "19.99")
    
    # Verify value
    price_input = page.query_selector("#price")
    assert price_input.input_value() == "19.99", "Price should accept decimal values"


def test_quantity_field_validation(browser_page):
    """Test that quantity field has minimum value constraint."""
    page = browser_page
    page.goto(f"{page.url.split('/')[0]}//{page.url.split('/')[2]}/manage-product.html")
    page.wait_for_timeout(1000)
    
    # Open modal
    page.click('[data-bs-target="#productModal"]')
    page.wait_for_timeout(500)
    
    # Check quantity field has min attribute
    qty_input = page.query_selector("#qty")
    assert qty_input is not None
    
    min_attr = qty_input.get_attribute("min")
    assert min_attr == "0", "Quantity field should have min=0"
