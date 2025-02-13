# src/utils/spatial_utils.py

from typing import List, Tuple
from math import cos, radians

def bbox_intersects(spatial_extent: List[float], bbox_filter: List[float]) -> bool:
    """
    Check if two bounding boxes intersect.
    
    Args:
        spatial_extent: [min_lon1, min_lat1, max_lon1, max_lat1]
        bbox_filter: [min_lon2, min_lat2, max_lon2, max_lat2]
        
    Returns:
        bool: True if bounding boxes intersect, False otherwise
    """
    min_lon1, min_lat1, max_lon1, max_lat1 = spatial_extent
    min_lon2, min_lat2, max_lon2, max_lat2 = bbox_filter
    
    # Check if one box is to the left of the other
    if min_lon1 > max_lon2 or max_lon1 < min_lon2:
        return False
        
    # Check if one box is above the other
    if min_lat1 > max_lat2 or max_lat1 < min_lat2:
        return False
        
    return True

def validate_bbox(bbox: List[float]) -> Tuple[bool, str]:
    """
    Validate bounding box coordinates.
    
    Args:
        bbox: [min_lon, min_lat, max_lon, max_lat]
        
    Returns:
        Tuple[bool, str]: (is_valid, error_message)
    """
    if len(bbox) != 4:
        return False, "Bounding box must contain exactly 4 coordinates"
        
    min_lon, min_lat, max_lon, max_lat = bbox
    
    # Check longitude range
    if not (-180 <= min_lon <= 180 and -180 <= max_lon <= 180):
        return False, "Longitude must be between -180 and 180 degrees"
        
    # Check latitude range
    if not (-90 <= min_lat <= 90 and -90 <= max_lat <= 90):
        return False, "Latitude must be between -90 and 90 degrees"
        
    # Check min/max relationships
    if min_lon >= max_lon:
        return False, "Minimum longitude must be less than maximum longitude"
    if min_lat >= max_lat:
        return False, "Minimum latitude must be less than maximum latitude"
        
    return True, ""

def calculate_bbox_area(bbox: List[float]) -> float:
    """
    Calculate approximate area of bounding box in square kilometers.
    
    Args:
        bbox: [min_lon, min_lat, max_lon, max_lat]
        
    Returns:
        float: Approximate area in square kilometers
    """
    min_lon, min_lat, max_lon, max_lat = bbox
    
    # Rough approximation using 111km per degree
    # More accurate calculations would need to account for Earth's spheroid shape
    width_km = abs(max_lon - min_lon) * 111 * abs(cos(radians((min_lat + max_lat) / 2)))
    height_km = abs(max_lat - min_lat) * 111
    
    return width_km * height_km