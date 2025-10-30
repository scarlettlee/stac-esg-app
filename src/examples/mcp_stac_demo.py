"""
MCP Service Demonstration
Shows how to use MCP (Model Context Protocol) for exposing STAC API access to AI models.

This demonstrates how to:
1. Register MCP tools for STAC operations
2. Call tools programmatically (simulating AI agent behavior)
3. Extend the service with new tools
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.mcp_service import MCPService, get_mcp_service


def demo_basic_mcp_usage():
    """Demonstrate basic MCP service usage."""
    print("=" * 60)
    print("MCP Service Demonstration")
    print("=" * 60)
    
    # Get the MCP service instance
    mcp_service = get_mcp_service()
    
    # List all available tools
    print("\n1. Available MCP Tools:")
    print("-" * 60)
    tools = mcp_service.list_tools()
    for tool in tools:
        print(f"  • {tool['name']}")
        print(f"    Description: {tool['description']}")
        print(f"    Enabled: {tool['enabled']}")
        print()
    
    # Demonstrate STAC search tool
    print("\n2. Demonstrating STAC Search Tool:")
    print("-" * 60)
    try:
        # Example: Search for collections over New York City
        result = mcp_service.call_tool(
            "search_stac_collections",
            {
                "bbox": [-74.05, 40.70, -73.93, 40.80],  # NYC bounding box
                "datetime": "2020-01-01, 2025-12-31"
            }
        )
        print(f"Found {result['count']} matching collections")
        for idx, coll in enumerate(result['collections'][:3], 1):  # Show first 3
            print(f"  {idx}. {coll['id']} - {coll['title']}")
    except Exception as e:
        print(f"Error: {str(e)}")
    
    # Demonstrate geocoding tool
    print("\n3. Demonstrating Geocoding Tool:")
    print("-" * 60)
    try:
        result = mcp_service.call_tool(
            "geocode_location",
            {"location": "Tokyo, Japan"}
        )
        if 'error' not in result:
            print(f"Location: {result['location']}")
            print(f"Coordinates: {result['coordinates']['latitude']:.4f}, {result['coordinates']['longitude']:.4f}")
            print(f"Bounding Box: {result['bounding_box']}")
        else:
            print(f"Error: {result['error']}")
    except Exception as e:
        print(f"Error: {str(e)}")
    
    # Demonstrate ESG topics tool
    print("\n4. Demonstrating ESG Topics Tool:")
    print("-" * 60)
    try:
        result = mcp_service.call_tool(
            "get_esg_topics",
            {"subsector": "Software & IT Services"}
        )
        if 'error' not in result:
            print(f"Subsector: {result['subsector']}")
            print(f"Found {result['count']} ESG topics")
            for idx, topic in enumerate(result['topics'][:3], 1):  # Show first 3
                print(f"  {idx}. {topic['topic']}")
        else:
            print(f"Error: {result['error']}")
    except Exception as e:
        print(f"Error: {str(e)}")


def demo_custom_tool():
    """Demonstrate registering and using a custom tool."""
    print("\n5. Demonstrating Custom Tool Registration:")
    print("-" * 60)
    
    mcp_service = get_mcp_service()
    
    def calculate_area(bbox):
        """Calculate area of a bounding box in square kilometers."""
        min_lon, min_lat, max_lon, max_lat = bbox
        import math
        
        # Rough approximation
        lat_diff = max_lat - min_lat
        lon_diff = max_lon - min_lon
        avg_lat = (min_lat + max_lat) / 2
        
        width_km = lon_diff * 111 * math.cos(math.radians(avg_lat))
        height_km = lat_diff * 111
        
        return width_km * height_km
    
    # Register a custom tool
    mcp_service.register_tool(
        "calculate_bbox_area",
        "Calculate the area of a bounding box in square kilometers",
        {
            "type": "object",
            "properties": {
                "bbox": {
                    "type": "array",
                    "items": {"type": "number"},
                    "description": "Bounding box [min_lon, min_lat, max_lon, max_lat]"
                }
            },
            "required": ["bbox"]
        },
        calculate_area,
        enabled=True
    )
    
    print("Registered new tool: calculate_bbox_area")
    
    # Use the custom tool
    try:
        result = mcp_service.call_tool(
            "calculate_bbox_area",
            {"bbox": [-74.05, 40.70, -73.93, 40.80]}  # NYC
        )
        print(f"Area of NYC bounding box: {result:.2f} km²")
    except Exception as e:
        print(f"Error: {str(e)}")


def demo_ai_agent_simulation():
    """
    Simulate how an AI agent would use MCP tools.
    This demonstrates the pattern for future AI integration.
    """
    print("\n6. Simulating AI Agent Using MCP Tools:")
    print("-" * 60)
    
    mcp_service = get_mcp_service()
    
    # Simulate AI agent workflow:
    # 1. User query: "Find geospatial data for Los Angeles"
    print("User Query: 'Find geospatial data for Los Angeles'")
    print()
    
    # 2. AI agent calls geocoding tool
    print("AI Agent → Calling geocode_location tool...")
    try:
        geo_result = mcp_service.call_tool(
            "geocode_location",
            {"location": "Los Angeles, CA"}
        )
        if 'error' not in geo_result:
            bbox = geo_result['bounding_box']
            print(f"  ✓ Geocoded: {geo_result['location']}")
            print(f"  ✓ Coordinates: {geo_result['coordinates']['latitude']:.4f}, {geo_result['coordinates']['longitude']:.4f}")
    except Exception as e:
        print(f"  ✗ Error: {str(e)}")
        return
    print()
    
    # 3. AI agent calls STAC search tool
    print("AI Agent → Calling search_stac_collections tool...")
    try:
        stac_result = mcp_service.call_tool(
            "search_stac_collections",
            {
                "bbox": bbox,
                "datetime": "2023-01-01, 2024-12-31"
            }
        )
        print(f"  ✓ Found {stac_result['count']} collections")
        for coll in stac_result['collections'][:2]:
            print(f"    - {coll['id']}")
    except Exception as e:
        print(f"  ✗ Error: {str(e)}")
    print()
    
    # 4. AI agent summarizes results
    print("AI Agent → Summary for user:")
    print("  'Found several geospatial datasets for Los Angeles,")
    print(f"  including {stac_result['count']} collections from Microsoft Planetary Computer.'")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("MCP Service with STAC API Integration Demo")
    print("=" * 60)
    
    # Run demonstrations
    demo_basic_mcp_usage()
    demo_custom_tool()
    demo_ai_agent_simulation()
    
    print("\n" + "=" * 60)
    print("Demo Complete!")
    print("=" * 60)
    print("\nKey Takeaways:")
    print("  • MCP tools can be registered and called programmatically")
    print("  • Tools wrap existing services (STAC, Geocoding, ESG)")
    print("  • AI agents can use these tools for data retrieval and analysis")
    print("  • Easy to extend with custom tools for your needs")
    print("\nNext Steps:")
    print("  • Integrate MCP with actual AI agents (Gemini, OpenAI)")
    print("  • Add more STAC-specific tools (item search, asset access)")
    print("  • Create AI workflows that combine multiple tools")

