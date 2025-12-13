import pytest
from unittest.mock import MagicMock

from backend.dao.products_dao import (
    get_all_products,
    insert_new_product,
    delete_product,
    update_product
)

def mock_connection():
    conn = MagicMock()
    cursor = MagicMock()
    conn.cursor.return_value = cursor
    return conn, cursor


# ---------------------------
# GET ALL PRODUCTS
# ---------------------------
def test_get_all_products_returns_list():
    """EP - Valid DB rows should be converted to dicts correctly"""
    conn, cursor = mock_connection()

    # Simulate cursor iteration
    cursor.__iter__.return_value = [
        (1, "Apple", 1, 2.5, 100, "kg"),
        (2, "Milk", 2, 1.2, 50, "liter")
    ]

    products = get_all_products(conn)

    assert len(products) == 2
    assert products[0]["name"] == "Apple"
    assert products[0]["price_per_unit"] == 2.5
    assert products[1]["uom_name"] == "liter"

    cursor.execute.assert_called_once()


def test_get_all_products_empty_result():
    """BVA - No rows in DB should return empty an list"""
    conn, cursor = mock_connection()
    cursor.__iter__.return_value = []

    products = get_all_products(conn)

    assert products == []


# ------------------------------
# INSERT NEW PRODUCT
# ------------------------------
def test_insert_new_product_success():
    """EP - Valid product should insert and return a new ID"""
    conn, cursor = mock_connection()
    cursor.lastrowid = 42

    product = {
        "name": "Banana",
        "uom_id": 1,
        "price_per_unit": 1.5,
        "quantity": 30
    }

    new_id = insert_new_product(conn, product)

    assert new_id == 42
    cursor.execute.assert_called_once()
    conn.commit.assert_called_once()


def test_insert_new_product_type_casting():
    """BVA - Numeric fields passed as strings are cast correctly"""
    conn, cursor = mock_connection()
    cursor.lastrowid = 1

    product = {
        "name": "Orange",
        "uom_id": "2",
        "price_per_unit": "3.25",
        "quantity": "10"
    }

    insert_new_product(conn, product)

    args = cursor.execute.call_args.args
    data = args[1]

    assert data == ("Orange", 2, 3.25, 10)


# ------------------------------
# DELETE PRODUCT
# ------------------------------
def test_delete_product_existing():
    """Decision table - Existing product = rowcount = 1"""
    conn, cursor = mock_connection()
    cursor.rowcount = 1

    rows = delete_product(conn, 5)

    assert rows == 1
    cursor.execute.assert_called_once_with(
        "DELETE FROM products WHERE product_id = %s",
        (5,)
    )
    conn.commit.assert_called_once()


def test_delete_product_non_existing():
    """Decision table - Non-existing product = rowcount = 0"""
    conn, cursor = mock_connection()
    cursor.rowcount = 0

    rows = delete_product(conn, 999)

    assert rows == 0


# --------------------------------
# UPDATE PRODUCT
# --------------------------------
def test_update_product_success():
    """EP - Valid update returns affected rows"""
    conn, cursor = mock_connection()
    cursor.rowcount = 1

    product = {
        "product_id": 3,
        "name": "Cheese",
        "uom_id": 1,
        "price_per_unit": 4.5,
        "quantity": 20
    }

    rows = update_product(conn, product)

    assert rows == 1
    cursor.execute.assert_called_once()
    conn.commit.assert_called_once()


def test_update_product_no_match():
    """Decision table - product_id not found = 0 rows updated"""
    conn, cursor = mock_connection()
    cursor.rowcount = 0

    product = {
        "product_id": 999,
        "name": "Ghost",
        "uom_id": 1,
        "price_per_unit": 1.0,
        "quantity": 1
    }

    rows = update_product(conn, product)

    assert rows == 0


def test_update_product_type_casting():
    """BVA - String numbers should be cast to correct numeric types"""
    conn, cursor = mock_connection()
    cursor.rowcount = 1

    product = {
        "product_id": "10",
        "name": "Yogurt",
        "uom_id": "2",
        "price_per_unit": "1.99",
        "quantity": "5"
    }

    update_product(conn, product)

    args = cursor.execute.call_args.args
    data = args[1]

    assert data == ("Yogurt", 2, 1.99, 5, 10)
