import os
import pytest
from playwright.sync_api import sync_playwright

BASE_URL = "http://127.0.0.1:8000"
SYSTEM_CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

@pytest.fixture(scope="session")
def browser():
    with sync_playwright() as p:
        launch_args = {"headless": False, "args": ["--no-sandbox"]}
        if os.path.exists(SYSTEM_CHROME):
            launch_args["executable_path"] = SYSTEM_CHROME
        browser = p.chromium.launch(**launch_args)
        yield browser
        browser.close()

@pytest.fixture
def page(browser):
    context = browser.new_context(viewport={"width": 1280, "height": 800})
    page = context.new_page()
    page.goto(f"{BASE_URL}/index.html")
    yield page
    context.close()