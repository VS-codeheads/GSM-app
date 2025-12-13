import sys
from pathlib import Path
import pytest

# Add project root to PYTHONPATH
root_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_path))

from backend.app import app
from backend.db.sql_connection import get_sql_connection
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()


@pytest.fixture(scope="session")
def flask_app():
    """
    Create Flask app instance for testing.
    Sets testing mode to disable error catching during request handling.
    """
    app.config["TESTING"] = True
    return app


@pytest.fixture
def client(flask_app):
    """
    Flask test client for making requests.
    """
    return flask_app.test_client()


@pytest.fixture
def db_conn():
    """
    Database connection for integration tests.
    Yields a connection that can be used for setup/validation.
    """
    conn = get_sql_connection()
    yield conn
    conn.close()


@pytest.fixture
def cleanup_products(db_conn):
    """
    Cleanup fixture that removes test products after each test.
    Returns a function that deletes products by their IDs.
    """
    created_ids = []
    
    yield lambda ids: created_ids.extend(ids)
    
    # Cleanup
    if created_ids:
        cursor = db_conn.cursor()
        for product_id in created_ids:
            cursor.execute("DELETE FROM order_details WHERE product_id = %s", (product_id,))
            cursor.execute("DELETE FROM products WHERE product_id = %s", (product_id,))
        db_conn.commit()


@pytest.fixture
def cleanup_orders(db_conn):
    """
    Cleanup fixture that removes test orders after each test.
    Returns a function that deletes orders by their IDs.
    """
    created_ids = []
    
    yield lambda ids: created_ids.extend(ids)
    
    # Cleanup
    if created_ids:
        cursor = db_conn.cursor()
        for order_id in created_ids:
            cursor.execute("DELETE FROM order_details WHERE order_id = %s", (order_id,))
            cursor.execute("DELETE FROM orders WHERE order_id = %s", (order_id,))
        db_conn.commit()
