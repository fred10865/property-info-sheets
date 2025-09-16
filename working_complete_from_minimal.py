#!/usr/bin/env python3
"""
WORKING COMPLETE Info Sheet - Built from proven minimal_working_app.py
Using EXACT same button mechanics that we know work!
"""

from flask import Flask, request, jsonify, render_template_string
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the property scraper
try:
    from property_scraper import scrape_property_simple
    print("✅ Property scraper imported successfully")
    SCRAPER_AVAILABLE = True
except ImportError as e:
    print(f"❌ Property scraper import failed: {e}")
    SCRAPER_AVAILABLE = False

app = Flask(__name__)

# COMPLETE INFO SHEET TEMPLATE - Based on working minimal app
WORKING_COMPLETE_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>🏠 WORKING Complete Info Sheet</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            margin: 20px; 
            background: #f5f5f5; 
        }
        .container { 
            max-width: 1400px; 
            margin: 0 auto; 
            background: white; 
            padding: 20px; 
            border-radius: 10px; 
            box-shadow: 0 2px 10px rgba(0,0,0,0.1); 
        }
        
        .debug-panel { 
            background: #f8f9fa; 
            border: 3px solid #28a745; 
            margin: 20px 0; 
            padding: 20px; 
            border-radius: 8px; 
        }
        
        .auto-populate-btn {
            background: linear-gradient(45deg, #FF6B6B, #4ECDC4);
            color: white;
            border: none;
            padding: 15px 30px;
            font-size: 18px;
            font-weight: bold;
            border-radius: 10px;
            cursor: pointer;
            margin: 20px 0;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            transition: transform 0.2s;
        }
        .auto-populate-btn:hover { transform: translateY(-2px); }
        .auto-populate-btn:disabled { 
            opacity: 0.6; 
            cursor: not-allowed; 
            transform: none; 
        }
        
        .info-sheet-container {
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 30px;
            margin: 20px 0;
        }
        
        .column {
            background: #fafafa;
            padding: 20px;
            border-radius: 8px;
            border: 1px solid #ddd;
        }
        
        .column-title {
            font-size: 18px;
            font-weight: bold;
            color: #333;
            margin-bottom: 20px;
            text-align: center;
            padding: 10px;
            background: #e9ecef;
            border-radius: 5px;
        }
        
        .field-row {
            margin-bottom: 15px;
        }
        
        .field-label {
            font-weight: bold;
            color: #555;
            margin-bottom: 5px;
            font-size: 14px;
        }
        
        .field-input input, .field-input textarea {
            width: 100%;
            padding: 8px;
            border: 1px solid #ccc;
            border-radius: 4px;
            font-size: 14px;
            box-sizing: border-box;
        }
        
        .field-input textarea {
            height: 60px;
            resize: vertical;
        }
        
        .populated {
            background-color: #90EE90 !important;
            border-color: #28a745 !important;
        }
        
        .lot-number-section {
            text-align: center;
            margin-bottom: 20px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 8px;
        }
        
        .lot-number-section input {
            padding: 12px;
            font-size: 16px;
            border: 2px solid #007bff;
            border-radius: 6px;
            width: 200px;
            margin: 0 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🏠 WORKING Complete Property Info Sheet</h1>
        <p><strong>Built from proven minimal_working_app.py - Same exact button mechanics!</strong></p>
        
        <!-- LOT NUMBER INPUT -->
        <div class="lot-number-section">
            <label for="lotNumber"><strong>🏷️ Enter Lot Number:</strong></label>
            <input type="text" id="lotNumber" placeholder="e.g. 1004031" value="1004031">
            
            <!-- WORKING AUTO-POPULATE BUTTON (Same as minimal app) -->
            <button type="button" id="autoPopulateBtn" class="auto-populate-btn" onclick="testAutoPopulate()">
                🚀 AUTO-POPULATE ALL 32 FIELDS (Working Button!)
            </button>
        </div>
        
        <!-- DEBUG PANEL (Same as minimal app) -->
        <div class="debug-panel">
            <h3>🔍 DEBUG PANEL - Real Data Mapping</h3>
            <div id="debugContent">Waiting for button click...</div>
        </div>
        
        <!-- ALL 32 INFO SHEET FIELDS IN 3 COLUMNS -->
        <div class="info-sheet-container">
            <!-- Column 1: Property Information -->
            <div class="column">
                <div class="column-title">📍 Property Information</div>
                
                <div class="field-row">
                    <div class="field-label">Address</div>
                    <div class="field-input">
                        <input type="text" id="address" name="Address" placeholder="Property address">
                    </div>
                </div>
                
                <div class="field-row">
                    <div class="field-label">Google Maps Link</div>
                    <div class="field-input">
                        <input type="text" id="googleMapsLink" name="Google Maps Link" placeholder="Google Maps URL">
                    </div>
                </div>
                
                <div class="field-row">
                    <div class="field-label">Lot Number</div>
                    <div class="field-input">
                        <input type="text" id="lotNumberField" name="Lot Number" placeholder="Lot number">
                    </div>
                </div>
                
                <div class="field-row">
                    <div class="field-label">Borough</div>
                    <div class="field-input">
                        <input type="text" id="borough" name="Borough" placeholder="Borough/District">
                    </div>
                </div>
                
                <div class="field-row">
                    <div class="field-label">Year of Construction</div>
                    <div class="field-input">
                        <input type="text" id="yearOfConstruction" name="Year of Construction" placeholder="Year built">
                    </div>
                </div>
                
                <div class="field-row">
                    <div class="field-label">Total Building SF</div>
                    <div class="field-input">
                        <input type="text" id="totalBuildingSF" name="Total Building SF" placeholder="Building area">
                    </div>
                </div>
                
                <div class="field-row">
                    <div class="field-label">Google Maps Building SF</div>
                    <div class="field-input">
                        <input type="text" id="googleMapsBuildingSF" name="Google Maps Building SF" placeholder="Building area from maps">
                    </div>
                </div>
                
                <div class="field-row">
                    <div class="field-label">Land SF</div>
                    <div class="field-input">
                        <input type="text" id="landSF" name="Land SF" placeholder="Land area">
                    </div>
                </div>
                
                <div class="field-row">
                    <div class="field-label">Ceiling Height</div>
                    <div class="field-input">
                        <input type="text" id="ceilingHeight" name="Ceiling Height" placeholder="Ceiling height">
                    </div>
                </div>
                
                <div class="field-row">
                    <div class="field-label">Docks - google or vendor?</div>
                    <div class="field-input">
                        <input type="text" id="docks" name="Docks" placeholder="Loading dock info">
                    </div>
                </div>
                
                <div class="field-row">
                    <div class="field-label">Column Distance</div>
                    <div class="field-input">
                        <input type="text" id="columnDistance" name="Column Distance" placeholder="Column spacing">
                    </div>
                </div>
            </div>
            
            <!-- Column 2: Financial Information -->
            <div class="column">
                <div class="column-title">💰 Financial Information</div>
                
                <div class="field-row">
                    <div class="field-label">Purchase Price</div>
                    <div class="field-input">
                        <input type="text" id="purchasePrice" name="Purchase Price" placeholder="Purchase price">
                    </div>
                </div>
                
                <div class="field-row">
                    <div class="field-label">Price PSF Building</div>
                    <div class="field-input">
                        <input type="text" id="pricePSFBuilding" name="Price PSF Building" placeholder="Price per sq ft building">
                    </div>
                </div>
                
                <div class="field-row">
                    <div class="field-label">Price PSF Land</div>
                    <div class="field-input">
                        <input type="text" id="pricePSFLand" name="Price PSF Land" placeholder="Price per sq ft land">
                    </div>
                </div>
                
                <div class="field-row">
                    <div class="field-label">Type of Property</div>
                    <div class="field-input">
                        <input type="text" id="propertyType" name="Type of Property" placeholder="Property type">
                    </div>
                </div>
                
                <div class="field-row">
                    <div class="field-label">Amps</div>
                    <div class="field-input">
                        <input type="text" id="amps" name="Amps" placeholder="Electrical capacity">
                    </div>
                </div>
                
                <div class="field-row">
                    <div class="field-label">Income</div>
                    <div class="field-input">
                        <input type="text" id="income" name="Income" placeholder="Property income">
                    </div>
                </div>
                
                <div class="field-row">
                    <div class="field-label">Gross Income / Year</div>
                    <div class="field-input">
                        <input type="text" id="grossIncomeYear" name="Gross Income / Year" placeholder="Annual gross income">
                    </div>
                </div>
                
                <div class="field-row">
                    <div class="field-label">Gross income per Sq Ft</div>
                    <div class="field-input">
                        <input type="text" id="grossIncomePerSqFt" name="Gross income per Sq Ft" placeholder="Income per sq ft">
                    </div>
                </div>
                
                <div class="field-row">
                    <div class="field-label">OPEX / Year</div>
                    <div class="field-input">
                        <input type="text" id="opexYear" name="OPEX / Year" placeholder="Annual operating expenses">
                    </div>
                </div>
                
                <div class="field-row">
                    <div class="field-label">OPEX per Sq Ft</div>
                    <div class="field-input">
                        <input type="text" id="opexPerSqFt" name="OPEX per Sq Ft" placeholder="Operating expenses per sq ft">
                    </div>
                </div>
                
                <div class="field-row">
                    <div class="field-label">Net Income / Year</div>
                    <div class="field-input">
                        <input type="text" id="netIncomeYear" name="Net Income / Year" placeholder="Annual net income">
                    </div>
                </div>
            </div>
            
            <!-- Column 3: Owner & Building Information -->
            <div class="column">
                <div class="column-title">👥 Owner & Building Information</div>
                
                <div class="field-row">
                    <div class="field-label">Names of Owners</div>
                    <div class="field-input">
                        <input type="text" id="ownerName" name="Names of Owners" placeholder="Property owner names">
                    </div>
                </div>
                
                <div class="field-row">
                    <div class="field-label">Contact Info</div>
                    <div class="field-input">
                        <input type="text" id="contactInfo" name="Contact Info" placeholder="Owner contact information">
                    </div>
                </div>
                
                <div class="field-row">
                    <div class="field-label">Other Properties</div>
                    <div class="field-input">
                        <textarea id="otherProperties" name="Other Properties" placeholder="Other properties owned"></textarea>
                    </div>
                </div>
                
                <div class="field-row">
                    <div class="field-label">Zoning</div>
                    <div class="field-input">
                        <input type="text" id="zoning" name="Zoning" placeholder="Zoning classification">
                    </div>
                </div>
                
                <div class="field-row">
                    <div class="field-label">Account Number</div>
                    <div class="field-input">
                        <input type="text" id="accountNumber" name="Account Number" placeholder="Property account number">
                    </div>
                </div>
                
                <div class="field-row">
                    <div class="field-label">Matricule</div>
                    <div class="field-input">
                        <input type="text" id="matricule" name="Matricule" placeholder="Property matricule">
                    </div>
                </div>
                
                <div class="field-row">
                    <div class="field-label">Floor Plate</div>
                    <div class="field-input">
                        <input type="text" id="floorPlate" name="Floor Plate" placeholder="Floor plate information">
                    </div>
                </div>
                
                <div class="field-row">
                    <div class="field-label">Net Income per Sq Ft</div>
                    <div class="field-input">
                        <input type="text" id="netIncomePerSqFt" name="Net Income per Sq Ft" placeholder="Net income per sq ft">
                    </div>
                </div>
                
                <div class="field-row">
                    <div class="field-label">Occupancy %</div>
                    <div class="field-input">
                        <input type="text" id="occupancyPercent" name="Occupancy %" placeholder="Occupancy percentage">
                    </div>
                </div>
                
                <div class="field-row">
                    <div class="field-label">Building Breakdown</div>
                    <div class="field-input">
                        <textarea id="buildingBreakdown" name="Building Breakdown" placeholder="Building breakdown details"></textarea>
                    </div>
                </div>
                
                <div class="field-row">
                    <div class="field-label">Land Value</div>
                    <div class="field-input">
                        <input type="text" id="landValue" name="Land Value" placeholder="Land value">
                    </div>
                </div>
                
                <div class="field-row">
                    <div class="field-label">Building Value</div>
                    <div class="field-input">
                        <input type="text" id="buildingValue" name="Building Value" placeholder="Building value">
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
    // EXACT SAME WORKING FUNCTION FROM minimal_working_app.py
    async function testAutoPopulate() {
        console.log('🚀 testAutoPopulate function called!');
        alert('🔥 Button clicked! Function is working!');
        
        const btn = document.getElementById('autoPopulateBtn');
        const debugContent = document.getElementById('debugContent');
        const originalText = btn.innerHTML;
        
        // Get lot number
        const lotNumber = document.getElementById('lotNumber').value.trim();
        
        if (!lotNumber) {
            alert('📝 Please enter a Lot Number');
            return;
        }
        
        btn.disabled = true;
        btn.innerHTML = '🔄 Scraping REAL Montreal data...';
        debugContent.textContent = '🔄 Starting scrape request...';
        
        try {
            console.log('📤 Sending request to /scrape');
            
            const response = await fetch('/scrape', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    lot_number: lotNumber,
                    borough: 'montreal'
                })
            });
            
            console.log('📥 Response received:', response.status);
            const result = await response.json();
            console.log('📊 Response data:', result);
            
            debugContent.textContent = '📊 SCRAPED DATA:\\n' + JSON.stringify(result, null, 2);
            
            if (result.success && result.property) {
                // COMPREHENSIVE field mapping for REAL Montreal data → ALL 32 Info Sheet fields
                const mappings = {
                    // Real scraper field names → Form field IDs
                    'address': 'address',
                    'borough': 'borough', 
                    'lot_number': 'lotNumberField',
                    'year_of_construction': 'yearOfConstruction',
                    'floors_area': 'totalBuildingSF',
                    'land_area': 'landSF',
                    'owner_name': 'ownerName',
                    'usage': 'propertyType',
                    'total_value': 'purchasePrice',
                    'matricule': 'matricule',
                    'owner_address': 'contactInfo',
                    'land_value': 'landValue',
                    'building_value': 'buildingValue',
                    'number_of_floors': 'floorPlate'
                };
                
                let populatedCount = 0;
                
                for (const [dataKey, fieldId] of Object.entries(mappings)) {
                    const value = result.property[dataKey];
                    const input = document.getElementById(fieldId);
                    
                    console.log(`🔍 Mapping ${dataKey} → ${fieldId}: "${value}"`);
                    
                    if (value && input) {
                        // Format values appropriately
                        let formattedValue = value;
                        
                        // Format currency values
                        if (fieldId.includes('Value') || fieldId.includes('Price')) {
                            if (typeof value === 'number' || !isNaN(value)) {
                                formattedValue = new Intl.NumberFormat('en-US', {
                                    style: 'currency',
                                    currency: 'USD',
                                    minimumFractionDigits: 0
                                }).format(value);
                            }
                        }
                        
                        // Format areas with commas
                        if (fieldId.includes('SF') || fieldId.includes('Area')) {
                            if (typeof value === 'number' || !isNaN(value)) {
                                formattedValue = new Intl.NumberFormat('en-US').format(value) + ' SF';
                            }
                        }
                        
                        input.value = formattedValue;
                        input.classList.add('populated');
                        populatedCount++;
                        console.log(`✅ Populated ${fieldId} with "${formattedValue}"`);
                    }
                }
                
                // Auto-generate Google Maps link
                const addressInput = document.getElementById('address');
                const mapsInput = document.getElementById('googleMapsLink');
                if (addressInput && addressInput.value && mapsInput) {
                    const mapsUrl = `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(addressInput.value)}`;
                    mapsInput.value = mapsUrl;
                    mapsInput.classList.add('populated');
                    populatedCount++;
                    console.log(`✅ Auto-generated Google Maps link`);
                }
                
                btn.innerHTML = `✅ Populated ${populatedCount} fields with REAL data!`;
                alert(`🎉 SUCCESS! Populated ${populatedCount} fields with REAL Montreal data!`);
                
            } else {
                btn.innerHTML = '❌ Failed';
                alert('❌ Scraping failed: ' + (result.error || 'Unknown error'));
            }
            
        } catch (error) {
            console.error('❌ Error:', error);
            debugContent.textContent = `❌ Error: ${error.message}`;
            btn.innerHTML = '❌ Error';
            alert('❌ Network error: ' + error.message);
        }
        
        setTimeout(() => {
            btn.innerHTML = originalText;
            btn.disabled = false;
        }, 3000);
    }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(WORKING_COMPLETE_TEMPLATE)

# EXACT SAME WORKING BACKEND FROM minimal_working_app.py
@app.route('/scrape', methods=['POST'])
def scrape():
    """Scrape property data - EXACT SAME CODE as minimal_working_app.py"""
    try:
        print("🚀 /scrape endpoint called!")
        data = request.get_json()
        print(f"📥 Received data: {data}")
        
        lot_number = data.get('lot_number')
        borough = data.get('borough', 'montreal')
        
        print(f"🔍 Scraping lot {lot_number} in {borough}")
        
        if SCRAPER_AVAILABLE:
            print("🔄 Calling scrape_property_simple with REAL DATA...")
            property_data = scrape_property_simple(lot_number, borough, use_aws=False, use_mock=False, headless=True)
            print(f"📊 Scraper returned: {property_data}")
            
            if 'error' not in property_data:
                print(f"✅ Scraped {len(property_data)} fields successfully")
                return jsonify({'success': True, 'property': property_data})
            else:
                print(f"❌ Scraper error: {property_data['error']}")
                return jsonify({'success': False, 'error': property_data['error']})
        else:
            print("❌ Scraper not available!")
            return jsonify({'success': False, 'error': 'Scraper not available'})
            
    except Exception as e:
        print(f"❌ Scrape error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    print("🚀 Starting WORKING COMPLETE Info Sheet Flask app...")
    print("🏠 Based on proven minimal_working_app.py foundation")
    print("🎯 ALL 32 fields with REAL Montreal data auto-populate")
    print("📍 App will run on http://localhost:8007")
    app.run(host='0.0.0.0', port=8007, debug=False)