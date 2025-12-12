import pytest
from unittest.mock import MagicMock, call
from backend.dao.order_list_dao import get_all_orders, get_recent_orders


# ---------------------------------------------------------
# Mock connection + cursor generator
# ---------------------------------------------------------
def mock_connection():
    conn = MagicMock()
    cursor = MagicMock()
    conn.cursor.return_value = cursor
    return conn, cursor


# ---------------------------------------------------------
# EP: get_all_orders returns rows
# ---------------------------------------------------------
def test_get_all_orders_returns_data():
    conn, cursor = mock_connection()

    fake_rows = [
        {"order_id": 1, "customer_name": "Alice", "total_price": 15.0, "datetime": "2025-01-01"},
        {"order_id": 2, "customer_name": "Bob", "total_price": 25.0, "datetime": "2025-01-02"},
    ]

    cursor.fetchall.return_value = fake_rows

    result = get_all_orders(conn)

    assert result == fake_rows
    cursor.execute.assert_called_once()

    sql = cursor.execute.call_args.args[0]
    assert "ORDER BY o.datetime DESC" in sql


# ---------------------------------------------------------
# EP: get_recent_orders returns rows
# ---------------------------------------------------------
def test_get_recent_orders_default_limit():
    conn, cursor = mock_connection()

    fake_rows = [{"order_id": 1}]

    cursor.fetchall.return_value = fake_rows

    result = get_recent_orders(conn)

    assert result == fake_rows

    # SQL correctness
    sql, params = cursor.execute.call_args.args
    assert "ORDER BY o.datetime DESC" in sql
    assert "LIMIT %s" in sql
    assert params == (5,)  # default


# ---------------------------------------------------------
# BVA:  limit = 1
# ---------------------------------------------------------
def test_get_recent_orders_limit_one():
    conn, cursor = mock_connection()
    cursor.fetchall.return_value = [{"order_id": 99}]

    result = get_recent_orders(conn, limit=1)

    assert result == [{"order_id": 99}]
    sql, params = cursor.execute.call_args.args
    assert params == (1,)


# ---------------------------------------------------------
# BVA: limit = 0 Edge case
# ---------------------------------------------------------
def test_get_recent_orders_limit_zero():
    conn, cursor = mock_connection()
    cursor.fetchall.return_value = []

    result = get_recent_orders(conn, limit=0)

    assert result == []
    sql, params = cursor.execute.call_args.args
    assert params == (0,)


# ---------------------------------------------------------
# BVA: large limit
# ---------------------------------------------------------
def test_get_recent_orders_large_limit():
    conn, cursor = mock_connection()
    cursor.fetchall.return_value = []

    result = get_recent_orders(conn, limit=999999)

    assert result == []
    sql, params = cursor.execute.call_args.args
    assert params == (999999,)


# ---------------------------------------------------------
# Decision Table: invalid limits
# ---------------------------------------------------------
@pytest.mark.parametrize("limit", [-1, -10, "abc", None])
def test_get_recent_orders_invalid_limits(limit):
    """Decision Table: function should raise for invalid limit types."""
    conn, cursor = mock_connection()

    with pytest.raises(Exception):  # Your DAO does no validation  DB errors hit here
        get_recent_orders(conn, limit=limit)
