#!/usr/bin/env python3
"""
Test the new /scrape route integration
Tests both the Flask route and the headless scraper functionality
"""

import requests
import json
import time

def test_scrape_route():
    """Test the new /scrape route"""
    
    print("🧪 TESTING NEW /SCRAPE ROUTE INTEGRATION")
    print("=" * 60)
    
    # Test data
    test_lot = "1004031"  # Same lot we tested before
    flask_url = "http://localhost:8000"  # Assuming Flask runs on port 8000
    
    # Test data to send
    test_data = {
        "lot_number": test_lot,
        "borough": "montreal"
    }
    
    print(f"🔍 Testing with lot number: {test_lot}")
    print(f"🌐 Flask URL: {flask_url}")
    print(f"📤 Sending data: {json.dumps(test_data, indent=2)}")
    
    try:
        # Make POST request to /scrape
        print("\n📡 Making POST request to /scrape...")
        response = requests.post(
            f"{flask_url}/scrape",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=60  # Give it time to scrape
        )
        
        print(f"📊 Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCESS! Route responded correctly")
            print(f"📋 Response structure:")
            print(f"   - success: {result.get('success')}")
            print(f"   - lot_number: {result.get('lot_number')}")
            print(f"   - borough: {result.get('borough')}")
            print(f"   - property data fields: {len(result.get('property', {}))}")
            
            if result.get('success'):
                print("\n🎉 PROPERTY DATA EXTRACTED:")
                property_data = result.get('property', {})
                for key, value in property_data.items():
                    if value and str(value).strip():
                        print(f"   📝 {key}: {value}")
                        
                print(f"\n✅ Successfully extracted {len(property_data)} property fields")
                print("🚀 Flask auto-populate integration is working!")
                        
            else:
                print(f"❌ Scraping failed: {result.get('error')}")
                
        else:
            print(f"❌ HTTP Error {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data.get('error', 'Unknown error')}")
            except:
                print(f"   Raw response: {response.text}")
                
    except requests.exceptions.ConnectionError:
        print("❌ CONNECTION ERROR: Flask app is not running")
        print("💡 Start Flask first with: python flask_app.py")
        
    except requests.exceptions.Timeout:
        print("⏰ TIMEOUT: Scraping took too long (>60 seconds)")
        print("💡 This might be normal for real scraping - try again")
        
    except Exception as e:
        print(f"❌ UNEXPECTED ERROR: {e}")

def test_headless_scraper():
    """Test the headless scraper directly"""
    
    print("\n🧪 TESTING HEADLESS SCRAPER DIRECTLY")
    print("=" * 60)
    
    try:
        from property_scraper import scrape_property_simple
        
        test_lot = "1004031"
        print(f"🔍 Testing headless scraper with lot: {test_lot}")
        
        # Test with headless=True (for Flask)
        print("🖥️ Testing with headless=True (Flask mode)...")
        result = scrape_property_simple(test_lot, "montreal", use_aws=False, use_mock=False, headless=True)
        
        print(f"📋 Headless scraper result type: {type(result)}")
        
        if 'error' in result:
            print(f"⚠️ Headless scraper returned error: {result['error']}")
            print("💡 This is expected if botasaurus has import issues")
            
            # Test mock data
            print("\n🧪 Testing mock data fallback...")
            mock_result = scrape_property_simple(test_lot, "montreal", use_aws=False, use_mock=True, headless=True)
            print(f"📋 Mock result: {len(mock_result)} fields")
            for key, value in mock_result.items():
                if value and str(value).strip():
                    print(f"   📝 {key}: {value}")
                    
        else:
            print("✅ Headless scraper working!")
            for key, value in result.items():
                if value and str(value).strip() and key != 'error':
                    print(f"   📝 {key}: {value}")
                    
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Check that property_scraper.py is available")
        
    except Exception as e:
        print(f"❌ Scraper error: {e}")

if __name__ == "__main__":
    print("🚀 FLASK SCRAPE INTEGRATION TESTS")
    print("=" * 60)
    
    # Test 1: Test headless scraper directly
    test_headless_scraper()
    
    # Test 2: Test Flask route
    test_scrape_route()
    
    print("\n" + "=" * 60)
    print("🏁 INTEGRATION TESTS COMPLETE")
    print("=" * 60)