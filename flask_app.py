#!/usr/bin/env python3
"""
Property Info Sheet Web App - Cloud Deployment Version
Uses Flask as web server with embedded Wave-style UI
"""

from flask import Flask, render_template_string, request, redirect, url_for, jsonify
import pandas as pd
import os
import json
from datetime import datetime
import glob
import shutil

app = Flask(__name__)

# Configuration
PRODUCTION_HOST = "0.0.0.0"
PRODUCTION_PORT = int(os.environ.get("PORT", 8000))

def get_property_files():
    """Get list of Excel files that represent properties"""
    try:
        files = [f for f in glob.glob("*.xlsx") if not f.startswith("~")]
        print(f"📁 Found {len(files)} Excel files: {files}")
        return files
    except Exception as e:
        print(f"⚠️ Error scanning for Excel files: {e}")
        return []

def load_property_data(property_id):
    """Load property data from Excel file with complete multi-section layout"""
    excel_file = f"{property_id}.xlsx"
    if not os.path.exists(excel_file):
        return None
    
    try:
        # Read the Property Info sheet with all columns
        df = pd.read_excel(excel_file, sheet_name='Property Info', header=None)
        
        # Structure the data to match the complete Excel layout
        data = {
            'property_info': [],
            'owner_info': [],
            'title_info': [],
            'important_info': [],
            'building_breakdown': [],
            'our_offer': [],
            'vendor_asking': [],
            'income': [],
            'questions': []
        }
        
        # Process the Excel data row by row
        for idx, row in df.iterrows():
            col_a = str(row[0]) if pd.notna(row[0]) else ""
            col_b = str(row[1]) if pd.notna(row[1]) else ""
            col_c = str(row[2]) if pd.notna(row[2]) else ""
            col_e = str(row[4]) if pd.notna(row[4]) else ""
            col_f = str(row[5]) if pd.notna(row[5]) else ""
            
            # Property Information section (Rows 1-14, Column A-B)
            if 1 <= idx <= 14 and col_a != "nan" and col_a not in ["Property Information", ""]:
                data['property_info'].append({
                    'field': col_a,
                    'value': col_b if col_b != "nan" else "",
                    'row': idx
                })
            
            # Owner Information section (Rows 1-5, Column E-F)
            if 1 <= idx <= 5 and col_e != "nan" and col_e not in ["Owner Information", ""]:
                data['owner_info'].append({
                    'field': col_e,
                    'value': col_f if col_f != "nan" else "",
                    'row': idx
                })
            
            # Title section (Rows 7-11, Column E-F)
            if 7 <= idx <= 11 and col_e != "nan" and col_e not in ["Title", ""]:
                data['title_info'].append({
                    'field': col_e,
                    'value': col_f if col_f != "nan" else "",
                    'row': idx
                })
            
            # Important Info section (Rows 13-18, Column E-F)
            if 13 <= idx <= 18 and col_e != "nan" and col_e not in ["Important Info", ""]:
                data['important_info'].append({
                    'field': col_e,
                    'value': col_f if col_f != "nan" else "",
                    'row': idx
                })
            
            # Building Breakdown section (Rows 16-21, Column A-B)
            if 16 <= idx <= 21 and col_a != "nan" and col_a not in ["Building Breakdown", ""]:
                data['building_breakdown'].append({
                    'field': col_a,
                    'value': col_b if col_b != "nan" else "",
                    'row': idx
                })
            
            # Our Offer section (Rows 23-28, Column A-B)
            if 23 <= idx <= 28 and col_a != "nan" and col_a not in [""]:
                data['our_offer'].append({
                    'field': col_a,
                    'value': col_b if col_b != "nan" else "",
                    'row': idx
                })
            
            # Vendor's Asking section (Rows 23-28, Column C)
            if 23 <= idx <= 28 and col_a != "nan" and col_a not in [""]:
                # Add vendor asking value for the same field
                if data['our_offer'] and data['our_offer'][-1]['row'] == idx:
                    data['our_offer'][-1]['vendor_value'] = col_c if col_c != "nan" else ""
            
            # Income section (Rows 30-37, Column A-B)
            if 30 <= idx <= 37 and col_a != "nan" and col_a not in ["Income", ""]:
                data['income'].append({
                    'field': col_a,
                    'value': col_b if col_b != "nan" else "",
                    'row': idx
                })
            
            # Questions section (Row 29+, Column E-F)
            if idx >= 29 and col_e != "nan" and col_e not in ["Questions", ""]:
                data['questions'].append({
                    'field': col_e,
                    'value': col_f if col_f != "nan" else "",
                    'row': idx
                })
        
        return data
    except Exception as e:
        print(f"Error loading {excel_file}: {e}")
        return None

def save_property_data(property_id, form_data):
    """Save property data back to Excel file with all sections"""
    excel_file = f"{property_id}.xlsx"
    
    # Create backup
    backup_file = f"backups/{property_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    os.makedirs("backups", exist_ok=True)
    if os.path.exists(excel_file):
        shutil.copy2(excel_file, backup_file)
    
    try:
        # Load existing file
        df = pd.read_excel(excel_file, sheet_name='Property Info', header=None)
        
        # Update values in the appropriate columns
        for idx, row in df.iterrows():
            # Check column A (Property Information, Building Breakdown, Our Offer, Income sections)
            if pd.notna(row[0]) and str(row[0]).strip() in form_data:
                field_name = str(row[0]).strip()
                df.iloc[idx, 1] = form_data[field_name]  # Update column B
                
                # Handle vendor asking values (column C)
                vendor_field = f"{field_name}_vendor"
                if vendor_field in form_data:
                    df.iloc[idx, 2] = form_data[vendor_field]  # Update column C
            
            # Check column E (Owner Information, Title, Important Info, Questions sections)
            if pd.notna(row[4]) and str(row[4]).strip() in form_data:
                field_name = str(row[4]).strip()
                df.iloc[idx, 5] = form_data[field_name]  # Update column F
        
        # Save back to Excel
        with pd.ExcelWriter(excel_file, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            df.to_excel(writer, sheet_name='Property Info', index=False, header=False)
        
        return True
    except Exception as e:
        print(f"Error saving {excel_file}: {e}")
        return False

# HTML Templates
PROPERTY_LIST_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Property Info Sheets</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #333; text-align: center; margin-bottom: 30px; }
        .property-list { list-style: none; padding: 0; }
        .property-item { margin: 15px 0; }
        .property-link { display: block; padding: 20px; background: #007acc; color: white; text-decoration: none; border-radius: 5px; transition: background 0.3s; }
        .property-link:hover { background: #005a9e; }
        .info { background: #e7f3ff; padding: 15px; border-radius: 5px; margin-top: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🏠 Property Info Sheets</h1>
        
        {% if properties %}
            <p>Found {{ properties|length }} properties:</p>
            <ul class="property-list">
                {% for property in properties %}
                <li class="property-item">
                    <a href="/property/{{ property }}" class="property-link">
                        📋 {{ property }}
                    </a>
                </li>
                {% endfor %}
            </ul>
            
            <div class="info">
                <strong>💡 For CRM Integration:</strong><br>
                Use the individual property URLs above to link directly from your CRM system.
            </div>
        {% else %}
            <p>No property files found. Upload .xlsx files to get started.</p>
            <p>Expected file format: Property_Name.xlsx</p>
        {% endif %}
    </div>
</body>
</html>
"""

PROPERTY_FORM_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>{{ property_id }} - Property Info</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .container { max-width: 1600px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #333; text-align: center; margin-bottom: 30px; }
        
        /* Main layout - 3 columns to match Excel */
        .excel-layout { 
            display: grid; 
            grid-template-columns: 1fr 1fr 1fr; 
            gap: 20px; 
            margin-bottom: 20px;
        }
        
        /* Section styling to match Excel */
        .section { border: 1px solid #ccc; border-radius: 5px; overflow: hidden; margin-bottom: 20px; }
        .section-header { 
            background: #70ad47; /* Excel green */
            color: white; 
            font-weight: bold; 
            padding: 8px 12px; 
            text-align: center;
            font-size: 13px;
        }
        .section-content { padding: 0; background: white; }
        
        /* Form fields to match Excel cells */
        .field-row { 
            display: grid; 
            grid-template-columns: 180px 1fr; 
            border-bottom: 1px solid #e0e0e0; 
            min-height: 32px;
            align-items: center;
        }
        .field-row:last-child { border-bottom: none; }
        .field-label { 
            padding: 6px 10px; 
            background: #f8f9fa; 
            border-right: 1px solid #e0e0e0;
            font-weight: 500;
            font-size: 12px;
        }
        .field-input { padding: 0; }
        .field-input input, .field-input textarea { 
            width: 100%; 
            border: none; 
            padding: 6px 10px; 
            font-size: 12px;
            background: transparent;
            outline: none;
            box-sizing: border-box;
        }
        .field-input input:focus, .field-input textarea:focus { 
            background: #fff3cd; 
            box-shadow: inset 0 0 3px rgba(0,123,255,0.3);
        }
        .field-input textarea { height: 50px; resize: vertical; }
        
        /* Special layouts for specific sections */
        .offer-vendor-section {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
            margin-bottom: 20px;
        }
        
        .offer-vendor-row {
            display: grid;
            grid-template-columns: 140px 1fr 1fr;
            border-bottom: 1px solid #e0e0e0;
            min-height: 32px;
            align-items: center;
        }
        
        .questions-section .field-input textarea {
            height: 300px;
        }
        
        /* Full width sections */
        .full-width { grid-column: 1 / -1; }
        
        /* Buttons */
        .button-row { margin: 30px 0; text-align: center; grid-column: 1 / -1; }
        .save-btn { 
            background: #28a745; 
            color: white; 
            padding: 12px 30px; 
            border: none; 
            border-radius: 5px; 
            font-size: 16px; 
            cursor: pointer; 
            margin-right: 15px;
        }
        .save-btn:hover { background: #218838; }
        .back-btn { 
            background: #6c757d; 
            color: white; 
            padding: 12px 30px; 
            border: none; 
            border-radius: 5px; 
            font-size: 16px; 
            cursor: pointer; 
            text-decoration: none; 
            display: inline-block;
        }
        .back-btn:hover { background: #545b62; }
        
        /* Messages */
        .message { padding: 15px; margin: 20px 0; border-radius: 5px; }
        .success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
        
        @media (max-width: 1200px) {
            .excel-layout { grid-template-columns: 1fr 1fr; }
        }
        @media (max-width: 768px) {
            .excel-layout { grid-template-columns: 1fr; }
            .field-row { grid-template-columns: 1fr; }
            .field-label { border-right: none; border-bottom: 1px solid #e0e0e0; }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🏠 {{ property_id }}</h1>
        
        {% if message %}
        <div class="message {{ message_type }}">{{ message }}</div>
        {% endif %}
        
        {% if data %}
        <form method="POST">
            <div class="excel-layout">
                <!-- Column 1: Property Information -->
                <div class="column-1">
                    <div class="section">
                        <div class="section-header">Property Information</div>
                        <div class="section-content">
                            {% for item in data.property_info %}
                            <div class="field-row">
                                <div class="field-label">{{ item.field }}</div>
                                <div class="field-input">
                                    {% if item.field in ['Google Maps Link', 'Notes'] %}
                                    <textarea name="{{ item.field }}" placeholder="Enter {{ item.field }}">{{ item.value if item.value != 'nan' else '' }}</textarea>
                                    {% else %}
                                    <input type="text" name="{{ item.field }}" value="{{ item.value if item.value != 'nan' else '' }}" placeholder="Enter {{ item.field }}">
                                    {% endif %}
                                </div>
                            </div>
                            {% endfor %}
                        </div>
                    </div>
                    
                    <div class="section">
                        <div class="section-header">Building Breakdown</div>
                        <div class="section-content">
                            {% for item in data.building_breakdown %}
                            <div class="field-row">
                                <div class="field-label">{{ item.field }}</div>
                                <div class="field-input">
                                    <input type="text" name="{{ item.field }}" value="{{ item.value if item.value != 'nan' else '' }}" placeholder="Enter {{ item.field }}">
                                </div>
                            </div>
                            {% endfor %}
                        </div>
                    </div>
                    
                    <div class="section">
                        <div class="section-header">Income</div>
                        <div class="section-content">
                            {% for item in data.income %}
                            <div class="field-row">
                                <div class="field-label">{{ item.field }}</div>
                                <div class="field-input">
                                    <input type="text" name="{{ item.field }}" value="{{ item.value if item.value != 'nan' else '' }}" placeholder="Enter {{ item.field }}">
                                </div>
                            </div>
                            {% endfor %}
                        </div>
                    </div>
                </div>
                
                <!-- Column 2: Owner Information -->
                <div class="column-2">
                    <div class="section">
                        <div class="section-header">Owner Information</div>
                        <div class="section-content">
                            {% for item in data.owner_info %}
                            <div class="field-row">
                                <div class="field-label">{{ item.field }}</div>
                                <div class="field-input">
                                    <input type="text" name="{{ item.field }}" value="{{ item.value if item.value != 'nan' else '' }}" placeholder="Enter {{ item.field }}">
                                </div>
                            </div>
                            {% endfor %}
                        </div>
                    </div>
                    
                    {% if data.title_info %}
                    <div class="section">
                        <div class="section-header">Title</div>
                        <div class="section-content">
                            {% for item in data.title_info %}
                            <div class="field-row">
                                <div class="field-label">{{ item.field }}</div>
                                <div class="field-input">
                                    <input type="text" name="{{ item.field }}" value="{{ item.value if item.value != 'nan' else '' }}" placeholder="Enter {{ item.field }}">
                                </div>
                            </div>
                            {% endfor %}
                        </div>
                    </div>
                    {% endif %}
                    
                    {% if data.important_info %}
                    <div class="section">
                        <div class="section-header">Important Info</div>
                        <div class="section-content">
                            {% for item in data.important_info %}
                            <div class="field-row">
                                <div class="field-label">{{ item.field }}</div>
                                <div class="field-input">
                                    {% if item.field in ['Type of Property'] %}
                                    <textarea name="{{ item.field }}" placeholder="Enter {{ item.field }}">{{ item.value if item.value != 'nan' else '' }}</textarea>
                                    {% else %}
                                    <input type="text" name="{{ item.field }}" value="{{ item.value if item.value != 'nan' else '' }}" placeholder="Enter {{ item.field }}">
                                    {% endif %}
                                </div>
                            </div>
                            {% endfor %}
                        </div>
                    </div>
                    {% endif %}
                </div>
                
                <!-- Column 3: Questions (large section) -->
                <div class="column-3">
                    {% if data.questions %}
                    <div class="section questions-section">
                        <div class="section-header">Questions</div>
                        <div class="section-content">
                            {% for item in data.questions %}
                            <div class="field-row">
                                <div class="field-label">{{ item.field }}</div>
                                <div class="field-input">
                                    <textarea name="{{ item.field }}" placeholder="Enter {{ item.field }}">{{ item.value if item.value != 'nan' else '' }}</textarea>
                                </div>
                            </div>
                            {% endfor %}
                        </div>
                    </div>
                    {% endif %}
                </div>
                
                <!-- Full Width: Our Offer vs Vendor's Asking -->
                <div class="full-width">
                    {% if data.our_offer %}
                    <div class="section">
                        <div class="section-content">
                            <div class="offer-vendor-row">
                                <div class="field-label" style="background: #70ad47; color: white; text-align: center; padding: 8px; font-weight: bold;">Field</div>
                                <div class="field-label" style="background: #70ad47; color: white; text-align: center; padding: 8px; font-weight: bold;">Our Offer</div>
                                <div class="field-label" style="background: #70ad47; color: white; text-align: center; padding: 8px; font-weight: bold;">Vendor's Asking</div>
                            </div>
                            {% for item in data.our_offer %}
                            <div class="offer-vendor-row">
                                <div class="field-label">{{ item.field }}</div>
                                <div class="field-input">
                                    <input type="text" name="{{ item.field }}" value="{{ item.value if item.value != 'nan' else '' }}" placeholder="Our {{ item.field }}">
                                </div>
                                <div class="field-input">
                                    <input type="text" name="{{ item.field }}_vendor" value="{{ item.vendor_value if item.vendor_value is defined and item.vendor_value != 'nan' else '' }}" placeholder="Vendor {{ item.field }}">
                                </div>
                            </div>
                            {% endfor %}
                        </div>
                    </div>
                    {% endif %}
                </div>
                
                <div class="button-row">
                    <button type="submit" class="save-btn">💾 Save Changes</button>
                    <a href="/properties" class="back-btn">← Back to Properties</a>
                </div>
            </div>
        </form>
        {% else %}
        <p>❌ Could not load property data.</p>
        <a href="/properties" class="back-btn">← Back to Properties</a>
        {% endif %}
    </div>
</body>
</html>
"""

def ensure_sample_data():
    """Create sample Excel file if no property files exist"""
    if not get_property_files():
        print("📝 No Excel files found, creating sample property...")
        try:
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
                ['Notes', 'Great property in excellent condition. Upload your own Excel files to replace this sample.'],
            ]
            
            # Create DataFrame and save
            df = pd.DataFrame(data, columns=['Field', 'Value'])
            with pd.ExcelWriter('Sample_Property.xlsx', engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Property Info', index=False, header=False)
            
            print("✅ Created Sample_Property.xlsx for demonstration")
        except Exception as e:
            print(f"⚠️ Could not create sample file: {e}")

@app.route('/')
def index():
    return redirect(url_for('properties'))

@app.route('/health')
def health_check():
    """Health check endpoint for Railway"""
    return {"status": "healthy", "app": "Property Info Sheets"}, 200

@app.route('/properties')
def properties():
    try:
        property_files = get_property_files()
        properties = [f.replace('.xlsx', '') for f in property_files]
        return render_template_string(PROPERTY_LIST_TEMPLATE, properties=properties)
    except Exception as e:
        print(f"❌ Error in properties route: {e}")
        return f"Error loading properties: {str(e)}", 500

@app.route('/property/<property_id>', methods=['GET', 'POST'])
def property_detail(property_id):
    if request.method == 'POST':
        # Handle form submission
        form_data = request.form.to_dict()
        success = save_property_data(property_id, form_data)
        
        if success:
            message = "✅ Changes saved successfully!"
            message_type = "success"
        else:
            message = "❌ Error saving changes. Please try again."
            message_type = "error"
        
        data = load_property_data(property_id)
        return render_template_string(
            PROPERTY_FORM_TEMPLATE, 
            property_id=property_id, 
            data=data,
            message=message,
            message_type=message_type
        )
    
    # Handle GET request
    data = load_property_data(property_id)
    if data is None:
        return f"Property '{property_id}' not found.", 404
    
    return render_template_string(PROPERTY_FORM_TEMPLATE, property_id=property_id, data=data)

if __name__ == "__main__":
    print("🚀 Starting Property Info Sheet Web App...")
    
    # Get port from environment (Railway sets this automatically)
    port = int(os.environ.get("PORT", 8000))
    host = "0.0.0.0"  # Railway requires 0.0.0.0
    
    print(f"🌐 App will be available on Railway's public URL")
    print(f"🔧 Internal binding: {host}:{port}")
    
    # Create required directories
    os.makedirs("backups", exist_ok=True)
    
    # Ensure we have sample data for demonstration
    ensure_sample_data()
    
    print("✅ App initialization complete - ready to serve requests!")
    
    # Start the Flask app with proper Railway configuration
    app.run(
        host=host, 
        port=port, 
        debug=False,
        threaded=True,
        use_reloader=False
    )