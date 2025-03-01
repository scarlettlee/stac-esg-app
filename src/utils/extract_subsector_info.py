import pandas as pd

def extract_subsector_info(file_path, subsector):
    # Load the Excel file
    xls = pd.ExcelFile(file_path)
    
    # Load the specific sheet
    df = pd.read_excel(xls, 'Sustainability Disclosure Topic')
    
    # Filter the data for the given subsector
    filtered_data = df[df['Sector'] == subsector]
    
    return filtered_data

subsector_info = extract_subsector_info('./src/data/SASB standard.xlsx', 'Apparel, Accessories & Footwear')
print(subsector_info)
