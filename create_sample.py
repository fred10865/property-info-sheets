#!/usr/bin/env python3
"""
Create a sample Excel file for deployment testing
"""
import pandas as pd
import os

def create_sample_excel():
    """Create a sample property Excel file for testing"""
    
    # Sample property data
    data = [
        ['Property Information', ''],
        ['Property Name', 'Sample Property'],
        ['Address', '123 Main Street'],
        ['City', 'Springfield'],
        ['State', 'IL'],
        ['Zip Code', '62701'],
        ['', ''],
        ['Financial Information', ''],
        ['Purchase Price', '$250,000'],
        ['Current Value', '$275,000'],
        ['Monthly Rent', '$1,800'],
        ['Property Tax', '$3,200'],
        ['', ''],
        ['Property Details', ''],
        ['Year Built', '1995'],
        ['Square Feet', '1,500'],
        ['Bedrooms', '3'],
        ['Bathrooms', '2'],
        ['Garage', 'Yes'],
        ['', ''],
        ['Important Info', ''],
        ['Property Manager', 'John Smith'],
        ['Manager Phone', '555-0123'],
        ['Tenant Name', 'Jane Doe'],
        ['Lease End Date', '12/31/2025'],
        ['Notes', 'Great property in excellent condition'],
    ]
    
    # Create DataFrame
    df = pd.DataFrame(data, columns=['Field', 'Value'])
    
    # Save to Excel
    with pd.ExcelWriter('Sample_Property.xlsx', engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Property Info', index=False, header=False)
    
    print("✅ Created Sample_Property.xlsx")

if __name__ == "__main__":
    create_sample_excel()