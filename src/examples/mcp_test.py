"""
STAC-ESG-App MCP Framework Test Script (Lightweight Version)

This script demonstrates the MCP framework by:
1. Fetching real satellite imagery from Microsoft Planetary Computer
2. Displaying image metadata and preview
3. Showing how the STAC Provider works

Perfect for testing ESG Provider implementations!

HOW TO RUN:
-----------
From project root:
    python src/examples/mcp_test.py

Or from examples directory:
    cd src/examples
    python mcp_test.py

WHAT IT DOES:
-------------
- Fetches a small preview image (fast, ~15-30 seconds)
- Shows satellite data for Auckland, New Zealand
- Displays the image in a matplotlib window
- Demonstrates how to use MCP providers

REQUIREMENTS:
-------------
- All dependencies from requirements.txt installed
- Internet connection (to access Microsoft Planetary Computer)
- matplotlib for visualization

NOTE: This fetches actual satellite data, so it may take 15-30 seconds to complete.
"""

import sys
import os
from pathlib import Path
import matplotlib.pyplot as plt
import requests
from io import BytesIO
from PIL import Image

# Add parent directory to sys.path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.mcp import registry
import planetary_computer


def test_mcp_framework():
    print("Testing MCP Framework (Lightweight Preview)...")

    # Get the STACImageProvider
    provider = registry.get_provider("STACImageProvider")
    if not provider:
        print("Error: STACImageProvider not found in registry")
        return

    print(f"Provider: {provider.get_name()}")
    print(f"Description: {provider.get_description()}")
    print(f"Capabilities: {', '.join(provider.get_capabilities())}")

    # Define search parameters
    collection_id = "sentinel-2-l2a"
    bbox = [174.80, -36.87, 174.86, -36.81]  # Smaller area of Auckland, NZ
    time_range = "2023-01-01/2024-01-01"

    print(f"\nSearching for {collection_id} images in Auckland, NZ...")
    items = provider.fetch_image(
        collection_id=collection_id,
        bbox=bbox,
        time_range=time_range
    )

    if not items:
        print("No items found")
        return

    print(f"Found {len(items)} items")

    # Use first item
    item = items[0]
    details = provider.get_item_details(item)

    print("\nItem details:")
    print(f"ID: {details['id']}")
    print(f"Date: {details['datetime']}")
    print(f"Cloud cover: {details['cloud_cover']}%")
    print(f"Available assets: {', '.join(details['available_assets'])}")

    print("\nFetching lightweight preview (rendered_preview/visual)...")

    # Sign the item to access Microsoft Planetary Computer assets
    signed_item = planetary_computer.sign(item)

    # Prefer rendered_preview, fallback to visual
    asset = signed_item.assets.get("rendered_preview") or signed_item.assets.get("visual")

    if asset is None:
        print("No quicklook asset found (rendered_preview/visual missing).")
        return

    # Fetch the preview image
    response = requests.get(asset.href, timeout=60)
    response.raise_for_status()
    img = Image.open(BytesIO(response.content))

    print("Success: preview image fetched")
    print(f"Preview size: {img.size}, format: {img.format}")

    # Show the image
    plt.figure(figsize=(8, 8))
    plt.imshow(img)
    plt.title(f"{collection_id} preview – {details['datetime']}")
    plt.axis("off")
    plt.show()

    print("\nLightweight MCP Framework test complete!")


if __name__ == "__main__":
    test_mcp_framework()
