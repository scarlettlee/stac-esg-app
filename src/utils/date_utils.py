# src/utils/date_utils.py

from datetime import datetime, timezone
from typing import Tuple, Optional, Union, List

def parse_date(date: Union[datetime, str, None]) -> Optional[datetime]:
    """
    Parse date string or datetime object and ensure it's timezone-aware.
    
    Args:
        date: Date string in ISO format or datetime object
        
    Returns:
        datetime: Timezone-aware datetime object or None if invalid
    """
    if date is None:
        return None
        
    if isinstance(date, datetime):
        return date if date.tzinfo else date.replace(tzinfo=timezone.utc)
        
    if isinstance(date, str):
        try:
            dt = datetime.fromisoformat(date.replace('Z', '+00:00'))
            return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
        except ValueError:
            return None
            
    return None

def temporal_intersects(
    temporal_extent: Tuple[Optional[datetime], Optional[datetime]],
    temporal_filter: List[str]
) -> bool:
    """
    Check if two temporal intervals intersect.
    
    Args:
        temporal_extent: Tuple of start and end dates from STAC collection
        temporal_filter: List of start and end date strings from user input
        
    Returns:
        bool: True if intervals intersect, False otherwise
    """
    start_date1, end_date1 = temporal_extent
    start_date2, end_date2 = [parse_date(date) for date in temporal_filter]
    
    # Handle cases where dates might be None
    if start_date1 is None and end_date1 is None:
        return True  # Collection has no temporal constraints
        
    if start_date2 is None or end_date2 is None:
        return False  # Invalid filter dates
        
    # Check for no intersection
    if (end_date1 and start_date2 and end_date1 < start_date2) or \
       (start_date1 and end_date2 and start_date1 > end_date2):
        return False
        
    return True

def validate_date_range(date_range: str) -> Tuple[bool, str]:
    """
    Validate date range string format and values.
    
    Args:
        date_range: Comma-separated date range string
        
    Returns:
        Tuple[bool, str]: (is_valid, error_message)
    """
    try:
        dates = [d.strip() for d in date_range.split(',')]
        if len(dates) != 2:
            return False, "Date range must contain exactly two dates separated by comma"
            
        start_date, end_date = [parse_date(d) for d in dates]
        if None in (start_date, end_date):
            return False, "Dates must be in ISO format (YYYY-MM-DD)"
            
        if start_date > end_date:
            return False, "Start date must be before end date"
            
        return True, ""
        
    except Exception as e:
        return False, f"Invalid date format: {str(e)}"