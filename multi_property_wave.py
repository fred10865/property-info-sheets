from h2o_wave import site, ui, on, handle_on
import pandas as pd
import os
from datetime import datetime
import glob

def get_property_files():
    """Get list of all Excel files that could be property info sheets."""
    # Look for Excel files in the current directory
    excel_files = glob.glob("*.xlsx")
    return [f for f in excel_files if not f.startswith('~')]  # Exclude temp files

def load_excel_data(filename):
    """Load Excel data from specific file and parse into sections."""
    if not os.path.exists(filename):
        return {}, None
    
    try:
        df = pd.read_excel(filename, sheet_name='Property Info', header=None)
        
        # Extract data with exact field mapping from Excel
        data = {}
        
        # Read the actual values from the Excel file
        for idx, row in df.iterrows():
            if pd.notna(row.iloc[0]):
                field_name = str(row.iloc[0]).strip()
                field_value = str(row.iloc[1]) if pd.notna(row.iloc[1]) else ""
                data[field_name] = field_value
        
        return data, df
    except Exception as e:
        print(f"Error loading {filename}: {e}")
        return {}, None

def create_property_selector():
    """Create a page that lists all available properties."""
    page = site['/properties']
    page.drop()
    
    excel_files = get_property_files()
    
    items = [
        ui.text_xl('Property Info Sheets'),
        ui.text('Select a property to view/edit its information sheet:'),
        ui.separator(),
    ]
    
    if excel_files:
        for file in excel_files:
            property_name = file.replace('.xlsx', '').replace('_', ' ').title()
            items.extend([
                ui.link(
                    label=property_name,
                    path=f'/property/{file.replace(".xlsx", "")}',
                    button=True
                ),
                ui.text(f'File: {file}'),
                ui.separator(),
            ])
    else:
        items.append(ui.text('No Excel files found in the current directory.'))
    
    items.extend([
        ui.separator(),
        ui.text('**URLs for CRM Integration:**'),
        ui.text('Use these URLs in your CRM to link directly to property sheets:'),
    ])
    
    for file in excel_files:
        property_id = file.replace('.xlsx', '')
        url = f'http://localhost:10101/property/{property_id}'
        items.extend([
            ui.text(f'**{property_id}**: `{url}`'),
        ])
    
    page['selector'] = ui.form_card(
        box='1 1 12 -1',
        items=items
    )
    
    page.save()

def create_property_editor(property_id):
    """Create the property editor for a specific property file."""
    filename = f"{property_id}.xlsx"
    data, df = load_excel_data(filename)
    
    if df is None:
        # Create error page if file doesn't exist
        page = site[f'/property/{property_id}']
        page.drop()
        page['error'] = ui.form_card(
            box='1 1 12 6',
            items=[
                ui.text_xl(f'Property Not Found: {property_id}'),
                ui.text(f'The file "{filename}" was not found.'),
                ui.text('Please check the property ID or ensure the Excel file exists.'),
                ui.button('back_to_list', 'Back to Property List', path='/properties'),
            ]
        )
        page.save()
        return
    
    page = site[f'/property/{property_id}']
    page.drop()  # Clear existing content
    
    property_name = property_id.replace('_', ' ').title()
    
    # Header with title and save button
    page['header'] = ui.form_card(
        box='1 1 12 3',
        items=[
            ui.text_xl(f'Property Info Sheet: {property_name}'),
            ui.text(f'File: {filename}'),
            ui.button('back_to_list', 'Back to Property List', path='/properties'),
            ui.button(f'save_{property_id}', 'Save Changes', primary=True),
        ]
    )
    
    # Left Column: Property Information
    property_info_items = [
        ui.text_l('**Property Information**'),
        ui.textbox(f'{property_id}_address', 'Address', value=data.get('Address', '')),
        ui.textbox(f'{property_id}_google_maps_link', 'Google Maps Link', value=data.get('Google Maps Link', '')),
        ui.textbox(f'{property_id}_lot_number', 'Lot Number', value=data.get('Lot Number', '')),
        ui.textbox(f'{property_id}_borough', 'Borough', value=data.get('Borough', '')),
        ui.textbox(f'{property_id}_year_construction', 'Year of construction', value=data.get('Year of construction', '')),
        ui.textbox(f'{property_id}_total_building_sf', 'Total Building SF', value=data.get('Total Building SF', '')),
        ui.textbox(f'{property_id}_google_maps_building_sf', 'Google Maps Building SF', value=data.get('Google Maps Building SF', '')),
        ui.textbox(f'{property_id}_floor_plate', 'Floor Plate', value=data.get('Floor Plate', '')),
        ui.textbox(f'{property_id}_land_sf', 'Land SF', value=data.get('Land SF', '')),
        ui.textbox(f'{property_id}_ceiling_height', 'Ceiling Height', value=data.get('Ceiling Height', '')),
        ui.textbox(f'{property_id}_docks', 'Docks - google or vendor?', value=data.get('Docks - google or vendor?', '')),
        ui.textbox(f'{property_id}_column_distance', 'Column Distance', value=data.get('Column Distance', '')),
        ui.textbox(f'{property_id}_amps', 'Amps', value=data.get('Amps', '')),
    ]
    
    page['property_info'] = ui.form_card(
        box='1 4 6 14',
        items=property_info_items
    )
    
    # Right Column Top: Owner Information
    owner_info_items = [
        ui.text_l('**Owner Information**'),
        ui.textbox(f'{property_id}_names_owners', 'Names of Owners', value=data.get('Names of Owners', '')),
        ui.textbox(f'{property_id}_other_properties', 'Other Properties', value=data.get('Other Properties', '')),
        ui.textbox(f'{property_id}_contact_info', 'Contact Info', value=data.get('Contact Info', '')),
        ui.textbox(f'{property_id}_vendor_goes_by', 'Vendor Goes By', value=data.get('Vendor Goes By', '')),
    ]
    
    page['owner_info'] = ui.form_card(
        box='7 4 6 5',
        items=owner_info_items
    )
    
    # Right Column Middle: Title
    title_items = [
        ui.text_l('**Title**'),
        ui.textbox(f'{property_id}_previous_sale_price', 'Previous Sale Price', value=data.get('Previous Sale Price', '')),
        ui.textbox(f'{property_id}_active_mortgage', 'Active Mortgage', value=data.get('Active Mortgage', '')),
        ui.textbox(f'{property_id}_registered_leases', 'Registered Leases', value=data.get('Registered Leases', '')),
        ui.textbox(f'{property_id}_other_notes', 'Other Notes', value=data.get('Other Notes', '')),
    ]
    
    page['title_info'] = ui.form_card(
        box='7 9 6 5',
        items=title_items
    )
    
    # Right Column Bottom: Important Info
    important_info_items = [
        ui.text_l('**Important Info**'),
        ui.textbox(f'{property_id}_sale_conditions', 'Sale Conditions', value=data.get('Sale Conditions', '')),
        ui.textbox(f'{property_id}_leaseback_terms', 'Leaseback Terms', value=data.get('Leaseback Terms', '')),
        ui.textbox(f'{property_id}_business_for_sale', 'Business for Sale', value=data.get('Business for Sale', '')),
        ui.textbox(f'{property_id}_owns_surrounding', 'Owns surrounding lots', value=data.get('Owns surrounding lots', '')),
        ui.textbox(f'{property_id}_type_property', 'Type of Property', value=data.get('Type of Property', 'See comment for instructions')),
    ]
    
    page['important_info'] = ui.form_card(
        box='7 14 6 6',
        items=important_info_items
    )
    
    # Building Breakdown Section
    building_items = [
        ui.text_l('**Building Breakdown**'),
        ui.textbox(f'{property_id}_building_total_sf', 'Total Building SF', value=data.get('Total Building SF', '')),
        ui.textbox(f'{property_id}_warehouse_space', 'Warehouse Space', value=data.get('Warehouse Space', '')),
        ui.textbox(f'{property_id}_mezzanine_space', 'Mezzanine Space', value=data.get('Mezzanine Space', '')),
        ui.textbox(f'{property_id}_office_space_sf', 'Office Space SF', value=data.get('Office Space SF', '')),
        ui.textbox(f'{property_id}_percent_office', '% of Office', value=data.get('% of Office', '')),
    ]
    
    page['building_breakdown'] = ui.form_card(
        box='1 18 6 6',
        items=building_items
    )
    
    # Our Offer and Vendor's Asking
    offer_items = [
        ui.text_l('**Our Offer**'),
        ui.textbox(f'{property_id}_purchase_price', 'Purchase Price', value=data.get('Purchase Price', '')),
        ui.textbox(f'{property_id}_price_psf_building', 'Price PSF of Building', value=data.get('Price PSF of Building', '')),
        ui.textbox(f'{property_id}_price_psf_land', 'Price PSF of Land', value=data.get('Price PSF of Land', '')),
        ui.textbox(f'{property_id}_net_rent_psf', 'Net Rent PSF', value=data.get('Net Rent PSF', '')),
        ui.textbox(f'{property_id}_cap_rate', 'Cap Rate', value=data.get('Cap Rate', '')),
    ]
    
    page['our_offer'] = ui.form_card(
        box='1 24 6 6',
        items=offer_items
    )
    
    vendor_asking_items = [
        ui.text_l('**Vendor\'s Asking**'),
        ui.textbox(f'{property_id}_vendor_purchase_price', 'Purchase Price', value=''),
        ui.textbox(f'{property_id}_vendor_price_psf_building', 'Price PSF of Building', value=''),
        ui.textbox(f'{property_id}_vendor_price_psf_land', 'Price PSF of Land', value=''),
        ui.textbox(f'{property_id}_vendor_net_rent_psf', 'Net Rent PSF', value=''),
        ui.textbox(f'{property_id}_vendor_cap_rate', 'Cap Rate', value=''),
    ]
    
    page['vendor_asking'] = ui.form_card(
        box='7 24 6 6',
        items=vendor_asking_items
    )
    
    # Income Section
    income_items = [
        ui.text_l('**Income**'),
        ui.textbox(f'{property_id}_gross_income_year', 'Gross Income / Year', value=data.get('Gross Income / Year', '')),
        ui.textbox(f'{property_id}_gross_income_sqft', 'Gross income per Sq Ft', value=data.get('Gross income per Sq Ft', '')),
        ui.textbox(f'{property_id}_opex_year', 'OPEX / Year', value=data.get('OPEX / Year', '')),
        ui.textbox(f'{property_id}_opex_sqft', 'OPEX per Sq Ft', value=data.get('OPEX per Sq Ft', '')),
        ui.textbox(f'{property_id}_net_income_year', 'Net Income / Year', value=data.get('Net Income / Year', '0')),
        ui.textbox(f'{property_id}_net_income_sqft', 'Net Income per Sq Ft', value=data.get('Net Income per Sq Ft', '0')),
        ui.textbox(f'{property_id}_occupancy_percent', 'Occupancy %', value=data.get('Occupancy %', '')),
    ]
    
    page['income'] = ui.form_card(
        box='1 30 6 9',
        items=income_items
    )
    
    # Questions Section
    questions_items = [
        ui.text_l('**Questions**'),
        ui.textbox(f'{property_id}_questions', 'Questions/Notes', value=''),
    ]
    
    page['questions'] = ui.form_card(
        box='7 30 6 9',
        items=questions_items
    )
    
    page.save()

@on()
async def save_property(q):
    """Handle save button click for specific property."""
    # Extract property ID from button name
    button_name = [key for key in q.args.keys() if key.startswith('save_')][0]
    property_id = button_name.replace('save_', '')
    filename = f"{property_id}.xlsx"
    
    try:
        # Load current Excel file
        df = pd.read_excel(filename, sheet_name='Property Info', header=None)
        
        # Create backup
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f'{property_id}_backup_{timestamp}.xlsx'
        
        if os.path.exists(filename):
            import shutil
            shutil.copy2(filename, backup_name)
        
        # Field mapping for updates
        field_mapping = {
            f'{property_id}_address': 'Address',
            f'{property_id}_google_maps_link': 'Google Maps Link',
            f'{property_id}_lot_number': 'Lot Number',
            f'{property_id}_borough': 'Borough',
            f'{property_id}_year_construction': 'Year of construction',
            f'{property_id}_total_building_sf': 'Total Building SF',
            f'{property_id}_google_maps_building_sf': 'Google Maps Building SF',
            f'{property_id}_floor_plate': 'Floor Plate',
            f'{property_id}_land_sf': 'Land SF',
            f'{property_id}_ceiling_height': 'Ceiling Height',
            f'{property_id}_docks': 'Docks - google or vendor?',
            f'{property_id}_column_distance': 'Column Distance',
            f'{property_id}_amps': 'Amps',
            f'{property_id}_names_owners': 'Names of Owners',
            f'{property_id}_other_properties': 'Other Properties',
            f'{property_id}_contact_info': 'Contact Info',
            f'{property_id}_vendor_goes_by': 'Vendor Goes By',
            f'{property_id}_previous_sale_price': 'Previous Sale Price',
            f'{property_id}_active_mortgage': 'Active Mortgage',
            f'{property_id}_registered_leases': 'Registered Leases',
            f'{property_id}_other_notes': 'Other Notes',
            f'{property_id}_sale_conditions': 'Sale Conditions',
            f'{property_id}_leaseback_terms': 'Leaseback Terms',
            f'{property_id}_business_for_sale': 'Business for Sale',
            f'{property_id}_owns_surrounding': 'Owns surrounding lots',
            f'{property_id}_type_property': 'Type of Property',
            f'{property_id}_building_total_sf': 'Total Building SF',
            f'{property_id}_warehouse_space': 'Warehouse Space',
            f'{property_id}_mezzanine_space': 'Mezzanine Space',
            f'{property_id}_office_space_sf': 'Office Space SF',
            f'{property_id}_percent_office': '% of Office',
            f'{property_id}_purchase_price': 'Purchase Price',
            f'{property_id}_price_psf_building': 'Price PSF of Building',
            f'{property_id}_price_psf_land': 'Price PSF of Land',
            f'{property_id}_net_rent_psf': 'Net Rent PSF',
            f'{property_id}_cap_rate': 'Cap Rate',
            f'{property_id}_gross_income_year': 'Gross Income / Year',
            f'{property_id}_gross_income_sqft': 'Gross income per Sq Ft',
            f'{property_id}_opex_year': 'OPEX / Year',
            f'{property_id}_opex_sqft': 'OPEX per Sq Ft',
            f'{property_id}_net_income_year': 'Net Income / Year',
            f'{property_id}_net_income_sqft': 'Net Income per Sq Ft',
            f'{property_id}_occupancy_percent': 'Occupancy %',
        }
        
        # Update DataFrame with form values
        for form_field, excel_field in field_mapping.items():
            if form_field in q.args:
                # Find the row with this field and update it
                for idx, row in df.iterrows():
                    if pd.notna(row.iloc[0]) and str(row.iloc[0]).strip() == excel_field:
                        df.iloc[idx, 1] = q.args[form_field]
                        break
        
        # Save updated Excel file
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Property Info', index=False, header=False)
        
        q.page['message'] = ui.message_bar(
            type='success',
            text=f'Changes saved successfully! Backup created: {backup_name}',
            box='1 39 12 1'
        )
    except Exception as e:
        q.page['message'] = ui.message_bar(
            type='error',
            text=f'Error saving changes: {str(e)}',
            box='1 39 12 1'
        )
    
    await q.page.save()

# Create property selector page
create_property_selector()

# Create individual property pages for existing files
excel_files = get_property_files()
for file in excel_files:
    property_id = file.replace('.xlsx', '')
    create_property_editor(property_id)

print("H2O Wave Multi-Property System is ready!")
print("Main page: http://localhost:10101/properties")
print("\nProperty URLs for CRM:")
for file in excel_files:
    property_id = file.replace('.xlsx', '')
    print(f"  {property_id}: http://localhost:10101/property/{property_id}")