"""
Date parsing and formatting utilities for the book library application.
"""

from datetime import date
from typing import Optional
from dateutil.parser import parse as parse_date
from dateutil.parser import ParserError


def parse_date_input(date_string: str) -> Optional[date]:
    """
    Parse a date string into a date object using dateutil.
    
    This function is very forgiving and can handle many date formats:
    - "2023-12-25" (ISO format)
    - "12/25/2023" (US format)
    - "25/12/2023" (European format) 
    - "Dec 25, 2023" (text format)
    - "yesterday", "today", "tomorrow" (relative)
    - "last monday", "next friday" (relative days)
    - And many more!
    
    Args:
        date_string: The date string to parse
        
    Returns:
        date object if parsing succeeds, None if it fails
        
    Examples:
        >>> parse_date_input("2023-12-25")
        datetime.date(2023, 12, 25)
        >>> parse_date_input("Dec 25, 2023")  
        datetime.date(2023, 12, 25)
        >>> parse_date_input("yesterday")
        datetime.date(2023, 12, 24)  # Assuming today is 2023-12-25
    """
    if not date_string or not date_string.strip():
        return None
    
    try:
        # dateutil.parser.parse is very flexible
        parsed_datetime = parse_date(date_string.strip())
        # Convert datetime to date (we only need the date part)
        return parsed_datetime.date()
    except (ParserError, ValueError, TypeError):
        return None


def format_date_for_display(date_obj: date) -> str:
    """
    Format a date object for display in the UI.
    
    Args:
        date_obj: The date to format
        
    Returns:
        Formatted date string
    """
    if not date_obj:
        return ""
    return date_obj.strftime("%Y-%m-%d (%a)")  # e.g., "2023-12-25 (Mon)"


def validate_date_input(date_string: str) -> bool:
    """
    Validate if a date string can be parsed.
    
    Args:
        date_string: The date string to validate
        
    Returns:
        True if the date can be parsed, False otherwise
    """
    return parse_date_input(date_string) is not None