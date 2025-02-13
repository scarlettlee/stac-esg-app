# src/services/stac_service.py

from datetime import datetime, timezone
from typing import List, Dict, Any, Tuple
from pystac_client import Client
from utils.date_utils import parse_date, temporal_intersects
from utils.spatial_utils import bbox_intersects

def initialize_stac_client(stac_url: str = "https://planetarycomputer.microsoft.com/api/stac/v1") -> Client:
    """
    Initialize a STAC client with the given URL.
    
    Args:
        stac_url (str): URL of the STAC API endpoint
        
    Returns:
        Client: Initialized STAC client
    """
    return Client.open(stac_url)


def process_temporal_filter(temporal_filter: str) -> List[str]:
    """
    Process temporal filter string into a list of dates.
    
    Args:
        temporal_filter (str): Comma-separated date range (e.g., "2020-01-01, 2025-12-31")
        
    Returns:
        List[str]: List containing start and end dates
    """
    return [date.strip() for date in temporal_filter.split(",")]


def get_collection_info(collection: Any) -> Dict[str, str]:
    """
    Extract relevant information from a STAC collection.
    
    Args:
        collection: STAC collection object
        
    Returns:
        Dict[str, str]: Dictionary containing collection information
    """
    return {
        "id": collection.id,
        "title": getattr(collection, 'title', 'No title'),
        "description": collection.description,
        "keywords": getattr(collection, 'keywords', []),
        "license": getattr(collection, 'license', 'No license information'),
        "providers": [provider.name for provider in getattr(collection, 'providers', [])]
    }


def search_stac_collections(
    bbox_filter: List[float],
    temporal_filter: str,
    client: Client = None
) -> Tuple[List[Dict[str, Any]], List[Dict[str, str]]]:
    """
    Search for STAC collections that intersect with given spatial and temporal filters.
    
    Args:
        bbox_filter (List[float]): Bounding box coordinates [min_lon, min_lat, max_lon, max_lat]
        temporal_filter (str): Comma-separated date range
        client (Client, optional): STAC client instance
        
    Returns:
        Tuple[List[Dict], List[Dict]]: Matching collections and their detailed information
    """
    try:
        # Initialize client if not provided
        if client is None:
            client = initialize_stac_client()

        # Get temporal filter dates
        temporal_dates = process_temporal_filter(temporal_filter)

        # Get all collections
        collections = client.get_collections()

        # Filter collections based on spatial and temporal criteria
        matching_collections = []
        collection_info = []

        for collection in collections:
            # Get spatial extent
            spatial_extent = collection.extent.spatial.bboxes[0]
            
            # Get temporal extent
            temporal_extent = collection.extent.temporal.intervals[0]

            # Check if collection intersects with filters
            if (bbox_intersects(spatial_extent, bbox_filter) and 
                temporal_intersects(temporal_extent, temporal_dates)):
                
                matching_collections.append(collection)
                collection_info.append(get_collection_info(collection))

        return matching_collections, collection_info

    except Exception as e:
        raise Exception(f"Error searching STAC collections: {str(e)}")


def get_collection_assets(collection: Any) -> Dict[str, Any]:
    """
    Get available assets from a collection.
    
    Args:
        collection: STAC collection object
        
    Returns:
        Dict[str, Any]: Dictionary of asset information
    """
    assets = {}
    if hasattr(collection, 'assets'):
        for asset_key, asset in collection.assets.items():
            assets[asset_key] = {
                "title": getattr(asset, 'title', 'No title'),
                "description": getattr(asset, 'description', 'No description'),
                "type": getattr(asset, 'type', 'No type information'),
                "roles": getattr(asset, 'roles', [])
            }
    return assets


def get_collection_metadata(collection: Any) -> Dict[str, Any]:
    """
    Get comprehensive metadata for a collection.
    
    Args:
        collection: STAC collection object
        
    Returns:
        Dict[str, Any]: Dictionary containing collection metadata
    """
    return {
        **get_collection_info(collection),
        "assets": get_collection_assets(collection),
        "spatial_extent": collection.extent.spatial.bboxes[0],
        "temporal_extent": [
            date.isoformat() if date else None 
            for date in collection.extent.temporal.intervals[0]
        ],
        "properties": getattr(collection, 'extra_fields', {})
    }