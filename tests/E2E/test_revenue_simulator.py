from .helpers import open_dashboard
from .validation import (
    assert_modal_visible,
    assert_select_has_options,
    assert_non_empty_container,
)

def test_revenue_simulation_flow(page):
    open_dashboard(page)

    page.click("button:has-text('Revenue Simulation')")
    assert_modal_visible(page, "#revenueModal")

    assert_select_has_options(page, "#sim-products")

    page.select_option("#sim-products", index=0)
    page.fill("#sim-days", "3")

    page.click("#run-simulation")

    # User-visible simulation finished when button re-enabled
    page.wait_for_selector("#run-simulation:not([disabled])")
