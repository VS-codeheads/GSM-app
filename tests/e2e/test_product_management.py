from .helpers import open_manage_product, fill_input, click
from .validation import assert_modal_visible, assert_text_visible

def test_add_product_modal_flow(page):
    open_manage_product(page)

    click(page, "button:has-text('+ Add Product')")
    assert_modal_visible(page, "#productModal")

    fill_input(page, "#name", "E2E Apple")
    page.select_option("#uoms", index=0)
    fill_input(page, "#price", "5")
    fill_input(page, "#qty", "10")

    click(page, "#saveProduct")

    # User-visible success when product appears
    assert_text_visible(page, "E2E Apple")
