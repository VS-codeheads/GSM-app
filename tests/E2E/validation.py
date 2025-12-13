def assert_row_exists(page, text):
    assert page.locator(f"text={text}").count() > 0


def assert_modal_visible(page, modal_id):
    assert page.locator(modal_id).is_visible()


def assert_error_visible(page, message):
    assert page.locator(f"text={message}").is_visible()
