def assert_text_visible(page, text):
    """Assert that specific user-visible text is shown"""
    page.wait_for_selector(f"text={text}")
    assert page.locator(f"text={text}").is_visible()


def assert_modal_visible(page, modal_id):
    """Assert that a modal dialog is visible"""
    page.wait_for_selector(f"{modal_id}.show")
    assert page.locator(modal_id).is_visible()


def assert_modal_hidden(page, modal_id):
    """Assert that a modal dialog is closed"""
    page.wait_for_selector(modal_id, state="hidden")


def assert_select_has_options(page, selector):
    """Assert that a select element has at least one option"""
    page.wait_for_selector(f"{selector} option")
    assert page.locator(f"{selector} option").count() > 0


def assert_non_empty_container(page, selector):
    """Assert that a container has rendered output"""
    page.wait_for_function(
        f"document.querySelector('{selector}').innerText.trim().length > 0"
    )
