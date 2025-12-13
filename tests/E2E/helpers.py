def open_dashboard(page):
    page.goto("http://127.0.0.1:8000/index.html")
    page.wait_for_selector("#ordersTableBody")


def open_manage_product(page):
    page.goto("http://127.0.0.1:8000/manage-product.html")
    page.wait_for_selector("table")


def open_orders_page(page):
    page.goto("http://127.0.0.1:8000/order.html")
    page.wait_for_selector("#customerName")


def fill_input(page, selector, value):
    page.wait_for_selector(selector)
    page.fill(selector, str(value))


def click(page, selector):
    page.wait_for_selector(selector)
    page.click(selector)
