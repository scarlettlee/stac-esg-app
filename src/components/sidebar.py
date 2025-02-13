# src/components/sidebar.py

import streamlit as st
from typing import Tuple, Dict, List
from config.sasb_sectors import SASB_SECTORS
from utils.date_utils import validate_date_range

def render_sector_selection() -> Tuple[str, str]:
    """
    Render sector and subsector selection widgets.
    
    Returns:
        Tuple[str, str]: Selected sector and subsector
    """
    st.sidebar.header("Industry Selection")
    
    selected_sector = st.sidebar.selectbox(
        "Select Industry Sector",
        options=list(SASB_SECTORS.keys()),
        key="sector_select"
    )
    
    selected_subsector = st.sidebar.selectbox(
        "Select Industry Subsector",
        options=SASB_SECTORS[selected_sector],
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

def render_date_range(
    default_range: str = "2020-01-01, 2025-12-31"
) -> Tuple[bool, str, List[str]]:
    """
    Render date range input widget with validation.
    
    Args:
        default_range: Default date range to display
        
    Returns:
        Tuple[bool, str, List[str]]: (is_valid, error_message, [start_date, end_date])
    """
    st.sidebar.header("Time Period")
    
    date_range = st.sidebar.text_input(
        "Date Range",
        value=default_range,
        help="Enter date range in format: YYYY-MM-DD, YYYY-MM-DD"
    )
    
    is_valid, error_message = validate_date_range(date_range)
    if not is_valid:
        st.sidebar.error(error_message)
        return False, error_message, []
    
    dates = [d.strip() for d in date_range.split(',')]
    return True, "", dates

def render_advanced_filters() -> Dict[str, any]:
    """
    Render advanced filtering options.
    
    Returns:
        Dict[str, any]: Dictionary of filter settings
    """
    with st.sidebar.expander("Advanced Filters"):
        filters = {
            "min_cloud_cover": st.slider(
                "Maximum Cloud Cover (%)",
                0, 100, 20,
                help="Filter scenes by maximum cloud cover percentage"
            ),
            "include_derived_data": st.checkbox(
                "Include Derived Data",
                True,
                help="Include processed and derived data products"
            ),
            "data_frequency": st.selectbox(
                "Data Frequency",
                options=["Any", "Daily", "Weekly", "Monthly", "Annual"],
                help="Filter by data collection frequency"
            )
        }
    
    return filters

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
    
    # Get date range
    is_valid, error_message, dates = render_date_range()
    
    # Get advanced filters
    advanced_filters = render_advanced_filters()
    
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
        "dates_valid": is_valid,
        "date_error": error_message,
        "date_range": dates,
        "advanced_filters": advanced_filters,
        "search_clicked": search_clicked
    }