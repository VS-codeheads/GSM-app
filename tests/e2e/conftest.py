import pytest
from playwright.sync_api import sync_playwright

BASE_URL = "http://127.0.0.1:8000"

@pytest.fixture(scope="session")
def browser():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,  # change to False locally if needed to get UI visually
            slow_mo=50      # helps to debug flakiness
        )
        yield browser
        browser.close()


@pytest.fixture
def page(browser):
    context = browser.new_context(
        viewport={"width": 1280, "height": 800}
    )
    page = context.new_page()
    page.goto(f"{BASE_URL}/index.html")
    yield page
    context.close()