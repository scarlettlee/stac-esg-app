# src/services/gemini_service.py

import streamlit as st
import google.generativeai as genai
import os
from typing import Union

# Configure Gemini API lazily to avoid import-time environment variable issues
_configured = False

def configure_gemini():
    """Configure Gemini API if not already configured."""
    global _configured
    if not _configured:
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable not set")
        genai.configure(api_key=api_key)
        _configured = True

def generate_text(prompt: str, sector: str = None, subsector: str = None) -> Union[str, None]:
    """Generate text using Google Gemini with sector context."""
    try:
        # Configure Gemini API
        configure_gemini()
        
        # Set up the model
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Create sector context
        sector_context = ""
        if sector and subsector:
            sector_context = f"Focus on ESG factors relevant to the {subsector} subsector within the {sector} sector. "
        
        # Combine context and prompt
        full_prompt = sector_context + prompt
        
        # Generate response
        response = model.generate_content(full_prompt)
        
        # Extract the text from the response
        if response.text:
            return response.text.strip()
        else:
            st.error("No response generated from Gemini")
            return None
            
    except Exception as e:
        st.error(f"Error generating text with Gemini: {str(e)}")
        return None

def generate_esg_insights(location: str, sector: str, subsector: str, collections: list) -> str:
    """Generate ESG insights specifically for the application context."""
    try:
        # Configure Gemini API
        configure_gemini()
        
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"""Analyze how the following geospatial data collections could help with ESG assessment for a {subsector} company in the {sector} sector located in {location}.

Focus on:
1. Environmental impact assessment
2. Social responsibility metrics  
3. Governance implications
4. Specific ESG risks and opportunities
5. Data-driven insights and recommendations

Available data collections:
{[collection.id for collection in collections]}

Please provide a comprehensive analysis with actionable insights."""

        response = model.generate_content(prompt)
        
        if response.text:
            return response.text.strip()
        else:
            return "Unable to generate ESG insights at this time."
            
    except Exception as e:
        st.error(f"Error generating ESG insights: {str(e)}")
        return f"Error generating insights: {str(e)}"
