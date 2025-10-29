"""
Google Maps integration for Streamlit
Replaces Folium with Google Maps for better interactivity and features.
"""

import streamlit as st
import streamlit.components.v1 as components
import os
from typing import List, Dict, Any, Optional
import json


def get_google_maps_api_key() -> Optional[str]:
    """Get Google Maps API key from environment variable."""
    api_key = os.getenv('GOOGLE_MAPS_API_KEY')
    if not api_key:
        st.warning("⚠️ GOOGLE_MAPS_API_KEY not set in environment. Google Maps will not work.")
    return api_key


def create_google_map_html(
    bbox: List[float],
    api_key: str,
    zoom_level: int = 10,
    map_type: str = "satellite",
    show_marker: bool = True,
    location_name: Optional[str] = None
) -> str:
    """
    Create an HTML/JavaScript snippet for Google Maps that displays a bounding box.
    
    Args:
        bbox: Bounding box [min_lon, min_lat, max_lon, max_lat]
        api_key: Google Maps API key
        zoom_level: Initial zoom level (1-20)
        map_type: Map type (satellite, roadmap, hybrid, terrain)
        show_marker: Whether to show a marker in the center
        location_name: Optional location name for the marker
        
    Returns:
        HTML string with embedded Google Maps
    """
    min_lon, min_lat, max_lon, max_lat = bbox
    center_lat = (min_lat + max_lat) / 2
    center_lon = (min_lon + max_lon) / 2
    
    # Calculate zoom based on bounding box size if not provided
    if zoom_level == 0:
        lat_diff = max_lat - min_lat
        lon_diff = max_lon - min_lon
        max_diff = max(lat_diff, lon_diff)
        
        if max_diff > 10:
            zoom_level = 5
        elif max_diff > 1:
            zoom_level = 7
        elif max_diff > 0.5:
            zoom_level = 8
        elif max_diff > 0.1:
            zoom_level = 10
        else:
            zoom_level = 12
    
    # Create the bounding box rectangle coordinates
    bounds = [
        {"lat": min_lat, "lng": min_lon},
        {"lat": min_lat, "lng": max_lon},
        {"lat": max_lat, "lng": max_lon},
        {"lat": max_lat, "lng": min_lon},
        {"lat": min_lat, "lng": min_lon}  # Close the rectangle
    ]
    
    marker_label = location_name or "Search Area"
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Google Maps - ESG Search Area</title>
        <script src="https://maps.googleapis.com/maps/api/js?key={api_key}&libraries=drawing,geometry"></script>
    </head>
    <body>
        <div id="map" style="width: 100%; height: 600px;"></div>
        <script>
            function initMap() {{
                // Center of the bounding box
                const center = {{lat: {center_lat}, lng: {center_lon}}};
                
                // Create map
                const map = new google.maps.Map(document.getElementById('map'), {{
                    zoom: {zoom_level},
                    center: center,
                    mapTypeId: google.maps.MapTypeId.{map_type}
                }});
                
                // Define rectangle bounds
                const bounds = new google.maps.LatLngBounds();
                
                // Bounding box coordinates for the rectangle
                const rectangleCoords = [
                    {{lat: {min_lat}, lng: {min_lon}}},
                    {{lat: {min_lat}, lng: {max_lon}}},
                    {{lat: {max_lat}, lng: {max_lon}}},
                    {{lat: {max_lat}, lng: {min_lon}}}
                ];
                
                // Create and add rectangle to show search area
                const rectangle = new google.maps.Rectangle({{
                    bounds: new google.maps.LatLngBounds(
                        new google.maps.LatLng({min_lat}, {min_lon}),
                        new google.maps.LatLng({max_lat}, {max_lon})
                    ),
                    strokeColor: '#FF0000',
                    strokeOpacity: 0.8,
                    strokeWeight: 3,
                    fillColor: '#FF0000',
                    fillOpacity: 0.15
                }});
                
                rectangle.setMap(map);
                
                // Fit map to show the entire rectangle
                const rectangleBounds = new google.maps.LatLngBounds(
                    new google.maps.LatLng({min_lat}, {min_lon}),
                    new google.maps.LatLng({max_lat}, {max_lon})
                );
                map.fitBounds(rectangleBounds);
                
                // Add marker in the center if requested
                {'const marker = new google.maps.Marker({' if show_marker else ''}
                {'position: center,' if show_marker else ''}
                {'title: "' + marker_label + '",' if show_marker else ''}
                {'map: map' if show_marker else ''}
                {'});' if show_marker else ''}
            }}
            
            // Initialize the map
            initMap();
        </script>
    </body>
    </html>
    """
    
    return html


def display_google_map(
    bbox: List[float],
    zoom_level: int = 0,
    map_type: str = "satellite",
    show_marker: bool = True,
    location_name: Optional[str] = None,
    height: int = 600
) -> None:
    """
    Display a Google Map in Streamlit with the given bounding box.
    
    Args:
        bbox: Bounding box [min_lon, min_lat, max_lon, max_lat]
        zoom_level: Zoom level (0 for auto-calculate, 1-20 for specific zoom)
        map_type: Map type ('satellite', 'roadmap', 'hybrid', 'terrain')
        show_marker: Whether to show a center marker
        location_name: Optional location name for the marker
        height: Height of the map in pixels
    """
    api_key = get_google_maps_api_key()
    
    if not api_key:
        st.error("Google Maps API key not configured. Please set GOOGLE_MAPS_API_KEY in your .env file.")
        return
    
    html = create_google_map_html(
        bbox=bbox,
        api_key=api_key,
        zoom_level=zoom_level,
        map_type=map_type,
        show_marker=show_marker,
        location_name=location_name
    )
    
    components.html(html, height=height)


def create_marker_map(
    center: Dict[str, float],
    markers: List[Dict[str, Any]],
    api_key: str,
    zoom: int = 10
) -> str:
    """
    Create a Google Map with multiple markers.
    
    Args:
        center: Center point {lat: float, lng: float}
        markers: List of marker dictionaries with 'lat', 'lng', 'title', 'description'
        api_key: Google Maps API key
        zoom: Zoom level
        
    Returns:
        HTML string for the map
    """
    markers_json = json.dumps(markers)
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Google Maps with Markers</title>
        <script src="https://maps.googleapis.com/maps/api/js?key={api_key}&libraries=drawing,geometry"></script>
    </head>
    <body>
        <div id="map" style="width: 100%; height: 600px;"></div>
        <script>
            function initMap() {{
                const center = {{lat: {center['lat']}, lng: {center['lng']}}};
                const map = new google.maps.Map(document.getElementById('map'), {{
                    zoom: {zoom},
                    center: center
                }});
                
                const markers = {markers_json};
                
                markers.forEach(markerData => {{
                    const marker = new google.maps.Marker({{
                        position: {{lat: markerData.lat, lng: markerData.lng}},
                        map: map,
                        title: markerData.title || 'Marker',
                        label: markerData.label || ''
                    }});
                    
                    if (markerData.description) {{
                        const infoWindow = new google.maps.InfoWindow({{
                            content: `<div><strong>${{markerData.title}}</strong><br>${{markerData.description}}</div>`
                        }});
                        
                        marker.addListener('click', () => {{
                            infoWindow.open(map, marker);
                        }});
                    }}
                }});
                
                // Auto-fit bounds if multiple markers
                if (markers.length > 1) {{
                    const bounds = new google.maps.LatLngBounds();
                    markers.forEach(m => bounds.extend({{lat: m.lat, lng: m.lng}}));
                    map.fitBounds(bounds);
                }}
            }}
            
            initMap();
        </script>
    </body>
    </html>
    """
    
    return html

