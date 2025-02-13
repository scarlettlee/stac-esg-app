# src/components/maps.py

import folium
from streamlit_folium import st_folium

def display_area_map(bbox: list[float]):
    """Display a map with the selected area."""
    center_lat = (bbox[1] + bbox[3]) / 2
    center_lon = (bbox[0] + bbox[2]) / 2
    
    m = folium.Map(location=[center_lat, center_lon], zoom_start=8)
    
    # Draw rectangle for bounding box
    folium.Rectangle(
        bounds=[[bbox[1], bbox[0]], [bbox[3], bbox[2]]],
        color="red",
        fill=True,
        popup="Search Area"
    ).add_to(m)
    
    return m