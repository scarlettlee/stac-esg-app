from typing import Dict, List, Any, Union, Optional, Tuple
from .base_provider import MCPBaseProvider
from pystac_client import Client
import planetary_computer
import numpy as np
import rasterio
import tempfile
import os
import logging

logger = logging.getLogger(__name__)

class STACImageProvider(MCPBaseProvider):
    """
    MCP Provider for retrieving actual satellite imagery from STAC collections.
    This is a model implementation for students to understand the MCP framework.
    """
    
    def __init__(self, stac_url: str = "https://planetarycomputer.microsoft.com/api/stac/v1"):
        """
        Initialize the STACImageProvider
        
        Args:
            stac_url: URL of the STAC API
        """
        self.stac_url = stac_url
        self._client = None
    
    def get_name(self) -> str:
        """Return the name of the provider"""
        return "STACImageProvider"
    
    def get_description(self) -> str:
        """Return a description of what the provider does"""
        return "Provides actual satellite imagery retrieval from STAC collections"
    
    def get_capabilities(self) -> List[str]:
        """Return a list of capabilities this provider supports"""
        return [
            "fetch_image", 
            "get_rgb_composite", 
            "get_item_details"
        ]
    
    def _get_client(self) -> Client:
        """
        Get or initialize STAC client
        
        Returns:
            Initialized STAC client
        """
        if self._client is None:
            self._client = Client.open(
                self.stac_url,
                modifier=planetary_computer.sign_inplace
            )
        return self._client
    
    def fetch_image(self, collection_id: str, bbox: List[float], 
                   time_range: str, max_items: int = 1) -> List[Dict[str, Any]]:
        """
        Fetch actual satellite imagery items matching criteria
        
        Args:
            collection_id: STAC collection ID (e.g., "landsat-c2-l2")
            bbox: Bounding box [min_lon, min_lat, max_lon, max_lat]
            time_range: Time range as ISO8601 (e.g., "2020-01-01/2020-12-31")
            max_items: Maximum number of items to return
            
        Returns:
            List of STAC items matching the criteria
        """
        from concurrent.futures import ThreadPoolExecutor, TimeoutError
        import time
        try:
            # Get client
            client = self._get_client()
            
            start_time = time.time()
            logger.info(f"Starting search for collection {collection_id}")
            logger.info(f"Search area: {bbox}")
            logger.info(f"Time range: {time_range}")
            
            def execute_search():
                try:
                    # Search for items matching criteria with relaxed cloud cover
                    search = client.search(
                        collections=[collection_id],
                        bbox=bbox,
                        datetime=time_range,
                        query={
                            "eo:cloud_cover": {"lt": 20},  # Relaxed cloud cover filter (was 2)
                        },
                        limit=5  # Get more results to have options
                    )
                    
                    # Force immediate execution of the search
                    logger.info("Executing STAC API query...")
                    return list(search.items())
                except Exception as e:
                    logger.error(f"Search execution error: {str(e)}")
                    raise
            
            # Execute search with longer timeout
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(execute_search)
                try:
                    items = future.result(timeout=30)  # Increased to 30 second timeout
                    elapsed = time.time() - start_time
                    logger.info(f"Search completed in {elapsed:.2f} seconds, found {len(items)} items")
                    
                    # Return requested number of items
                    return items[:max_items] if items else []
                except TimeoutError:
                    logger.error("Search timed out after 30 seconds")
                    raise Exception("Search is taking too long. The API might be slow. Please try again in a moment.")
                except Exception as e:
                    logger.error(f"Search failed: {str(e)}")
                    raise Exception(f"Failed to search for satellite images: {str(e)}")
            
            # Get items
            items = list(search.items())
            if not items:
                logger.warning(f"No items found for collection {collection_id} in the specified area and time range")
                return []
            
            # Return limited number of items
            return items[:max_items]
            
        except Exception as e:
            logger.error(f"Error fetching images: {str(e)}")
            return []
    
    def get_rgb_composite(self, item: Any, bands: List[str] = ["B04", "B03", "B02"]) -> Tuple[Optional[np.ndarray], str]:
        """
        Create an RGB composite from a STAC item
        
        Args:
            item: STAC item
            bands: List of band names to use for RGB (defaults to Sentinel-2 RGB bands)
            
        Returns:
            Tuple of (numpy array with RGB data or None, message string)
        """
        try:
            if len(bands) != 3:
                return None, "Exactly 3 bands must be provided for RGB composite"
            
            # Check if all bands exist in item
            for band in bands:
                if band not in item.assets:
                    return None, f"Band '{band}' not found in item"
            
            # Get URLs for each band
            urls = [planetary_computer.sign(item.assets[band].href) for band in bands]
            
            # Read bands
            band_data = []
            for url in urls:
                with rasterio.open(url) as src:
                    band_data.append(src.read(1))
            
            # Stack bands into RGB
            rgb_image = np.stack(band_data, axis=-1)
            
            # Normalize for display (simple stretching)
            for i in range(rgb_image.shape[2]):
                band = rgb_image[:, :, i]
                valid = band > 0
                if np.any(valid):
                    p2 = np.percentile(band[valid], 2)
                    p98 = np.percentile(band[valid], 98)
                    rgb_image[:, :, i] = np.clip((band - p2) / (p98 - p2) * 255, 0, 255)
            
            # Convert to uint8 for display
            rgb_image = rgb_image.astype(np.uint8)
            
            return rgb_image, "RGB composite created successfully"
            
        except Exception as e:
            logger.error(f"Error creating RGB composite: {str(e)}")
            return None, f"Error: {str(e)}"
    
    def save_rgb_as_file(self, rgb_image: np.ndarray) -> str:
        """
        Save RGB image to a temporary file
        
        Args:
            rgb_image: RGB image data
            
        Returns:
            Path to temporary file
        """
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.tif') as temp_file:
                # Create RGB GeoTIFF
                height, width = rgb_image.shape[0], rgb_image.shape[1]
                with rasterio.open(
                    temp_file.name, 'w', driver='GTiff',
                    height=height, width=width,
                    count=3, dtype=rgb_image.dtype
                ) as dst:
                    # Write each channel
                    for i in range(3):
                        dst.write(rgb_image[:, :, i], i+1)
                
                return temp_file.name
                
        except Exception as e:
            logger.error(f"Error saving RGB image: {str(e)}")
            return ""
    
    def get_item_details(self, item: Any) -> Dict[str, Any]:
        """
        Get detailed information about a STAC item
        
        Args:
            item: STAC item
            
        Returns:
            Dictionary with item details
        """
        try:
            # Extract basic information
            details = {
                "id": item.id,
                "datetime": item.datetime.isoformat() if hasattr(item, 'datetime') else "Unknown",
                "bbox": item.bbox,
                "collection": item.collection_id if hasattr(item, 'collection_id') else "Unknown",
                "available_assets": list(item.assets.keys()),
                "cloud_cover": item.properties.get("eo:cloud_cover", "Unknown"),
                "platform": item.properties.get("platform", "Unknown"),
                "instrument": item.properties.get("instrument", "Unknown")
            }
            
            return details
            
        except Exception as e:
            logger.error(f"Error getting item details: {str(e)}")
            return {"error": str(e)}