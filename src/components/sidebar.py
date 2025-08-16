# src/components/sidebar.py

import streamlit as st
from typing import Tuple, Dict, List
from config.sasb_sectors import SASB_SECTORS

def render_sector_selection() -> Tuple[str, str]:
    """
    Render sector and subsector selection widgets.
    
    Returns:
        Tuple[str, str]: Selected sector and subsector
    """
    st.sidebar.header("Industry Selection")
    
    # Set default sector to "Technology & Communications"
    default_sector = "Technology & Communications"
    default_sector_index = list(SASB_SECTORS.keys()).index(default_sector)
    
    selected_sector = st.sidebar.selectbox(
        "Select Industry Sector",
        options=list(SASB_SECTORS.keys()),
        index=default_sector_index,
        key="sector_select"
    )
    
    # Set default subsector to "Software & IT Services" for Technology & Communications
    if selected_sector == "Technology & Communications":
        default_subsector = "Software & IT Services"
    else:
        default_subsector = SASB_SECTORS[selected_sector][0]
    
    # Find the index of the default subsector
    subsector_options = SASB_SECTORS[selected_sector]
    try:
        default_index = subsector_options.index(default_subsector)
    except ValueError:
        default_index = 0  # Fallback to first option if not found
    
    selected_subsector = st.sidebar.selectbox(
        "Select Industry Subsector",
        options=subsector_options,
        index=default_index,
        key="subsector_select"
    )
    
    return selected_sector, selected_subsector

def render_location_input(default_location: str = "New York City") -> str:
    """
    Render location input widget.
    
    Args:
        default_location: Default location to display
        
    Returns:
        str: Input location
    """
    st.sidebar.header("Location")
    
    location = st.sidebar.text_input(
        "Enter Location",
        value=default_location,
        help="Enter a city, region, or country name (e.g., 'Tokyo, Japan' or 'California, USA')"
    )
    
    return location





def render_sidebar() -> Dict[str, any]:
    """
    Render complete sidebar with all components.
    
    Returns:
        Dict[str, any]: Dictionary containing all sidebar inputs
    """
    st.sidebar.title("Search Filters")
    
    # Get sector selections
    sector, subsector = render_sector_selection()
    
    # Get location
    location = render_location_input()
    
    # Search button
    search_clicked = st.sidebar.button(
        "Search and Generate Insights",
        type="primary",
        use_container_width=True
    )
    
    return {
        "sector": sector,
        "subsector": subsector,
        "location": location,
        "search_clicked": search_clicked
    }