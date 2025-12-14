"""
Validation functions for GSM domain data.
"""
import re
from decimal import Decimal, InvalidOperation


def is_valid_product_name(name):
    """
    Validate product name: non-empty, alphanumeric with spaces, 1-100 chars.
    
    Args:
        name: Product name string
    
    Returns:
        True if valid, False otherwise
    """
    if not name or not isinstance(name, str):
        return False
    name = name.strip()
    if len(name) < 1 or len(name) > 100:
        return False
    # Allow letters, numbers, spaces, and common punctuation
    return bool(re.match(r'^[a-zA-Z0-9\s\-\.\,\(\)]+$', name))


def is_valid_uom(uom):
    """
    Validate Unit of Measurement: non-empty, alphanumeric, 1-10 chars.
    
    Args:
        uom: UOM string (e.g., 'kg', 'pcs', 'ltr')
    
    Returns:
        True if valid, False otherwise
    """
    if not uom or not isinstance(uom, str):
        return False
    uom = uom.strip()
    if len(uom) < 1 or len(uom) > 10:
        return False
    return bool(re.match(r'^[a-zA-Z0-9]+$', uom))


def is_valid_price(price):
    """
    Validate price: positive number with up to 2 decimal places.
    
    Args:
        price: Price string or number
    
    Returns:
        True if valid, False otherwise
    """
    try:
        if isinstance(price, str):
            price = price.strip().replace('$', '').replace(',', '')
        
        price_decimal = Decimal(str(price))
        
        # Must be positive
        if price_decimal <= 0:
            return False
        
        # Check decimal places
        if price_decimal.as_tuple().exponent < -2:
            return False
        
        return True
    except (InvalidOperation, ValueError, TypeError):
        return False


def is_valid_quantity(quantity):
    """
    Validate quantity: non-negative number.
    
    Args:
        quantity: Quantity string or number
    
    Returns:
        True if valid, False otherwise
    """
    try:
        if isinstance(quantity, str):
            quantity = quantity.strip()
        
        qty_decimal = Decimal(str(quantity))
        return qty_decimal >= 0
    except (InvalidOperation, ValueError, TypeError):
        return False


def is_valid_positive_integer(value):
    """
    Validate positive integer.
    
    Args:
        value: Integer string or number
    
    Returns:
        True if valid, False otherwise
    """
    try:
        int_value = int(value)
        return int_value > 0
    except (ValueError, TypeError):
        return False


def is_valid_date(date_str):
    """
    Validate date string in various common formats.
    Accepts: YYYY-MM-DD, MM/DD/YYYY, DD-MM-YYYY, etc.
    
    Args:
        date_str: Date string
    
    Returns:
        True if valid, False otherwise
    """
    if not date_str or not isinstance(date_str, str):
        return False
    
    date_patterns = [
        r'^\d{4}-\d{2}-\d{2}$',  # YYYY-MM-DD
        r'^\d{2}/\d{2}/\d{4}$',  # MM/DD/YYYY
        r'^\d{2}-\d{2}-\d{4}$',  # DD-MM-YYYY
        r'^\d{2}/\d{2}/\d{4}$',  # DD/MM/YYYY (also matches MM/DD/YYYY but acceptable)
        r'^\d{4}/\d{2}/\d{2}$',  # YYYY/MM/DD
    ]
    
    return any(re.match(pattern, date_str.strip()) for pattern in date_patterns)


def is_valid_datetime(datetime_str):
    """
    Validate datetime string.
    Accepts formats like: YYYY-MM-DD HH:MM:SS, DD/MM/YYYY HH:MM, etc.
    
    Args:
        datetime_str: Datetime string
    
    Returns:
        True if valid, False otherwise
    """
    if not datetime_str or not isinstance(datetime_str, str):
        return False
    
    datetime_patterns = [
        r'^\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}$',  # YYYY-MM-DD HH:MM:SS
        r'^\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}$',        # YYYY-MM-DD HH:MM
        r'^\d{2}/\d{2}/\d{4}\s\d{2}:\d{2}:\d{2}$',  # MM/DD/YYYY HH:MM:SS
        r'^\d{2}/\d{2}/\d{4}\s\d{2}:\d{2}$',        # MM/DD/YYYY HH:MM
        r'^\d{2}/\d{2}/\d{4},\s\d{2}:\d{2}:\d{2}$',  # DD/MM/YYYY, HH:MM:SS
        r'^\d{2}/\d{2}/\d{4},\s\d{2}:\d{2}$',        # DD/MM/YYYY, HH:MM
        r'^\d{2}/\d{2}/\d{4},\s\d{2}:\d{2}:\d{2}$',  # DD/MM/YYYY, HH:MM:SS (comma)
        r'^\d{2}/\d{2}/\d{4},\s\d{2}:\d{2}$',        # DD/MM/YYYY, HH:MM (comma)
    ]
    
    return any(re.match(pattern, datetime_str.strip()) for pattern in datetime_patterns)


def is_valid_total(total):
    """
    Validate total amount: non-negative number with up to 2 decimal places.
    
    Args:
        total: Total amount string or number
    
    Returns:
        True if valid, False otherwise
    """
    try:
        if isinstance(total, str):
            total = total.strip().replace('$', '').replace(',', '')
        
        total_decimal = Decimal(str(total))
        
        # Must be non-negative (0 is allowed for totals)
        if total_decimal < 0:
            return False
        
        # Check decimal places
        if total_decimal.as_tuple().exponent < -2:
            return False
        
        return True
    except (InvalidOperation, ValueError, TypeError):
        return False


def is_non_empty_string(value):
    """
    Validate that a value is a non-empty string.
    
    Args:
        value: Value to check
    
    Returns:
        True if valid, False otherwise
    """
    return isinstance(value, str) and len(value.strip()) > 0


def is_valid_order_id(order_id):
    """
    Validate order ID: positive integer.
    
    Args:
        order_id: Order ID string or number
    
    Returns:
        True if valid, False otherwise
    """
    return is_valid_positive_integer(order_id)


def is_valid_product_id(product_id):
    """
    Validate product ID: positive integer.
    
    Args:
        product_id: Product ID string or number
    
    Returns:
        True if valid, False otherwise
    """
    return is_valid_positive_integer(product_id)


def is_valid_temperature(temp):
    """
    Validate temperature: number in reasonable range (-100 to 100 Celsius).
    
    Args:
        temp: Temperature string or number
    
    Returns:
        True if valid, False otherwise
    """
    try:
        if isinstance(temp, str):
            # Remove common temperature symbols
            temp = temp.strip().replace('°', '').replace('C', '').replace('F', '')
        
        temp_float = float(temp)
        return -100 <= temp_float <= 100
    except (ValueError, TypeError):
        return False


def is_valid_percentage(percentage):
    """
    Validate percentage: number between 0 and 100.
    
    Args:
        percentage: Percentage string or number
    
    Returns:
        True if valid, False otherwise
    """
    try:
        if isinstance(percentage, str):
            percentage = percentage.strip().replace('%', '')
        
        pct_float = float(percentage)
        return 0 <= pct_float <= 100
    except (ValueError, TypeError):
        return False
