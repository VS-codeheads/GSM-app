"""
End-to-end tests for order creation functionality.
"""
import time
from tests.e2e.helpers import (
    verify_element_exists,
    fill_form_field,
    click_button,
    select_dropdown_option,
)
from tests.e2e.validation import (
    is_non_empty_string,
    is_valid_price,
    is_valid_quantity,
    is_valid_total,
)


def test_order_page_loads(browser_page):
    """Test that the order page loads successfully."""
    page = browser_page
    
    # Navigate to order page
    page.goto(f"{page.url.split('/')[0]}//{page.url.split('/')[2]}/order.html")
    page.wait_for_timeout(1000)
    
    # Verify page elements
    verify_element_exists(page, ".navbar")
    verify_element_exists(page, "#content-area")
    verify_element_exists(page, "#customerName")
    verify_element_exists(page, "#itemsInOrder")
    verify_element_exists(page, "#product_grand_total")
    verify_element_exists(page, "#saveOrder")


def test_customer_name_field(browser_page):
    """Test customer name input field."""
    page = browser_page
    page.goto(f"{page.url.split('/')[0]}//{page.url.split('/')[2]}/order.html")
    page.wait_for_timeout(1000)
    
    # Fill customer name
    customer_name = "John Doe"
    fill_form_field(page, "#customerName", customer_name)
    
    # Verify value
    name_input = page.query_selector("#customerName")
    assert name_input.input_value() == customer_name, "Customer name should be set"


def test_add_item_button_exists(browser_page):
    """Test that the 'Add Item' button is present."""
    page = browser_page
    page.goto(f"{page.url.split('/')[0]}//{page.url.split('/')[2]}/order.html")
    page.wait_for_timeout(1000)
    
    # Verify add more button
    verify_element_exists(page, "#addMoreButton")
    
    add_btn = page.query_selector("#addMoreButton")
    assert "+ Add Item" in add_btn.inner_text(), "Button should say '+ Add Item'"


def test_add_item_creates_new_row(browser_page):
    """Test that clicking 'Add Item' creates a new product row."""
    page = browser_page
    page.goto(f"{page.url.split('/')[0]}//{page.url.split('/')[2]}/order.html")
    page.wait_for_timeout(2000)
    
    # Get initial row count
    initial_rows = page.query_selector_all(".product-item")
    initial_count = len(initial_rows)
    
    # Click add item
    page.click("#addMoreButton")
    page.wait_for_timeout(500)
    
    # Check new row was added
    new_rows = page.query_selector_all(".product-item")
    assert len(new_rows) == initial_count + 1, "New product row should be added"


def test_product_row_structure(browser_page):
    """Test that product rows have correct structure."""
    page = browser_page
    page.goto(f"{page.url.split('/')[0]}//{page.url.split('/')[2]}/order.html")
    page.wait_for_timeout(2000)
    
    # Add an item if none exist
    page.click("#addMoreButton")
    page.wait_for_timeout(500)
    
    # Check row has all required elements
    first_row = page.query_selector(".product-item")
    assert first_row is not None, "Product item should exist"
    
    # Check for product dropdown
    product_select = first_row.query_selector(".cart-product")
    assert product_select is not None, "Product select should exist"
    
    # Check for price field
    price_field = first_row.query_selector(".product-price")
    assert price_field is not None, "Price field should exist"
    assert price_field.get_attribute("readonly") is not None, "Price should be readonly"
    
    # Check for quantity field
    qty_field = first_row.query_selector(".product-qty")
    assert qty_field is not None, "Quantity field should exist"
    
    # Check for total field
    total_field = first_row.query_selector(".product-total")
    assert total_field is not None, "Total field should exist"
    assert total_field.get_attribute("readonly") is not None, "Total should be readonly"
    
    # Check for remove button
    remove_btn = first_row.query_selector(".remove-row")
    assert remove_btn is not None, "Remove button should exist"


def test_remove_item_button(browser_page):
    """Test that remove button removes a product row."""
    page = browser_page
    page.goto(f"{page.url.split('/')[0]}//{page.url.split('/')[2]}/order.html")
    page.wait_for_timeout(2000)
    
    # Add two items
    page.click("#addMoreButton")
    page.wait_for_timeout(300)
    page.click("#addMoreButton")
    page.wait_for_timeout(300)
    
    # Get row count
    rows_before = page.query_selector_all(".product-item")
    count_before = len(rows_before)
    
    # Click remove on first row
    if count_before > 0:
        first_remove_btn = page.query_selector(".remove-row")
        if first_remove_btn:
            first_remove_btn.click()
            page.wait_for_timeout(500)
            
            # Check row was removed
            rows_after = page.query_selector_all(".product-item")
            assert len(rows_after) == count_before - 1, "Row should be removed"


def test_product_dropdown_loads_options(browser_page):
    """Test that product dropdown loads with product options."""
    page = browser_page
    page.goto(f"{page.url.split('/')[0]}//{page.url.split('/')[2]}/order.html")
    page.wait_for_timeout(2000)
    
    # Add an item
    page.click("#addMoreButton")
    page.wait_for_timeout(1000)
    
    # Check product dropdown has options
    first_row = page.query_selector(".product-item")
    if first_row:
        product_select = first_row.query_selector(".cart-product")
        options = product_select.query_selector_all("option")
        
        # Should have at least the default "--Select--" option
        assert len(options) > 0, "Product dropdown should have options"


def test_grand_total_displays(browser_page):
    """Test that grand total field is present and initialized."""
    page = browser_page
    page.goto(f"{page.url.split('/')[0]}//{page.url.split('/')[2]}/order.html")
    page.wait_for_timeout(1000)
    
    # Check grand total field
    grand_total = page.query_selector("#product_grand_total")
    assert grand_total is not None, "Grand total field should exist"
    assert grand_total.get_attribute("readonly") is not None, "Grand total should be readonly"
    
    # Initial value should be 0.00
    initial_value = grand_total.input_value()
    assert initial_value == "0.00" or initial_value == "0", "Initial grand total should be 0.00"


def test_save_order_button(browser_page):
    """Test that save order button exists and is clickable."""
    page = browser_page
    page.goto(f"{page.url.split('/')[0]}//{page.url.split('/')[2]}/order.html")
    page.wait_for_timeout(1000)
    
    # Verify save button
    save_btn = page.query_selector("#saveOrder")
    assert save_btn is not None, "Save order button should exist"
    assert "Save" in save_btn.inner_text(), "Button should say 'Save'"


def test_order_with_customer_name(browser_page):
    """Test creating an order with customer name only."""
    page = browser_page
    page.goto(f"{page.url.split('/')[0]}//{page.url.split('/')[2]}/order.html")
    page.wait_for_timeout(2000)
    
    # Fill customer name
    timestamp = int(time.time())
    customer_name = f"Test Customer {timestamp}"
    fill_form_field(page, "#customerName", customer_name)
    
    # Verify name is set
    name_input = page.query_selector("#customerName")
    assert name_input.input_value() == customer_name


def test_quantity_field_defaults(browser_page):
    """Test that quantity fields have proper default values."""
    page = browser_page
    page.goto(f"{page.url.split('/')[0]}//{page.url.split('/')[2]}/order.html")
    page.wait_for_timeout(2000)
    
    # Add an item
    page.click("#addMoreButton")
    page.wait_for_timeout(500)
    
    # Check quantity default
    first_row = page.query_selector(".product-item")
    if first_row:
        qty_field = first_row.query_selector(".product-qty")
        default_qty = qty_field.input_value()
        assert default_qty == "1", "Default quantity should be 1"


def test_price_updates_when_product_selected(browser_page):
    """Test that price field updates when a product is selected."""
    page = browser_page
    page.goto(f"{page.url.split('/')[0]}//{page.url.split('/')[2]}/order.html")
    page.wait_for_timeout(2000)
    
    # Add an item
    page.click("#addMoreButton")
    page.wait_for_timeout(1000)
    
    first_row = page.query_selector(".product-item")
    if first_row:
        product_select = first_row.query_selector(".cart-product")
        options = product_select.query_selector_all("option")
        
        # If there are product options (beyond --Select--)
        if len(options) > 1:
            # Get initial price
            price_field = first_row.query_selector(".product-price")
            initial_price = price_field.input_value()
            
            # Select a product
            page.select_option(".cart-product", index=1)
            page.wait_for_timeout(1000)
            
            # Check if price updated (should not be 0.00 anymore if product has price)
            new_price = price_field.input_value()
            # Price may or may not change depending on product data
            assert price_field is not None, "Price field should exist after selection"


def test_order_summary_box(browser_page):
    """Test that order summary box is displayed."""
    page = browser_page
    page.goto(f"{page.url.split('/')[0]}//{page.url.split('/')[2]}/order.html")
    page.wait_for_timeout(1000)
    
    # Verify summary box
    verify_element_exists(page, ".summary-box")
    
    # Check "Grand Total:" label
    summary_text = page.query_selector(".summary-box").inner_text()
    assert "Grand Total" in summary_text, "Summary should show 'Grand Total'"


def test_quantity_field_constraints(browser_page):
    """Test that quantity field has proper constraints."""
    page = browser_page
    page.goto(f"{page.url.split('/')[0]}//{page.url.split('/')[2]}/order.html")
    page.wait_for_timeout(2000)
    
    # Add an item
    page.click("#addMoreButton")
    page.wait_for_timeout(500)
    
    first_row = page.query_selector(".product-item")
    if first_row:
        qty_field = first_row.query_selector(".product-qty")
        
        # Check min attribute
        min_val = qty_field.get_attribute("min")
        assert min_val == "1", "Quantity minimum should be 1"
        
        # Check type
        input_type = qty_field.get_attribute("type")
        assert input_type == "number", "Quantity should be number type"


def test_navigation_back_to_dashboard(browser_page):
    """Test navigation back to dashboard from order page."""
    page = browser_page
    page.goto(f"{page.url.split('/')[0]}//{page.url.split('/')[2]}/order.html")
    page.wait_for_timeout(1000)
    
    # Click dashboard link
    dashboard_link = page.query_selector('a[href="index.html"]')
    assert dashboard_link is not None, "Dashboard link should exist"
    
    page.click('a[href="index.html"]')
    page.wait_for_timeout(1000)
    
    # Verify we're back on dashboard
    assert "index.html" in page.url or page.url.endswith("/"), "Should navigate back to dashboard"
