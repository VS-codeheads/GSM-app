from helpers import open_manage_product, fill_input, click

def test_add_product_modal_flow(page):
    open_manage_product(page)

    # Open modal
    click(page, "button:has-text('+ Add Product')")
    page.wait_for_selector("#productModal.show")

    # Fill form
    fill_input(page, "#name", "E2E Apple")
    page.select_option("#uoms", index=0)
    fill_input(page, "#price", "5")
    fill_input(page, "#qty", "10")

    # Click save
    click(page, "#saveProduct")

    # Modal should close (user-visible success)
    page.wait_for_selector("#productModal", state="hidden")




