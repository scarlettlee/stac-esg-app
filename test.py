# from openai import OpenAI
# client = OpenAI(base_url="https://genai.science-cloud.hu/ollama/v1/", api_key="sk-78f50a026b6445c99a14dc7ccef78fde")

# print(client.models.list())

# response = client.chat.completions.create(
#   model="llama3.1:8b",
#   messages=[
#     {"role": "system", "content": "You are a helpful assistant."},
#     {"role": "user", "content": "What is a LLM?"}
#   ]
# )

# print(response)

# from openai import OpenAI

# client = OpenAI(
#     base_url = 'http://localhost:11434/v1',
#     api_key='ollama', # required, but unused
# )

# response = client.chat.completions.create(
#   model="llama2",
#   messages=[
#     {"role": "system", "content": "You are a helpful assistant."},
#     {"role": "user", "content": "Who won the world series in 2020?"},
#     {"role": "assistant", "content": "The LA Dodgers won in 2020."},
#     {"role": "user", "content": "Where was it played?"}
#   ]
# )
# print(response.choices[0].message.content)

# import ee
# ee.Authenticate()
# ee.Initialize(project='scarlettlee33')
# print(ee.String('Hello from the Earth Engine servers!').getInfo())

# import ee

# try:
#     # Try to initialize without authentication first
#     ee.Initialize(project='scarlettlee33')
#     print('get here')
# except Exception as e:
#     # If initialization fails, try authenticating first
#     ee.Authenticate()
#     ee.Initialize(project='scarlettlee33')
#     print('get here 1')

# # Test the connection
# print(ee.String('Hello from the Earth Engine servers!').getInfo())

# import ee
# ee.Reset()  # Clear existing credentials
# ee.Authenticate()  # Re-authenticate
# ee.Initialize()

################################################################################
from pystac_client import Client
from datetime import datetime
from pystac_client import Client
import matplotlib.pyplot as plt
import rioxarray
import numpy as np
import requests
from io import BytesIO
from PIL import Image
import folium
from matplotlib.colors import Normalize
import folium
from pystac_client import Client
import rioxarray
import numpy as np
import matplotlib.pyplot as plt
import io
import base64
from folium import raster_layers

# URL of the STAC API
stac_api_url = "https://earth-search.aws.element84.com/v1"

# Connect to the STAC API
client = Client.open(stac_api_url)

# # List all collections
# collections = client.get_collections()
# for collection in collections:
#     print(f"Collection ID: {collection.id}")

# Define search parameters
search_params = {
    "collections": ["sentinel-2-l2a"],  # Specify the collection(s) you want to search
    "bbox": [-123.0, 44.0, -121.0, 46.0],     # Define a bounding box [min lon, min lat, max lon, max lat]
    "datetime": "2022-12-31/2023-01-01",      # Define time range as an interval; can also use a single date
    "max_items": 10                           # Limit the number of items returned
}

# Perform the search
search_results = client.search(**search_params)

# # Iterate over the items in the search result
# for item in search_results.items():
#     # Perform operations with each item (e.g., print item details)
#     print(f"Item ID: {item.id}")
#     print(f"Item Properties: {item.properties}")
#     print(f"Links: {item.links}")

# Get the first item from the search results
item = next(search_results.items())
print(f"Working with item: {item.id}")
# Get the bounding box from the item
bbox = item.bbox
print(f"Image bounding box: {bbox}")

# # List all the available assets
# print("\nAvailable assets:")
# for asset_key, asset in item.assets.items():
#     print(f"- {asset_key}: {asset.title if asset.title else 'No title'}")

# # Method 1: Display a pre-generated thumbnail
# if 'thumbnail' in item.assets:
#     thumbnail_url = item.assets['thumbnail'].href
#     response = requests.get(thumbnail_url)
#     img = Image.open(BytesIO(response.content))
    
#     plt.figure(figsize=(10, 10))
#     plt.imshow(img)
#     plt.axis('off')
#     plt.title("Thumbnail from STAC Item")
#     plt.show()


# # Method 3: Display a single band as a grayscale image
# try:
#     # Try to access and display a single band (e.g., near-infrared)
#     if 'nir08' in item.assets:
#         nir_band = rioxarray.open_rasterio(item.assets['nir08'].href)
        
#         plt.figure(figsize=(10, 10))
#         plt.imshow(nir_band.values[0], cmap='gray')
#         plt.colorbar(label='Near Infrared Reflectance')
#         plt.title("Near Infrared Band (B08)")
#         plt.axis('off')
#         plt.show()
# except Exception as e:
#     print(f"Error displaying single band: {str(e)}")

# Method 2: Create a false-color composite from bands
# For Sentinel-2, common combinations are:
# - Natural color: Red (B04), Green (B03), Blue (B02)
# - False color infrared: NIR (B08), Red (B04), Green (B03)
# - Agriculture: SWIR (B11), NIR (B08), Blue (B02)
# Function to create a true color image
def create_rgb_image(item):
    # Load the red, green, and blue bands
    # These are typically B04 (red), B03 (green), B02 (blue) for Sentinel-2
    red_band = rioxarray.open_rasterio(item.assets['red'].href)
    green_band = rioxarray.open_rasterio(item.assets['green'].href)
    blue_band = rioxarray.open_rasterio(item.assets['blue'].href)
    
    # Normalize the bands (Sentinel-2 L2A data is typically 0-10000)
    red_norm = red_band / 10000.0
    green_norm = green_band / 10000.0
    blue_norm = blue_band / 10000.0
    
    # Stack the bands to create an RGB image
    rgb = np.dstack([
        red_norm.values[0],
        green_norm.values[0],
        blue_norm.values[0]
    ])
    
    # Enhance contrast for better visualization
    # Apply a simple percentile stretch (2% to 98%)
    for i in range(3):
        p_low, p_high = np.percentile(rgb[:,:,i], [2, 98])
        rgb[:,:,i] = np.clip((rgb[:,:,i] - p_low) / (p_high - p_low), 0, 1)
    
    return rgb, [
        float(red_band.x.min().values), 
        float(red_band.y.min().values), 
        float(red_band.x.max().values), 
        float(red_band.y.max().values)
    ]

try:
    # Create RGB image
    print("Creating RGB composite...")
    rgb_image, image_extent = create_rgb_image(item)
    
    # Create a figure and save it to a buffer
    print("Creating image for map overlay...")
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.imshow(rgb_image)
    ax.axis('off')
    
    # Save figure to a PNG in memory
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0, dpi=150)
    buf.seek(0)
    
    # Encode the PNG as base64
    img_str = base64.b64encode(buf.read()).decode()
    
    # Create a Folium map centered on the image
    center_lat = (bbox[1] + bbox[3]) / 2
    center_lon = (bbox[0] + bbox[2]) / 2
    
    print("Creating Folium map...")
    m = folium.Map(location=[center_lat, center_lon], zoom_start=10)
    
    # Add the image overlay to the map
    # Note: We use the actual bounds from the image for precise positioning
    raster_layers.ImageOverlay(
        image=f"data:image/png;base64,{img_str}",
        bounds=[[bbox[1], bbox[0]], [bbox[3], bbox[2]]],
        opacity=0.8,
        name="Sentinel-2 Image"
    ).add_to(m)
    
    # Add a rectangle to show the original bounds
    folium.Rectangle(
        bounds=[[bbox[1], bbox[0]], [bbox[3], bbox[2]]],
        color='red',
        weight=2,
        fill=False,
        name="Image Footprint"
    ).add_to(m)
    
    # Add layer control
    folium.LayerControl().add_to(m)
    
    # Display the map
    print("Map created successfully")
    m.save("sentinel2_on_folium.html")
    print("Map saved to sentinel2_on_folium.html")
    
    # In Jupyter, you would just display the map with:
    # m

except Exception as e:
    print(f"Error: {str(e)}")
    print("This might happen if the assets require authentication or if the images are not directly accessible.")

# def create_true_color_composite():
#     # Load the red, green, and blue bands
#     red_band = rioxarray.open_rasterio(item.assets['red'].href)
#     green_band = rioxarray.open_rasterio(item.assets['green'].href)
#     blue_band = rioxarray.open_rasterio(item.assets['blue'].href)
    
#     # Normalize each band to 0-1 range for visualization
#     # Sentinel-2 bands are typically in the range 0-10000
#     red_norm = red_band / 10000.0
#     green_norm = green_band / 10000.0
#     blue_norm = blue_band / 10000.0
    
#     # Stack the bands into an RGB image
#     rgb = np.stack([red_norm.values[0], green_norm.values[0], blue_norm.values[0]], axis=-1)
    
#     # Apply some contrast enhancement
#     # Clip values to a percentile range to enhance visibility
#     p_low, p_high = 2, 98
#     for i in range(3):
#         p_low_val = np.percentile(rgb[:,:,i], p_low)
#         p_high_val = np.percentile(rgb[:,:,i], p_high)
#         rgb[:,:,i] = np.clip((rgb[:,:,i] - p_low_val) / (p_high_val - p_low_val), 0, 1)
    
#     return rgb, red_band

# try:
#     # # Create a true color composite
#     # rgb_image, reference_band = create_true_color_composite()
    
#     # # Plot the RGB image
#     # plt.figure(figsize=(12, 12))
#     # plt.imshow(rgb_image)
#     # plt.axis('off')
#     # plt.title("True Color Composite (R-G-B)")
#     # plt.show()
    
#     # Get the bounding box from the item's geometry
#     bbox = item.bbox
    
#     # Create a folium map centered on the area
#     center_lat = (bbox[1] + bbox[3]) / 2
#     center_lon = (bbox[0] + bbox[2]) / 2
    
#     m = folium.Map(location=[center_lat, center_lon], zoom_start=10)
    
#     # Add a rectangle to show the image footprint
#     folium.Rectangle(
#         bounds=[(bbox[1], bbox[0]), (bbox[3], bbox[2])],
#         color='red',
#         fill=True,
#         fill_opacity=0.2,
#         popup=f"Image: {item.id}"
#     ).add_to(m)
#     m.save("simple_map1.html")
    
#     # Display the map
#     m

# except Exception as e:
#     print(f"Error creating composite: {str(e)}")
#     print("This might happen if the assets require authentication or if the COG format is not directly accessible.")
#     print("In such cases, you might need to use a specific SDK for the provider or download the data first.")

################################################################################
