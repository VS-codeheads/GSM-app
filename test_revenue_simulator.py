from helpers import open_dashboard

def test_revenue_simulation_flow(page):
    open_dashboard(page)

    # Open modal
    page.click("button:has-text('Revenue Simulation')")
    page.wait_for_selector("#revenueModal.show")

    # Products loaded
    page.wait_for_selector("#sim-products option")

    # User input
    page.select_option("#sim-products", index=0)
    page.fill("#sim-days", "3")

    # Run simulation
    page.click("#run-simulation")

    # Result container should exist and not be empty
    page.wait_for_function(
        "document.querySelector('#sim-result').innerText.length > 0"
    )





