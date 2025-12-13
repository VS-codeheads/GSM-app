"""
End-to-end tests for dashboard functionality.
"""
from tests.e2e.helpers import (
    verify_element_exists,
    wait_for_table_rows,
    get_table_cell_text,
)
from tests.e2e.validation import (
    is_valid_date,
    is_valid_order_id,
    is_non_empty_string,
    is_valid_total,
)


def test_dashboard_loads(browser_page):
    """Test that the dashboard page loads successfully."""
    page = browser_page
    
    # Verify navbar is present
    verify_element_exists(page, ".navbar")
    verify_element_exists(page, ".navbar-brand")
    
    # Verify main content area
    verify_element_exists(page, "#content-area")
    
    # Verify navigation links
    verify_element_exists(page, 'a[href="index.html"]')
    verify_element_exists(page, 'a[href="manage-product.html"]')
    verify_element_exists(page, 'a[href="order.html"]')


def test_weather_widget_displays(browser_page):
    """Test that the weather widget loads and displays data."""
    page = browser_page
    
    # Verify weather widget exists
    verify_element_exists(page, "#weatherWidget", timeout=5000)
    verify_element_exists(page, "#weatherContent", timeout=5000)
    
    # Wait for weather to load (should replace "Loading weather...")
    page.wait_for_timeout(2000)
    
    weather_content = page.query_selector("#weatherContent")
    text = weather_content.inner_text() if weather_content else ""
    
    # Weather should have loaded or show error
    assert text != "Loading weather...", "Weather widget still showing loading message"


def test_orders_table_displays(browser_page):
    """Test that the orders table loads and displays data."""
    page = browser_page
    
    # Verify table structure
    verify_element_exists(page, ".table")
    verify_element_exists(page, "#ordersTableBody")
    
    # Wait for table to populate (or remain empty if no orders)
    page.wait_for_timeout(2000)
    
    # Check table headers
    headers = page.query_selector_all(".table thead th")
    assert len(headers) == 4, "Expected 4 table headers"
    
    header_texts = [h.inner_text() for h in headers]
    assert "Date" in header_texts
    assert "Order #" in header_texts
    assert "Customer" in header_texts
    assert "Total" in header_texts


def test_orders_table_with_data(browser_page):
    """Test that orders table displays valid data when orders exist."""
    page = browser_page
    
    # Wait for orders to load
    page.wait_for_timeout(2000)
    
    # Check if there are any rows
    rows = page.query_selector_all("#ordersTableBody tr")
    
    if len(rows) > 0:
        # Validate first row data
        date_text = get_table_cell_text(page, ".table", 0, 0)
        order_num = get_table_cell_text(page, ".table", 0, 1)
        customer = get_table_cell_text(page, ".table", 0, 2)
        total = get_table_cell_text(page, ".table", 0, 3)
        
        # Validate data types
        # Accept multiple date formats as rendered by the UI
        assert is_valid_date(date_text) or is_valid_datetime(date_text), f"Invalid date: {date_text}"
        assert is_valid_order_id(order_num), f"Invalid order ID: {order_num}"
        assert is_non_empty_string(customer), f"Invalid customer name: {customer}"
        assert is_valid_total(total), f"Invalid total: {total}"


def test_toggle_orders_button(browser_page):
    """Test the toggle orders button functionality."""
    page = browser_page
    
    # Find toggle button
    toggle_btn = page.query_selector("#toggleOrdersBtn")
    assert toggle_btn is not None, "Toggle orders button not found"
    
    initial_text = toggle_btn.inner_text()
    
    # Click toggle
    page.click("#toggleOrdersBtn")
    page.wait_for_timeout(1000)
    
    # Check if text changed
    new_text = toggle_btn.inner_text()
    assert new_text != initial_text, "Toggle button text should change"


def test_revenue_modal_opens(browser_page):
    """Test that the revenue simulation modal can be opened."""
    page = browser_page
    
    # Click revenue button
    revenue_btn = page.query_selector('[data-bs-target="#revenueModal"]')
    if revenue_btn:
        page.click('[data-bs-target="#revenueModal"]')
        page.wait_for_timeout(500)
        
        # Check if modal appears
        modal = page.query_selector("#revenueModal")
        if modal:
            # Modal should be visible
            assert modal.is_visible(), "Revenue modal should be visible after clicking button"


def test_order_search_functionality(browser_page):
    """Test that the order search input is functional."""
    page = browser_page
    
    # Verify search input exists
    verify_element_exists(page, "#orderSearch")
    
    # Type in search box
    page.fill("#orderSearch", "test customer")
    
    # Verify input value
    search_input = page.query_selector("#orderSearch")
    assert search_input.input_value() == "test customer", "Search input value incorrect"


def test_navigation_to_new_order(browser_page):
    """Test navigation to new order page."""
    page = browser_page
    
    # Click "New Order" button
    new_order_link = page.query_selector('a[href="order.html"]')
    assert new_order_link is not None, "New Order link not found"
    
    page.click('a[href="order.html"]')
    page.wait_for_timeout(1000)
    
    # Verify we're on order page
    assert "order.html" in page.url, "Should navigate to order.html"


def test_navigation_to_manage_products(browser_page):
    """Test navigation to manage products page."""
    page = browser_page
    
    # Click "Manage Products" button
    manage_link = page.query_selector('a[href="manage-product.html"]')
    assert manage_link is not None, "Manage Products link not found"
    
    page.click('a[href="manage-product.html"]')
    page.wait_for_timeout(1000)
    
    # Verify we're on manage-product page
    assert "manage-product.html" in page.url, "Should navigate to manage-product.html"


def test_dashboard_responsive_navbar(browser_page):
    """Test that navbar elements are present and functional."""
    page = browser_page
    
    # Verify navbar brand
    brand = page.query_selector(".navbar-brand")
    assert brand is not None, "Navbar brand not found"
    assert "GSMS" in brand.inner_text(), "Navbar brand should contain 'GSMS'"
    
    # Verify nav links
    nav_links = page.query_selector_all(".nav-link")
    assert len(nav_links) >= 3, "Should have at least 3 navigation links"


# Import datetime for datetime validation
from tests.e2e.validation import is_valid_datetime
