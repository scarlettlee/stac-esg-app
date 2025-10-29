# src/components/maps.py

"""
Google Maps integration - using Google Maps exclusively for all mapping needs.
This aligns with Google family API strategy.
"""

from typing import Optional
from components.google_maps import display_google_map


def display_area_map(
    bbox: list[float],
    location_name: Optional[str] = None
):
    """
    Display a map with the selected area using Google Maps.
    
    Args:
        bbox: Bounding box [min_lon, min_lat, max_lon, max_lat]
        location_name: Optional location name for the map marker
    """
    display_google_map(
        bbox=bbox,
        zoom_level=0,  # Auto-calculate based on bounding box
        map_type="satellite",
        show_marker=True,
        location_name=location_name,
        height=600
    )