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
    return [f for f in glob.glob("*.xlsx") if not f.startswith("~")]

def load_property_data(property_id):
    """Load property data from Excel file"""
    excel_file = f"{property_id}.xlsx"
    if not os.path.exists(excel_file):
        return None
    
    try:
        # Read the Property Info sheet
        df = pd.read_excel(excel_file, sheet_name='Property Info', header=None)
        
        # Convert to a simple format for web display
        data = {}
        current_section = ""
        
        for idx, row in df.iterrows():
            if pd.notna(row[0]) and row[0].strip():
                field_name = str(row[0]).strip()
                field_value = str(row[1]) if pd.notna(row[1]) else ""
                
                # Check if this is a section header (no value in column B)
                if not field_value or field_value.lower() == 'nan':
                    current_section = field_name
                    if current_section not in data:
                        data[current_section] = {}
                else:
                    if current_section:
                        data[current_section][field_name] = field_value
                    else:
                        data[field_name] = field_value
        
        return data
    except Exception as e:
        print(f"Error loading {excel_file}: {e}")
        return None

def save_property_data(property_id, form_data):
    """Save property data back to Excel file"""
    excel_file = f"{property_id}.xlsx"
    
    # Create backup
    backup_file = f"backups/{property_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    os.makedirs("backups", exist_ok=True)
    if os.path.exists(excel_file):
        shutil.copy2(excel_file, backup_file)
    
    try:
        # Load existing file
        df = pd.read_excel(excel_file, sheet_name='Property Info', header=None)
        
        # Update values
        for idx, row in df.iterrows():
            if pd.notna(row[0]) and row[0].strip():
                field_name = str(row[0]).strip()
                if field_name in form_data:
                    df.iloc[idx, 1] = form_data[field_name]
        
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
        .container { max-width: 1000px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #333; text-align: center; margin-bottom: 30px; }
        .section { margin: 30px 0; padding: 20px; border: 1px solid #ddd; border-radius: 8px; }
        .section-title { font-size: 18px; font-weight: bold; color: #555; margin-bottom: 15px; border-bottom: 2px solid #007acc; padding-bottom: 5px; }
        .form-group { margin: 15px 0; }
        label { display: block; font-weight: bold; margin-bottom: 5px; color: #333; }
        input[type="text"], textarea { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; font-size: 14px; }
        textarea { height: 80px; resize: vertical; }
        .save-btn { background: #28a745; color: white; padding: 15px 30px; border: none; border-radius: 5px; font-size: 16px; cursor: pointer; margin: 20px 10px 20px 0; }
        .save-btn:hover { background: #218838; }
        .back-btn { background: #6c757d; color: white; padding: 15px 30px; border: none; border-radius: 5px; font-size: 16px; cursor: pointer; text-decoration: none; display: inline-block; }
        .back-btn:hover { background: #545b62; }
        .message { padding: 15px; margin: 20px 0; border-radius: 5px; }
        .success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
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
            {% for section_name, section_data in data.items() %}
                {% if section_data is mapping %}
                <div class="section">
                    <div class="section-title">{{ section_name }}</div>
                    {% for field_name, field_value in section_data.items() %}
                    <div class="form-group">
                        <label for="{{ field_name }}">{{ field_name }}</label>
                        {% if field_value|length > 50 %}
                        <textarea name="{{ field_name }}" id="{{ field_name }}">{{ field_value }}</textarea>
                        {% else %}
                        <input type="text" name="{{ field_name }}" id="{{ field_name }}" value="{{ field_value }}">
                        {% endif %}
                    </div>
                    {% endfor %}
                </div>
                {% endif %}
            {% endfor %}
            
            <button type="submit" class="save-btn">💾 Save Changes</button>
            <a href="/properties" class="back-btn">← Back to Properties</a>
        </form>
        {% else %}
        <p>❌ Could not load property data.</p>
        <a href="/properties" class="back-btn">← Back to Properties</a>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    return redirect(url_for('properties'))

@app.route('/properties')
def properties():
    property_files = get_property_files()
    properties = [f.replace('.xlsx', '') for f in property_files]
    return render_template_string(PROPERTY_LIST_TEMPLATE, properties=properties)

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
    print(f"🌐 Running on http://{PRODUCTION_HOST}:{PRODUCTION_PORT}")
    
    # Create required directories
    os.makedirs("backups", exist_ok=True)
    
    # Start the Flask app
    app.run(host=PRODUCTION_HOST, port=PRODUCTION_PORT, debug=False)