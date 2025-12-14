import pytest
from unittest.mock import MagicMock, call
from datetime import datetime
from backend.dao.order_dao import add_order

# ---------------------------------------------------------
# Builder to make a fake DB connection + cursor
# ---------------------------------------------------------
def mock_connection():
    conn = MagicMock()
    cursor = MagicMock()
    conn.cursor.return_value = cursor
    cursor.lastrowid = 99   # simulate new order ID
    return conn, cursor


# ---------------------------------------------------------
# NEW ORDER TESTS
# ---------------------------------------------------------
def test_add_new_order_inserts_order_and_details():
    """EP: A valid order inserts into orders + order_details + reduces stock"""
    conn, cursor = mock_connection()

    order = {
        "customer_name": "John",
        "total_price": 20.0,
        "order_details": [
            {"product_id": 1, "quantity": 2, "total_price": 10},
            {"product_id": 2, "quantity": 1, "total_price": 10}
        ]
    }

    order_id = add_order(conn, order)

    # Correct new order ID returned
    assert order_id == 99

    assert any("INSERT INTO orders" in str(c) for c in cursor.execute.mock_calls), "No INSERT INTO orders call executed"
    assert any("INSERT INTO order_details" in str(c) for c in cursor.execute.mock_calls)
    assert any("UPDATE products" in str(c) for c in cursor.execute.mock_calls)

    conn.commit.assert_called_once()


# ---------------------------------------------------------
# EDIT EXISTING ORDER
# ---------------------------------------------------------
def test_edit_existing_order_restores_old_stock_and_updates_order():
    """Decision Table: Editing order requires restore old stock + delete old items + update order"""
    conn, cursor = mock_connection()

    # Simulate DB returning old items - so that they can be restored
    cursor.fetchall.return_value = [
        {"product_id": 1, "quantity": 3},
        {"product_id": 2, "quantity": 1},
    ]

    order = {
        "order_id": 5,
        "customer_name": "Maria",
        "total_price": 50.0,
        "order_details": [
            {"product_id": 1, "quantity": 1, "total_price": 20},
            {"product_id": 2, "quantity": 2, "total_price": 30}
        ]
    }

    returned_id = add_order(conn, order)

    assert returned_id == 5  # Edited order keeps its ID

    # Old items fetched for restore 
    cursor.execute.assert_any_call(
        "SELECT product_id, quantity FROM order_details WHERE order_id = %s",
        (5,)
    )

    # Old stock restored 
    assert call(
        "UPDATE products SET quantity = quantity + %s WHERE product_id = %s",
        (3, 1)
    ) in cursor.execute.mock_calls

    assert call(
        "UPDATE products SET quantity = quantity + %s WHERE product_id = %s",
        (1, 2)
    ) in cursor.execute.mock_calls

    # Old details deleted 
    cursor.execute.assert_any_call(
        "DELETE FROM order_details WHERE order_id = %s",
        (5,)
    )

    # Order updated 
    update_calls = [
        call for call in cursor.execute.mock_calls
        if "UPDATE orders" in str(call)
    ]

    assert update_calls, "UPDATE orders was not called"

    sql, params = update_calls[0].args

    assert "UPDATE orders" in sql
    assert params[0] == "Maria"
    assert params[1] == 50
    assert isinstance(params[2], datetime)  #  timestamp check
    assert params[3] == 5

    conn.commit.assert_called_once()


# ---------------------------------------------------------
# BVA: Editing an order with no previous items
# ---------------------------------------------------------
def test_edit_existing_order_with_no_old_items():
    """BVA: Editing order where no old items exist should not fail"""
    conn, cursor = mock_connection()

    cursor.fetchall.return_value = []  # Simulate no old items

    order = {
        "order_id": 10,
        "customer_name": "Empty",
        "total_price": 0,
        "order_details": []
    }

    result_id = add_order(conn, order)

    assert result_id == 10  # Still returns same ID
    conn.commit.assert_called_once()


# ---------------------------------------------------------
# EP: Attempting order with no details - should still work
# ---------------------------------------------------------
def test_add_order_with_empty_details():
    """EP - Order with zero items still inserts main order but performs no detail inserts"""
    conn, cursor = mock_connection()

    order = {
        "customer_name": "Nobody",
        "total_price": 0,
        "order_details": []
    }

    add_order(conn, order)

    # Should insert into orders
    assert any(
        "INSERT INTO orders" in str(call.args[0])
        for call in cursor.execute.mock_calls
    )

    # Shouldn't insert into order_details
    assert not any(
        "INSERT INTO order_details" in str(call.args)
        for call in cursor.execute.mock_calls
    )

    conn.commit.assert_called_once()


def test_edit_order_to_remove_all_details():
    """ Test updating an old order when the new order has empty details"""
    conn, cursor = mock_connection()

    cursor.fetchall.return_value = [
        {"product_id": 10, "quantity": 5}
    ]

    order = {
        "order_id": 15,
        "customer_name": "Claire",
        "total_price": 0.0,
        "order_details": []
    }

    returned_id = add_order(conn, order)

    assert returned_id == 15

    assert call("UPDATE products SET quantity = quantity + %s WHERE product_id = %s", (5, 10)) in cursor.execute.mock_calls

    cursor.execute.assert_any_call("DELETE FROM order_details WHERE order_id = %s", (15,))

    assert not any("INSERT INTO order_details" in str(c) for c in cursor.execute.mock_calls)

    assert any("UPDATE orders" in str(c) for c in cursor.execute.mock_calls)

    conn.commit.assert_called_once()