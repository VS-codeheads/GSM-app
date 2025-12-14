from helpers import open_orders_page, fill_input, click

def test_create_order(page):
    open_orders_page(page)

    fill_input(page, "#customerName", "E2E Customer")

    click(page, "#addMoreButton")

    page.wait_for_selector(".cart-product")
    page.select_option(".cart-product", index=1)

    fill_input(page, ".product-qty", "2")

    click(page, "#saveOrder")

    page.wait_for_timeout(1000)
    assert page.url.endswith("index.html")
