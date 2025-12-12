import pytest
from unittest.mock import MagicMock, call
from backend.dao.order_details_dao import get_order_details


# ---------------------------------------------------------
# Helper to generate a fake MySQL connection + cursor
# ---------------------------------------------------------
def mock_connection():
    conn = MagicMock()
    cursor = MagicMock()
    conn.cursor.return_value = cursor
    return conn, cursor


# ---------------------------------------------------------
# EP: Valid order_id returns rows
# ---------------------------------------------------------
def test_get_order_details_returns_rows():
    conn, cursor = mock_connection()

    sample_rows = [
        {
            "order_id": 5,
            "customer_name": "John",
            "total_price": 25.0,
            "datetime": "2025-12-12 12:00",
            "product_name": "Apple",
            "uom_id": 1,
            "uom_name": "kg",
            "quantity": 2,
            "item_total": 10.0,
        },
        {
            "order_id": 5,
            "customer_name": "John",
            "total_price": 25.0,
            "datetime": "2025-12-12 12:00",
            "product_name": "Banana",
            "uom_id": 1,
            "uom_name": "kg",
            "quantity": 3,
            "item_total": 15.0,
        },
    ]

    cursor.fetchall.return_value = sample_rows

    result = get_order_details(conn, 5)

    # Validating result delivered correctly
    assert result == sample_rows

    # Validates correct SQL was executed
    cursor.execute.assert_called_once()
    executed_sql, params = cursor.execute.call_args.args
    assert "SELECT" in executed_sql
    assert "FROM orders" in executed_sql
    assert params == (5,)


# ---------------------------------------------------------
# EP: No matching order_id returns empty list
# ---------------------------------------------------------
def test_get_order_details_no_results():
    conn, cursor = mock_connection()
    cursor.fetchall.return_value = []

    result = get_order_details(conn, 999)  # nonexistent order

    assert result == []
    cursor.execute.assert_called_once()
    assert cursor.execute.call_args.args[1] == (999,)


# ---------------------------------------------------------
# BVA: Smallest valid order_id (1)
# ---------------------------------------------------------
def test_get_order_details_order_id_min_boundary():
    conn, cursor = mock_connection()
    cursor.fetchall.return_value = []

    get_order_details(conn, 1)

    cursor.execute.assert_called_once()
    assert cursor.execute.call_args.args[1] == (1,)


# ---------------------------------------------------------
# BVA: Very large order_id
# ---------------------------------------------------------
def test_get_order_details_large_order_id():
    conn, cursor = mock_connection()
    cursor.fetchall.return_value = []

    get_order_details(conn, 999999999)

    cursor.execute.assert_called_once()
    assert cursor.execute.call_args.args[1] == (999999999,)


# ---------------------------------------------------------
# Decision Table: Order exists but has no products Edge case
# ---------------------------------------------------------
def test_get_order_details_order_exists_but_no_items():
    """In case the order exists but order_details table is empty"""
    conn, cursor = mock_connection()

    # Simulate JOIN returning no rows because order_details is empty
    cursor.fetchall.return_value = []

    result = get_order_details(conn, 12)

    assert result == []
    cursor.execute.assert_called_once()
