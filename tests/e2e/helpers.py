"""
Helper functions for E2E tests.
"""


def verify_field(scope, selector, validator, timeout=3000):
    """
    Verify that a field matches a validation rule.
    
    Args:
        scope: Playwright page or locator
        selector: CSS selector for the element
        validator: Function that returns True if value is valid
        timeout: Timeout in milliseconds
    """
    scope.wait_for_selector(selector, state="visible", timeout=timeout)
    element = scope.query_selector(selector)
    assert element is not None, f"Element {selector} not found in scope"
    value = element.inner_text()
    assert validator(value), f"Validation failed for {selector}: {value}"


def verify_input_value(scope, selector, validator, timeout=3000):
    """
    Verify that an input field value matches a validation rule.
    
    Args:
        scope: Playwright page or locator
        selector: CSS selector for the input element
        validator: Function that returns True if value is valid
        timeout: Timeout in milliseconds
    """
    scope.wait_for_selector(selector, state="visible", timeout=timeout)
    element = scope.query_selector(selector)
    assert element is not None, f"Element {selector} not found in scope"
    value = element.input_value()
    assert validator(value), f"Validation failed for {selector}: {value}"


def wait_for_table_rows(page, table_selector, min_rows=1, timeout=5000):
    """
    Wait for a table to have at least min_rows rows.
    
    Args:
        page: Playwright page
        table_selector: CSS selector for the table
        min_rows: Minimum number of rows expected
        timeout: Timeout in milliseconds
    
    Returns:
        List of row elements
    """
    page.wait_for_selector(f"{table_selector} tbody tr", timeout=timeout)
    rows = page.query_selector_all(f"{table_selector} tbody tr")
    assert len(rows) >= min_rows, f"Expected at least {min_rows} rows, found {len(rows)}"
    return rows


def fill_form_field(page, selector, value, clear_first=True):
    """
    Fill a form field with a value.
    
    Args:
        page: Playwright page
        selector: CSS selector for the input
        value: Value to enter
        clear_first: Whether to clear the field first
    """
    page.wait_for_selector(selector, state="visible")
    if clear_first:
        page.fill(selector, "")
    page.fill(selector, str(value))


def click_button(page, selector, timeout=3000):
    """
    Click a button and wait for it to be clickable.
    
    Args:
        page: Playwright page
        selector: CSS selector for the button
        timeout: Timeout in milliseconds
    """
    page.wait_for_selector(selector, state="visible", timeout=timeout)
    page.click(selector)


def select_dropdown_option(page, selector, value):
    """
    Select an option from a dropdown.
    
    Args:
        page: Playwright page
        selector: CSS selector for the select element
        value: Value to select
    """
    page.wait_for_selector(selector, state="visible")
    page.select_option(selector, value)


def wait_for_alert(page, expected_text=None, timeout=3000):
    """
    Wait for an alert/toast message to appear.
    
    Args:
        page: Playwright page
        expected_text: Optional text to verify in the alert
        timeout: Timeout in milliseconds
    """
    # Wait for common alert selectors
    alert_selectors = [".alert", ".toast", "[role='alert']"]
    
    for selector in alert_selectors:
        try:
            page.wait_for_selector(selector, state="visible", timeout=timeout)
            if expected_text:
                element = page.query_selector(selector)
                if element and expected_text in element.inner_text():
                    return True
            return True
        except:
            continue
    
    if expected_text:
        raise AssertionError(f"Alert with text '{expected_text}' not found")
    raise AssertionError("No alert found")


def get_table_cell_text(page, table_selector, row_index, col_index):
    """
    Get text from a specific table cell.
    
    Args:
        page: Playwright page
        table_selector: CSS selector for the table
        row_index: 0-based row index
        col_index: 0-based column index
    
    Returns:
        Text content of the cell
    """
    cell = page.query_selector(f"{table_selector} tbody tr:nth-child({row_index + 1}) td:nth-child({col_index + 1})")
    assert cell is not None, f"Cell at row {row_index}, col {col_index} not found"
    return cell.inner_text().strip()


def verify_element_exists(page, selector, timeout=3000):
    """
    Verify that an element exists on the page.
    
    Args:
        page: Playwright page
        selector: CSS selector for the element
        timeout: Timeout in milliseconds
    """
    page.wait_for_selector(selector, state="visible", timeout=timeout)
    element = page.query_selector(selector)
    assert element is not None, f"Element {selector} not found"


def verify_element_not_exists(page, selector, timeout=1000):
    """
    Verify that an element does not exist on the page.
    
    Args:
        page: Playwright page
        selector: CSS selector for the element
        timeout: Timeout in milliseconds
    """
    try:
        page.wait_for_selector(selector, state="visible", timeout=timeout)
        raise AssertionError(f"Element {selector} should not exist but was found")
    except:
        pass  # Expected - element not found
