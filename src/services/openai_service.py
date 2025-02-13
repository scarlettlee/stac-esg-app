# src/services/openai_service.py

import streamlit as st
from openai import OpenAI
import os
from typing import Union

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def generate_text(prompt: str, sector: str = None, subsector: str = None) -> Union[str, None]:
    """Generate text using OpenAI with sector context."""
    try:
        sector_context = ""
        if sector and subsector:
            sector_context = f"Focus on ESG factors relevant to the {subsector} subsector within the {sector} sector. "
        
        full_prompt = sector_context + prompt
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a geospatial data expert and good at ESG research."},
                {"role": "user", "content": full_prompt}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        st.error(f"Error generating text: {str(e)}")
        return None
