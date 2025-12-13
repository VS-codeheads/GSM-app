import pytest
from unittest.mock import MagicMock

from backend.dao.uom_dao import get_all_uoms


def mock_connection():
    conn = MagicMock()
    cursor = MagicMock()
    conn.cursor.return_value = cursor
    return conn, cursor


# ---------------------------------------------------------
# GET ALL UOMS
# ---------------------------------------------------------
def test_get_all_uoms_returns_list():
    """EP - Valid UOM rows are returned as dicts"""
    conn, cursor = mock_connection()

    # Simulate DB rows (tuple-based cursor)
    cursor.__iter__.return_value = [
        (1, "kg"),
        (2, "liter"),
        (3, "piece")
    ]

    result = get_all_uoms(conn)

    assert result == [
        {"uom_id": 1, "uom_name": "kg"},
        {"uom_id": 2, "uom_name": "liter"},
        {"uom_id": 3, "uom_name": "piece"},
    ]

    cursor.execute.assert_called_once_with(
        "SELECT uom_id, uom_name FROM uom"
    )


def test_get_all_uoms_empty_result():
    """BVA - No UOM rows in DB = empty list"""
    conn, cursor = mock_connection()

    cursor.__iter__.return_value = []

    result = get_all_uoms(conn)

    assert result == []


def test_get_all_uoms_single_row():
    """BVA - Exactly one UOM in DB"""
    conn, cursor = mock_connection()

    cursor.__iter__.return_value = [(1, "kg")]

    result = get_all_uoms(conn)

    assert len(result) == 1
    assert result[0]["uom_id"] == 1
    assert result[0]["uom_name"] == "kg"


def test_get_all_uoms_cursor_used_correctly():
    """Decision table - cursor is obtained and query executed once"""
    conn, cursor = mock_connection()
    cursor.__iter__.return_value = []

    get_all_uoms(conn)

    conn.cursor.assert_called_once()
    cursor.execute.assert_called_once()
