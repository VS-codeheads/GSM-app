
def verify_field(scope, selector, validator, timeout=3000):
    scope.wait_for_selector(selector, state="visible", timeout=timeout)
    element = scope.query_selector(selector)
    assert element is not None, f"Element {selector} not found in scope"
    value = element.inner_text()
    assert validator(value), f"Validation failed for {selector}: {value}"


def verify_input_value(scope, selector, validator, timeout=3000):
    scope.wait_for_selector(selector, state="visible", timeout=timeout)
    element = scope.query_selector(selector)
    assert element is not None, f"Element {selector} not found in scope"
    value = element.input_value()
    assert validator(value), f"Validation failed for {selector}: {value}"


def wait_for_table_rows(page, table_selector, min_rows=1, timeout=5000):
    page.wait_for_selector(f"{table_selector} tbody tr", timeout=timeout)
    rows = page.query_selector_all(f"{table_selector} tbody tr")
    assert len(rows) >= min_rows, f"Expected at least {min_rows} rows, found {len(rows)}"
    return rows


def fill_form_field(page, selector, value, clear_first=True):
    page.wait_for_selector(selector, state="visible")
    if clear_first:
        page.fill(selector, "")
    page.fill(selector, str(value))


def click_button(page, selector, timeout=3000):
    page.wait_for_selector(selector, state="visible", timeout=timeout)
    page.click(selector)


def select_dropdown_option(page, selector, value):
    page.wait_for_selector(selector, state="visible")
    page.select_option(selector, value)


def wait_for_alert(page, expected_text=None, timeout=3000):
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
    cell = page.query_selector(f"{table_selector} tbody tr:nth-child({row_index + 1}) td:nth-child({col_index + 1})")
    assert cell is not None, f"Cell at row {row_index}, col {col_index} not found"
    return cell.inner_text().strip()


def verify_element_exists(page, selector, timeout=3000):
    page.wait_for_selector(selector, state="visible", timeout=timeout)
    element = page.query_selector(selector)
    assert element is not None, f"Element {selector} not found"


def verify_element_not_exists(page, selector, timeout=1000):
    try:
        page.wait_for_selector(selector, state="visible", timeout=timeout)
        raise AssertionError(f"Element {selector} should not exist but was found")
    except:
        pass  
