import pytest
from playwright.sync_api import sync_playwright
import subprocess
import time
import os


def _launch_browser(p):
    """Launch a browser with fallbacks to avoid segfaults on some macOS setups."""
    headless = os.environ.get("HEADLESS", "1") not in {"0", "false", "False"}
    launch_args = {
        "headless": headless,
        "args": ["--no-sandbox"],
    }

    chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

    try:
        return p.chromium.launch(**launch_args)
    except Exception:
        pass

    if os.path.exists(chrome_path):
        try:
            return p.chromium.launch(**launch_args, executable_path=chrome_path)
        except Exception:
            pass

    for browser_type in (p.webkit, p.firefox):
        try:
            return browser_type.launch(**launch_args)
        except Exception:
            continue

    raise RuntimeError("Failed to launch any Playwright browser (chromium/webkit/firefox)")

# Base URL for the frontend
BASE_URL = "http://127.0.0.1:8000"
API_URL = "http://127.0.0.1:5000"


@pytest.fixture(scope="session")
def backend_server():
    """
    Start the Flask backend server before tests and stop it after.
    """
    # Set environment variables
    env = os.environ.copy()
    
    # Start backend server
    process = subprocess.Popen(
        ["python", "-m", "backend.app"],
        cwd="/Users/sofiethorlund/GSM-app tests/GSM-app",
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    
    # Wait for server to start
    time.sleep(3)
    
    yield process
    
    # Cleanup
    process.terminate()
    process.wait()


@pytest.fixture(scope="session")
def frontend_server():
    """
    Start a simple HTTP server for the frontend.
    """
    process = subprocess.Popen(
        ["python", "-m", "http.server", "8000"],
        cwd="/Users/viktorbach/GSM-app tests/GSM-app/UI",
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    
    # Wait for server to start
    time.sleep(2)
    
    yield process
    
    # Cleanup
    process.terminate()
    process.wait()


@pytest.fixture
def browser_page(backend_server, frontend_server):
    """
    Provides a Playwright browser page instance for each test.
    """
    with sync_playwright() as p:
        browser = _launch_browser(p)
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080}
        )
        page = context.new_page()

        # Navigate to base URL so tests that rely on browser_page start loaded
        page.goto(f"{BASE_URL}/index.html")
        page.wait_for_load_state("networkidle")
        
        yield page
        
        context.close()
        browser.close()


@pytest.fixture
def dashboard_page(browser_page):
    """
    Navigate to dashboard and return the page.
    """
    browser_page.goto(f"{BASE_URL}/index.html")
    browser_page.wait_for_load_state("networkidle")
    return browser_page


@pytest.fixture
def products_page(browser_page):
    """
    Navigate to manage products page and return the page.
    """
    browser_page.goto(f"{BASE_URL}/manage-product.html")
    browser_page.wait_for_load_state("networkidle")
    return browser_page


@pytest.fixture
def orders_page(browser_page):
    """
    Navigate to orders page and return the page.
    """
    browser_page.goto(f"{BASE_URL}/order.html")
    browser_page.wait_for_load_state("networkidle")
    return browser_page
