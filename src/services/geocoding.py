from geopy.geocoders import Nominatim
import streamlit as st

from typing import Union

def get_bounding_box(location: str) -> Union[list[float], None]:
    """Get bounding box coordinates for a given location."""
    try:
        geolocator = Nominatim(user_agent="stac_search_app")
        loc = geolocator.geocode(location)
        
        if loc:
            buffer = 0.5
            return [
                loc.longitude - buffer,
                loc.latitude - buffer,
                loc.longitude + buffer,
                loc.latitude + buffer
            ]
        return None
    except Exception as e:
        st.error(f"Error getting location: {str(e)}")
        return None
