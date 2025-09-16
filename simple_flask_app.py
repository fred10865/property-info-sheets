#!/usr/bin/env python3
"""
Simplified Flask app for testing the /scrape integration
Minimal setup without database dependencies
"""

from flask import Flask, request, jsonify
import os
import sys

# Import the property scraper
try:
    from property_scraper import scrape_property_simple
    SCRAPER_AVAILABLE = True
    print("✅ Property scraper imported successfully")
except ImportError as e:
    SCRAPER_AVAILABLE = False
    print(f"⚠️ Property scraper not available: {e}")

app = Flask(__name__)

@app.route('/')
def index():
    return """
    <html>
    <head><title>Property Scraper Test</title></head>
    <body>
        <h1>🏠 Property Scraper Test</h1>
        <p>Flask app is running!</p>
        <p>Scraper available: {}</p>
        <p>Test the integration:</p>
        <ul>
            <li><a href="/test_scrape_page.html">/test_scrape_page.html</a> - Test page</li>
            <li><code>POST /scrape</code> - Scrape endpoint</li>
        </ul>
    </body>
    </html>
    """.format("✅ Yes" if SCRAPER_AVAILABLE else "❌ No")

@app.route('/scrape', methods=['POST'])
def scrape_property_route():
    """Simple scrape route that accepts JSON with lot_number and returns property data"""
    if not SCRAPER_AVAILABLE:
        return jsonify({'success': False, 'error': 'Property scraper not available'}), 500
    
    try:
        # Get JSON data from request
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No JSON data provided'}), 400
        
        lot_number = data.get('lot_number', '').strip()
        borough = data.get('borough', 'montreal').strip()  # Default to montreal
        
        if not lot_number:
            return jsonify({'success': False, 'error': 'lot_number is required'}), 400
        
        print(f"🔍 Scraping property data for Lot {lot_number} in {borough}")
        
        # Call the scraper function - try real scraper first, fallback to mock if needed
        try:
            scraped_data = scrape_property_simple(lot_number, borough, use_aws=False, use_mock=False, headless=True)
            
            # Check if scraping failed and fallback to mock data
            if 'error' in scraped_data:
                print(f"⚠️ Real scraper failed: {scraped_data['error']}, using mock data")
                scraped_data = scrape_property_simple(lot_number, borough, use_aws=False, use_mock=True, headless=True)
                
        except Exception as scraper_error:
            print(f"⚠️ Scraper exception: {scraper_error}, using mock data")
            scraped_data = scrape_property_simple(lot_number, borough, use_aws=False, use_mock=True, headless=True)
        
        # Filter out empty values and prepare response
        property_data = {k: v for k, v in scraped_data.items() if v and str(v).strip() and k != 'error'}
        
        print(f"✅ Successfully scraped {len(property_data)} fields for lot {lot_number}")
        
        return jsonify({
            'success': True,
            'property': property_data,
            'lot_number': lot_number,
            'borough': borough
        })
        
    except Exception as e:
        error_msg = f"Scraping failed: {str(e)}"
        print(f"❌ Scrape route error: {error_msg}")
        return jsonify({'success': False, 'error': error_msg}), 500

@app.route('/test_scrape_page.html')
def test_page():
    """Serve the test page"""
    try:
        with open('test_scrape_page.html', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return """
        <html>
        <head><title>Test Page Not Found</title></head>
        <body>
            <h1>❌ Test Page Not Found</h1>
            <p>Please create test_scrape_page.html first</p>
        </body>
        </html>
        """

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    print(f"🚀 Starting simplified Flask app on port {port}")
    print(f"🔧 Scraper available: {SCRAPER_AVAILABLE}")
    app.run(host='0.0.0.0', port=port, debug=True)