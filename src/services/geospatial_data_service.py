import streamlit as st
import rasterio
from rasterio.plot import show
import geopandas as gpd
from pystac_client import Client
import planetary_computer
import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO
import requests
import tempfile

def fetch_geospatial_data(collection_id, bbox, time_range):
    """Fetch actual geospatial data items from a STAC collection"""
    
    # Connect to Planetary Computer STAC API
    catalog = Client.open(
        "https://planetarycomputer.microsoft.com/api/stac/v1",
        modifier=planetary_computer.sign_inplace
    )
    
    # Search for items
    search = catalog.search(
        collections=[collection_id],
        bbox=bbox,
        datetime=time_range
    )
    
    # Get all items
    items = list(search.items())
    if not items:
        return None, "No items found for the given parameters"
    
    # For demonstration, use the first item
    item = items[0]
    
    # For raster data (example with Landsat)
    if collection_id in ["landsat-c2-l2", "sentinel-2-l2a"]:
        # Get the visual/RGB asset URL
        if "visual" in item.assets:
            asset = item.assets["visual"]
        elif "red" in item.assets and "green" in item.assets and "blue" in item.assets:
            # Process individual bands to create a composite RGB image
            red_url = planetary_computer.sign(item.assets["red"].href)
            green_url = planetary_computer.sign(item.assets["green"].href)
            blue_url = planetary_computer.sign(item.assets["blue"].href)
            
            # Open each band and stack them to create an RGB image
            with rasterio.open(red_url) as red_src, \
                 rasterio.open(green_url) as green_src, \
                 rasterio.open(blue_url) as blue_src:
                
                red = red_src.read(1)
                green = green_src.read(1)
                blue = blue_src.read(1)
                
                # Stack bands into an RGB image
                rgb_image = np.stack((red, green, blue), axis=-1)
                
                # Ensure dimensions are integers
                height = int(rgb_image.shape[0])
                width = int(rgb_image.shape[1])                

                # Create a temporary file on disk to store the RGB image
                with tempfile.NamedTemporaryFile(delete=False, suffix='.tif') as temp_file:
                    with rasterio.open(
                        temp_file.name, 'w', driver='GTiff',
                        height=height, width=width,
                        count=3, dtype=rgb_image.dtype
                    ) as dst:
                        dst.write(rgb_image[:, :, 0], 1)
                        dst.write(rgb_image[:, :, 1], 2)
                        dst.write(rgb_image[:, :, 2], 3)
                
                # Return the path to the temporary file
                return item, temp_file.name
        else:
            return None, "No suitable visual assets found"
            
        # Get the signed URL for the asset
        url = planetary_computer.sign(asset.href)
        
        # Return the item for further processing
        return item, url
    
    # For vector data (example with building footprints)
    elif collection_id in ["ms-buildings"]:
        if "geojson" in item.assets:
            asset = item.assets["geojson"]
            url = planetary_computer.sign(asset.href)
            return item, url
    
    return None, "Unsupported collection type"

def load_and_display_data(item, url, data_type="raster"):
    """Load and prepare geospatial data for display"""
    
    if data_type == "raster":
        try:
            # For cloud-optimized GeoTIFFs, we can read directly from URL
            with rasterio.open(url, driver='GTiff') as src:
                # Read the data
                image = src.read()
                
                # Get metadata
                metadata = {
                    "bounds": src.bounds,
                    "crs": src.crs,
                    "resolution": src.res,
                    "dimensions": (src.width, src.height),
                }
                
                # Basic statistics
                stats = {
                    "min": np.nanmin(image, axis=(1,2)),
                    "max": np.nanmax(image, axis=(1,2)),
                    "mean": np.nanmean(image, axis=(1,2)),
                    "std": np.nanstd(image, axis=(1,2))
                }
                
                # Display the image using IPython.display.Image
                if "rendered_preview" in item.assets:
                    preview_url = item.assets["rendered_preview"].href
                    st.image(preview_url, width=500)
                else:
                    st.write("Rendered preview not available.")

                return image, metadata, stats
                
        except Exception as e:
            return None, None, f"Error loading raster data: {str(e)}"
    
    elif data_type == "vector":
        try:
            # For GeoJSON data
            response = requests.get(url)
            if response.status_code == 200:
                # Load with geopandas
                gdf = gpd.read_file(BytesIO(response.content))
                
                # Basic statistics for vector attributes
                numeric_columns = gdf.select_dtypes(include=np.number).columns
                stats = {col: {
                    "min": gdf[col].min(),
                    "max": gdf[col].max(),
                    "mean": gdf[col].mean(),
                    "count": gdf[col].count()
                } for col in numeric_columns}
                
                return gdf, gdf.crs, stats
                
        except Exception as e:
            return None, None, f"Error loading vector data: {str(e)}"
    
    return None, None, "Unsupported data type"
