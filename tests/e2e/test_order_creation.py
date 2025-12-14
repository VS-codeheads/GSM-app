from .helpers import open_orders_page, fill_input, click
from .validation import assert_text_visible

def test_create_order(page):
    open_orders_page(page)

    fill_input(page, "#customerName", "E2E Customer")

    click(page, "#addMoreButton")

    page.wait_for_selector(".cart-product")
    page.select_option(".cart-product", index=1)

    fill_input(page, ".product-qty", "2")

    click(page, "#saveOrder")

    # User-visible success when the dashboard loads
    assert_text_visible(page, "Orders Overview")
