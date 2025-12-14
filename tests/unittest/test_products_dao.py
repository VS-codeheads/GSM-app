import pytest
from unittest.mock import MagicMock

from backend.dao.products_dao import (
    get_all_products,
    insert_new_product,
    delete_product,
    update_product
)

# -------------------------------------------------
# FIXTURE: Mock DB connection + cursor
# -------------------------------------------------
@pytest.fixture
def mock_connection():
    conn = MagicMock()
    cursor = MagicMock()
    conn.cursor.return_value = cursor
    return conn, cursor


# -------------------------------------------------
# GET ALL PRODUCTS
# -------------------------------------------------
def test_get_all_products_returns_list(mock_connection):
    """EP: Valid DB rows are converted to dicts correctly"""
    conn, cursor = mock_connection

    cursor.__iter__.return_value = [
        (1, "Apple", 1, 2.5, 5.0, 100, "kg"),
        (2, "Milk", 2, 1.2, 3.0, 50, "liter"),
    ]

    products = get_all_products(conn)

    assert len(products) == 2
    assert products[0]["name"] == "Apple"
    assert products[0]["price_per_unit"] == 2.5
    assert products[0]["selling_price"] == 5.0
    assert products[1]["uom_name"] == "liter"

    cursor.execute.assert_called_once()


def test_get_all_products_empty_result(mock_connection):
    """BVA: Empty result set returns empty list"""
    conn, cursor = mock_connection
    cursor.__iter__.return_value = []

    products = get_all_products(conn)

    assert products == []


# -------------------------------------------------
# INSERT NEW PRODUCT
# -------------------------------------------------
def test_insert_new_product_success(mock_connection):
    """EP: Valid product is inserted and returns new ID"""
    conn, cursor = mock_connection
    cursor.lastrowid = 42

    product = {
        "name": "Banana",
        "uom_id": 1,
        "price_per_unit": 1.5,
        "selling_price": 3.0,
        "quantity": 30,
    }

    new_id = insert_new_product(conn, product)

    assert new_id == 42
    cursor.execute.assert_called_once()
    conn.commit.assert_called_once()


def test_insert_product_uses_insert_sql(mock_connection):
    """White-box: INSERT statement is used"""
    conn, cursor = mock_connection
    cursor.lastrowid = 1

    product = {
        "name": "Test",
        "uom_id": 1,
        "price_per_unit": 1.0,
        "selling_price": 2.0,
        "quantity": 1,
    }

    insert_new_product(conn, product)

    query, _ = cursor.execute.call_args.args
    assert query.strip().startswith("INSERT INTO products")


def test_insert_new_product_type_casting(mock_connection):
    """BVA: String numeric fields are cast correctly"""
    conn, cursor = mock_connection
    cursor.lastrowid = 1

    product = {
        "name": "Orange",
        "uom_id": "2",
        "price_per_unit": "3.25",
        "selling_price": "6.50",
        "quantity": "10",
    }

    insert_new_product(conn, product)

    _, data = cursor.execute.call_args.args
    assert data == ("Orange", 2, 3.25, 6.50, 10)


@pytest.mark.parametrize("quantity", [-1, 1001])
def test_insert_product_invalid_quantity_boundaries(mock_connection, quantity):
    """BVA: Quantity < 0 or > 1000 is rejected"""
    conn, _ = mock_connection

    product = {
        "name": "Invalid",
        "uom_id": 1,
        "price_per_unit": 1.0,
        "selling_price": 2.0,
        "quantity": quantity,
    }

    with pytest.raises(ValueError):
        insert_new_product(conn, product)


def test_insert_product_does_not_commit_on_invalid_quantity(mock_connection):
    """Decision table: Invalid quantity → no DB commit"""
    conn, _ = mock_connection

    product = {
        "name": "Invalid",
        "uom_id": 1,
        "price_per_unit": 10,
        "selling_price": 12,
        "quantity": 5000,
    }

    with pytest.raises(ValueError):
        insert_new_product(conn, product)

    conn.commit.assert_not_called()


# -------------------------------------------------
# DELETE PRODUCT
# -------------------------------------------------
def test_delete_product_existing(mock_connection):
    """Decision table: Existing product → 1 row affected"""
    conn, cursor = mock_connection
    cursor.rowcount = 1

    rows = delete_product(conn, 5)

    assert rows == 1
    cursor.execute.assert_called_once_with(
        "DELETE FROM products WHERE product_id = %s",
        (5,),
    )
    conn.commit.assert_called_once()


def test_delete_product_non_existing(mock_connection):
    """Decision table: Non-existing product → 0 rows affected"""
    conn, cursor = mock_connection
    cursor.rowcount = 0

    rows = delete_product(conn, 999)

    assert rows == 0


# -------------------------------------------------
# UPDATE PRODUCT
# -------------------------------------------------
def test_update_product_success(mock_connection):
    """EP: Valid update returns affected rows"""
    conn, cursor = mock_connection
    cursor.rowcount = 1

    product = {
        "product_id": 3,
        "name": "Cheese",
        "uom_id": 1,
        "price_per_unit": 4.5,
        "selling_price": 9.0,
        "quantity": 20,
    }

    rows = update_product(conn, product)

    assert rows == 1
    cursor.execute.assert_called_once()
    conn.commit.assert_called_once()


def test_update_product_no_match(mock_connection):
    """Decision table: product_id not found → 0 rows updated"""
    conn, cursor = mock_connection
    cursor.rowcount = 0

    product = {
        "product_id": 999,
        "name": "Ghost",
        "uom_id": 1,
        "price_per_unit": 1.0,
        "selling_price": 2.0,
        "quantity": 1,
    }

    rows = update_product(conn, product)

    assert rows == 0


def test_update_product_type_casting(mock_connection):
    """BVA: String numeric fields are cast correctly"""
    conn, cursor = mock_connection
    cursor.rowcount = 1

    product = {
        "product_id": "10",
        "name": "Yogurt",
        "uom_id": "2",
        "price_per_unit": "1.99",
        "selling_price": "3.98",
        "quantity": "5",
    }

    update_product(conn, product)

    _, data = cursor.execute.call_args.args
    assert data == ("Yogurt", 2, 1.99, 3.98, 5, 10)


def test_update_product_rejects_large_quantity(mock_connection):
    """BVA: Quantity > 1000 is rejected on update"""
    conn, _ = mock_connection

    product = {
        "product_id": 1,
        "name": "TooMany",
        "uom_id": 1,
        "price_per_unit": 10,
        "selling_price": 12,
        "quantity": 5001,
    }

    with pytest.raises(ValueError):
        update_product(conn, product)
