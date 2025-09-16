#!/usr/bin/env python3
"""
Quebec Property Scraper API
Extracts property data from cadastral lot number and municipality
Optimized for Quebec evaluation websites and business registry integration

📖 COMPLETE DOCUMENTATION: See MASTER_QUEBEC_SCRAPER_RESEARCH.md
   - Implementation patterns for all 7 scraper types
   - Enhanced Montreal strategies with Tavily research
   - AWS integration, error handling, and maintenance guides
   - Emergency debugging and troubleshooting procedures

🏙️ MONTREAL BREAKTHROUGH: NO VPN REQUIRED!
   - Montreal scraper works perfectly without AWS VPN rotation
   - Anti-detection requirements: French Canadian locale, human-like behavior
   - Successfully extracts "Aire d'étage" and navigation: search → results → detail
   - Use direct connection for optimal performance

🚨 BEFORE USING: Read the master documentation for setup and usage patterns
"""

import os
import sys
import time
import subprocess
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class QuebecPropertyScraperAPI:
    """Quebec Property Data Extraction API"""
    
    def __init__(self):
        # AWS EC2 Instances for VPN rotation
        # Canadian instances in ca-central-1 (Montreal) for optimal Quebec access
        self.aws_instances = {
            # Canadian servers (ca-central-1 - Montreal)
            1: 'i-0b8f9025cf8a0040c',  # Canada Central - IP: 15.222.11.196
            2: 'i-091da18f939f0ce1e',  # Canada Central - IP: 35.182.253.30
            3: 'i-0b60617fddaa1f14c',  # Canada Central - IP: 16.52.152.239
            # US servers (backup - us-east-1c)
            4: 'i-0b6f0fc9180ed3ddf',  # US East 1c - IP: 3.93.52.90
            5: 'i-09acfa3aa12dffec4',  # US East 1c - IP: 35.175.197.175
            6: 'i-0d7b894bbf723df3a',  # US East 1c - IP: 54.91.35.211
            7: 'i-07c17f3ac8c56f995',  # US East 1c - IP: 34.204.45.83
            8: 'i-07a2197f386183392',  # US East 1c - IP: 13.218.101.130
        }
        
        # AWS regions for each instance
        self.aws_regions = {
            1: 'ca-central-1',  # Canadian instances
            2: 'ca-central-1',
            3: 'ca-central-1',
            4: 'us-east-1',     # US instances
            5: 'us-east-1',
            6: 'us-east-1',
            7: 'us-east-1',
            8: 'us-east-1',
        }
        
        # Quebec Municipality Evaluation URLs (from FinalInfomationAboutAreasPDF.csv)
        # Municipality-specific VPN requirements
        # IMPORTANT: Montreal works WITHOUT VPN - direct connection is successful
        # Other Quebec municipalities may require AWS VPN rotation for rate limiting
        self.vpn_exempt_municipalities = [
            'montreal',
            'montreal.ca'
        ]
        
        self.municipality_urls = {
            'laval': 'https://e-services.acceo.com/immosoft/controller/ImmoNetPub/U4051/trouverParAdresse?init_mapping=&fourn_seq=173',
            'montreal': 'https://montreal.ca/role-evaluation-fonciere/lot-renove',
            'longueuil': 'https://servicesenligne.longueuil.quebec.ca/SIL/',
            'gatineau': 'https://role.gatineau.ca/rolfoncier/',
            'sherbrooke': 'https://www.ville.sherbrooke.qc.ca/services-municipaux/evaluation-fonciere/',
            'saguenay': 'https://saguenay.ca/services-aux-citoyens/evaluation-fonciere',
            'levis': 'https://www.ville.levis.qc.ca/citoyens/services-en-ligne/evaluation-municipale/',
            'quebec': 'https://www.ville.quebec.qc.ca/services/evaluation_fonciere/',
            'drummondville': 'https://e-services.acceo.com/immosoft/controller/ImmoNetPub/U4051/trouverParAdresse?init_mapping=&language=fr&fourn_seq=224',
            'saint-eustache': 'https://e-services.acceo.com/immosoft/controller/ImmoNetPub/U4051/trouverParAdresse?init_mapping=&language=fr&fourn_seq=431',
            'vaudreuil-dorion': 'https://e-services.acceo.com/immosoft/controller/ImmoNetPub/U4051/trouverParAdresse?init_mapping=&language=fr&fourn_seq=523',
            'mascouche': 'https://e-services.acceo.com/immosoft/controller/ImmoNetPub/U4051/trouverParAdresse?init_mapping=&language=fr&fourn_seq=301',
            'bois-des-fillion': 'https://e-services.acceo.com/immosoft/controller/ImmoNetPub/U4051/trouverParAdresse?init_mapping=&language=fr&fourn_seq=195',
            # Fallback to generic Quebec evaluation portal
            'generic': 'https://www.donneesquebec.ca/recherche/fr/dataset/evaluation-fonciere'
        }
        
    def get_aws_instance_ip(self, instance_id, server_num=1):
        """Get public IP of AWS EC2 instance"""
        try:
            # Try AWS CLI with full path first
            aws_paths = [
                "C:\\Program Files\\Amazon\\AWSCLIV2\\aws.exe",
                "aws"  # Fallback to PATH
            ]
            
            aws_cmd = None
            for path in aws_paths:
                try:
                    result = subprocess.run([path, "--version"], capture_output=True, text=True)
                    if result.returncode == 0:
                        aws_cmd = path
                        break
                except FileNotFoundError:
                    continue
            
            if not aws_cmd:
                print(f"⚠️ AWS CLI not found. Install with: winget install Amazon.AWSCLI")
                return None
            
            # Get the region for this server
            region = self.aws_regions.get(server_num, 'us-east-1')
            
            result = subprocess.run([
                aws_cmd, "ec2", "describe-instances", 
                "--region", region,
                "--instance-ids", instance_id,
                "--query", "Reservations[*].Instances[*].PublicIpAddress",
                "--output", "text"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                ip = result.stdout.strip()
                if ip and ip != "None":
                    return ip
                else:
                    print(f"⚠️ No public IP found for instance {instance_id}")
                    return None
            else:
                print(f"⚠️ AWS CLI error: {result.stderr}")
                return None
        except Exception as e:
            print(f"Error getting instance IP: {e}")
            return None
    
    def start_aws_instance(self, instance_id, server_num=1):
        """Start AWS EC2 instance"""
        try:
            # Try AWS CLI with full path first
            aws_paths = [
                "C:\\Program Files\\Amazon\\AWSCLIV2\\aws.exe",
                "aws"  # Fallback to PATH
            ]
            
            aws_cmd = None
            for path in aws_paths:
                try:
                    result = subprocess.run([path, "--version"], capture_output=True, text=True)
                    if result.returncode == 0:
                        aws_cmd = path
                        break
                except FileNotFoundError:
                    continue
            
            if not aws_cmd:
                print(f"⚠️ AWS CLI not found")
                return False
            
            # Get the region for this server
            region = self.aws_regions.get(server_num, 'us-east-1')
                
            subprocess.run([
                aws_cmd, "ec2", "start-instances", 
                "--region", region,
                "--instance-ids", instance_id
            ], capture_output=True)
            time.sleep(90)  # Wait for instance to boot
            return True
        except Exception as e:
            print(f"Error starting instance: {e}")
            return False
    
    def create_driver(self, use_aws_proxy=False, server_num=1):
        """Create optimized Chrome driver with enhanced anti-detection"""
        options = Options()
        # options.add_argument('--headless')  # Commented out so you can see the browser
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        options.add_argument('--lang=fr-CA')  # French Canadian for Quebec sites
        # Enhanced anti-detection measures
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        if use_aws_proxy and server_num in self.aws_instances:
            instance_id = self.aws_instances[server_num]
            self.start_aws_instance(instance_id, server_num)
            proxy_ip = self.get_aws_instance_ip(instance_id, server_num)
            if proxy_ip:
                options.add_argument(f'--proxy-server={proxy_ip}:8080')
        
        try:
            driver = webdriver.Chrome(options=options)
            driver.set_page_load_timeout(30)
            # Additional anti-detection JavaScript execution
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            return driver
        except Exception as e:
            print(f"Error creating driver: {e}")
            return None
    
    def scrape_property_data(self, lot_number, municipality, use_aws=True):
        """
        Main function to scrape Quebec property data
        Returns structured data for property info sheet
        """
        print(f"🔍 Scraping data for Lot {lot_number} in {municipality}")
        
        # Check if municipality is VPN-exempt (e.g., Montreal works without VPN)
        municipality_lower = municipality.lower()
        needs_vpn = not any(exempt in municipality_lower for exempt in self.vpn_exempt_municipalities)
        
        if not needs_vpn:
            print(f"🏙️ {municipality} detected - running directly without AWS VPN (known to work)")
            use_aws = False
            max_servers = 1  # Only try once for VPN-exempt municipalities
        elif 'montreal' in municipality_lower:
            print("🏙️ Montreal detected - running directly without AWS proxy")
            use_aws = False
            max_servers = 1  # Only try once for Montreal
        else:
            # Try multiple AWS servers if one gets rate limited (for other cities like Laval)
            max_servers = max(self.aws_instances.keys()) if self.aws_instances else 5
        
        for server_num in range(1, max_servers + 1):  # Try all configured servers
            if 'montreal' in municipality.lower():
                print(f"🔧 Attempting Montreal scrape directly (no AWS)")
            else:
                print(f"🔧 Attempting with AWS server {server_num}")
            
            driver = self.create_driver(use_aws_proxy=use_aws, server_num=server_num)
            if not driver:
                print(f"❌ Failed to create driver with server {server_num}")
                continue
            
            try:
                # Primary scraping from Quebec property evaluation records
                property_data = self._scrape_quebec_evaluation(driver, lot_number, municipality, server_num)
                
                # Check if we got rate limited
                if property_data.get('rate_limited'):
                    print(f"⚠️ Server {server_num} is rate limited, trying next server...")
                    driver.quit()
                    continue
                
                # Secondary scraping for business/owner information if owner name found
                if property_data.get('owner_name'):
                    business_data = self._scrape_quebec_business_registry(driver, property_data['owner_name'])
                    property_data.update(business_data)
                
                print(f"✅ Successfully scraped with server {server_num}")
                return property_data
                
            except Exception as e:
                print(f"❌ Scraping error with server {server_num}: {e}")
            finally:
                driver.quit()
        
        # If all servers failed
        print("❌ All AWS servers failed or are rate limited")
        return {"error": "All servers rate limited or failed"}
    
    def _scrape_quebec_evaluation(self, driver, lot_number, municipality, server_num):
        """Scrape Quebec municipal evaluation sites for property data"""
        try:
            print(f"🔍 Accessing Quebec evaluation site for {municipality} (Server {server_num})")
            
            # Normalize municipality name
            municipality_key = municipality.lower().replace('-', '').replace(' ', '')
            
            # Find matching URL
            eval_url = None
            for key, url in self.municipality_urls.items():
                if municipality_key in key or key in municipality_key:
                    eval_url = url
                    break
            
            if not eval_url:
                # Default to Laval if municipality not found
                eval_url = self.municipality_urls['laval']
                print(f"⚠️ Municipality '{municipality}' not found, using Laval as default")
            
            driver.get(eval_url)
            time.sleep(3)
            
            # DEBUG: Print page title and URL
            print(f"🌐 Page loaded - Title: {driver.title}")
            print(f"🌐 Current URL: {driver.current_url}")
            
            # DEBUG: Print page content snippet
            print(f"📄 Page content preview (first 800 chars):")
            print("=" * 70)
            print(driver.page_source[:800])
            print("=" * 70)
            
            # Define rate limiting indicators
            rate_limit_indicators = [
                "l'outil gratuit est destiné à la consultation personnelle citoyenne",
                "limite de consultations gratuites",
                "accès illimité au rôle d'évaluation",
                "portail de données immobilières",
                "too many requests",
                "rate limit",
                "access denied",
                "blocked"
            ]
            
            # Check for rate limiting message first
            page_source = driver.page_source.lower()
            
            # Look for specific Quebec evaluation content
            if 'acceo' in page_source or 'évaluation' in page_source or 'propriété' in page_source:
                print("✅ Quebec evaluation system detected")
            else:
                print("⚠️ Quebec evaluation system NOT detected - might be blocked or different page")
            
            if any(indicator in page_source for indicator in rate_limit_indicators):
                print(f"⚠️ Rate limiting detected on server {server_num}")
                print(f"🔍 Rate limit message found in page")
                # DEBUG: Show which specific indicator was found
                for indicator in rate_limit_indicators:
                    if indicator in page_source:
                        print(f"🔍 Found rate limit indicator: '{indicator}'")
                        break
                return {'rate_limited': True, 'lot_number': lot_number, 'municipality': municipality}
            
            print(f"✅ No rate limiting detected on server {server_num}")
            
            # Montreal has a different system - handle it separately (NO VPN NEEDED)
            if 'montreal' in municipality.lower() or 'montreal.ca' in eval_url:
                print("🏙️ Calling Montreal-specific scraper (VPN-exempt)")
                return self._scrape_montreal_evaluation(driver, lot_number, municipality, server_num)
            
            # For Laval and similar sites, click "Par cadastre" button first
            if 'laval' in municipality.lower() or 'acceo.com' in eval_url:
                try:
                    # Look for "Par cadastre" button or link
                    cadastre_button_selectors = [
                        'a:contains("Par cadastre")',
                        'button:contains("Par cadastre")',
                        'a[href*="cadastre"]',
                        'button[onclick*="cadastre"]',
                        '.cadastre-btn',
                        '#par-cadastre',
                        'a:contains("Cadastre")',
                        'button:contains("Cadastre")'
                    ]
                    
                    cadastre_button = None
                    for selector in cadastre_button_selectors:
                        try:
                            if ':contains(' in selector:
                                # Handle contains selector
                                text = selector.split(':contains("')[1].split('")')[0]
                                cadastre_button = driver.find_element(By.XPATH, f"//a[contains(text(), '{text}') or contains(text(), '{text.lower()}')]")
                            else:
                                cadastre_button = driver.find_element(By.CSS_SELECTOR, selector)
                            print(f"✅ Found 'Par cadastre' button with selector: {selector}")
                            break
                        except:
                            continue
                    
                    if cadastre_button:
                        cadastre_button.click()
                        print("✅ Clicked 'Par cadastre' button")
                        time.sleep(5)  # Increased wait time for dynamic content
                        
                        # Check if URL changed or page reloaded
                        new_url = driver.current_url
                        print(f"🔍 URL after clicking button: {new_url}")
                        
                        # Wait for dynamic content to load
                        try:
                            WebDriverWait(driver, 15).until(
                                lambda driver: len(driver.find_elements(By.CSS_SELECTOR, 'input[type="text"]')) > 0 or
                                              driver.find_element(By.ID, "NoCadastre") or
                                              'cadastre' in driver.page_source.lower()
                            )
                            print("✅ Page content updated after button click")
                        except:
                            print("⚠️ Timeout waiting for dynamic content")
                            
                            # Check for iframes
                            iframes = driver.find_elements(By.TAG_NAME, "iframe")
                            print(f"🔍 Found {len(iframes)} iframes on page")
                            
                            if iframes:
                                # Try switching to the first iframe
                                try:
                                    driver.switch_to.frame(iframes[0])
                                    print("✅ Switched to iframe")
                                    time.sleep(3)
                                except Exception as e:
                                    print(f"❌ Error switching to iframe: {e}")
                        
                        # Additional wait for page stabilization  
                        time.sleep(3)
                        
                        # Check for rate limiting after clicking button
                        page_source = driver.page_source.lower()
                        if any(indicator in page_source for indicator in rate_limit_indicators):
                            print(f"⚠️ Rate limiting detected after button click on server {server_num}")
                            return {'rate_limited': True, 'lot_number': lot_number, 'municipality': municipality}
                            
                    else:
                        print("⚠️ Could not find 'Par cadastre' button, proceeding with current page")
                        
                except Exception as e:
                    print(f"⚠️ Error clicking 'Par cadastre' button: {e}")
            
            # Quebec Acceo system selectors (used by most municipalities)
            lot_selectors = [
                '#NoCadastre',  # Main cadastre field for Acceo system
                'input[name="NoCadastre"]',
                'input[id="NoCadastre"]',
                '#lot',
                '#numero_lot',
                '#numero-lot',
                '#numero_cadastre',
                '#numero-cadastre',
                'input[name="lot"]',
                'input[name="numero_lot"]',
                'input[name="cadastre"]',
                'input[placeholder*="cadastre"]',
                'input[placeholder*="lot"]',
                'input[placeholder*="numéro"]',
                'input[id*="cadastre"]',
                'input[id*="lot"]',
                'input[id*="numero"]',
                '[name*="search"]',
                '[name*="recherche"]',
                'input[type="text"]:first-of-type',
                'input[type="search"]'
            ]
            
            # Try to find and fill lot number input
            lot_input = None
            
            # Debug: Show all input fields on the page
            try:
                all_inputs = driver.find_elements(By.TAG_NAME, "input")
                print(f"🔍 Found {len(all_inputs)} input fields on page")
                
                # Show all buttons too
                all_buttons = driver.find_elements(By.TAG_NAME, "button")
                print(f"🔍 Found {len(all_buttons)} button elements on page")
                
                # Show all links
                all_links = driver.find_elements(By.TAG_NAME, "a")
                print(f"🔍 Found {len(all_links)} link elements on page")
                
                text_inputs = [inp for inp in all_inputs if inp.get_attribute('type') in ['text', 'search', None]]
                print(f"🔍 Found {len(text_inputs)} text input fields")
                
                print("📝 All input fields details:")
                for i, inp in enumerate(all_inputs[:20]):  # Show more inputs
                    try:
                        input_type = inp.get_attribute('type') or 'text'
                        input_id = inp.get_attribute('id') or ''
                        input_name = inp.get_attribute('name') or ''
                        input_placeholder = inp.get_attribute('placeholder') or ''
                        input_class = inp.get_attribute('class') or ''
                        is_visible = inp.is_displayed()
                        print(f"  Input {i}: id='{input_id}', name='{input_name}', type='{input_type}', placeholder='{input_placeholder}', class='{input_class}', visible={is_visible}")
                    except Exception as e:
                        print(f"  Input {i}: Error getting attributes - {e}")
                
                print("🔗 First 10 buttons:")
                for i, btn in enumerate(all_buttons[:10]):
                    try:
                        btn_text = btn.text.strip()
                        btn_id = btn.get_attribute('id') or ''
                        btn_class = btn.get_attribute('class') or ''
                        is_visible = btn.is_displayed()
                        print(f"  Button {i}: text='{btn_text}', id='{btn_id}', class='{btn_class}', visible={is_visible}")
                    except Exception as e:
                        print(f"  Button {i}: Error getting attributes - {e}")
                
                print("🔗 First 10 links:")
                for i, link in enumerate(all_links[:10]):
                    try:
                        link_text = link.text.strip()
                        link_href = link.get_attribute('href') or ''
                        link_id = link.get_attribute('id') or ''
                        is_visible = link.is_displayed()
                        print(f"  Link {i}: text='{link_text}', href='{link_href}', id='{link_id}', visible={is_visible}")
                    except Exception as e:
                        print(f"  Link {i}: Error getting attributes - {e}")
                        
            except Exception as e:
                print(f"⚠️ Error analyzing page elements: {e}")
                
                # Also check for form elements and buttons
                all_forms = driver.find_elements(By.TAG_NAME, "form")
                print(f"🔍 Found {len(all_forms)} forms on page")
                
                all_buttons = driver.find_elements(By.TAG_NAME, "button")
                print(f"🔍 Found {len(all_buttons)} buttons on page")
                for i, btn in enumerate(all_buttons[:5]):  # Show first 5
                    try:
                        print(f"  Button {i}: id='{btn.get_attribute('id')}', class='{btn.get_attribute('class')}', text='{btn.text}'")
                    except:
                        pass
                        
                # Check for selects and textareas too
                all_selects = driver.find_elements(By.TAG_NAME, "select")
                all_textareas = driver.find_elements(By.TAG_NAME, "textarea")
                print(f"🔍 Found {len(all_selects)} select fields and {len(all_textareas)} textareas")
                
            except:
                pass
            
            for selector in lot_selectors:
                try:
                    lot_input = driver.find_element(By.CSS_SELECTOR, selector)
                    print(f"✅ Found lot input with selector: {selector}")
                    break
                except:
                    continue
            
            if lot_input:
                lot_input.clear()
                lot_input.send_keys(str(lot_number))
                
                # Check for report type radio button (from original scraper)
                try:
                    report_type = driver.find_element(By.ID, "ty_rapport_eval")
                    if not report_type.is_selected():
                        report_type.click()
                        print("✅ Selected evaluation report type")
                except Exception as e:
                    print(f"ℹ️ No report type selection needed: {e}")
                
                # Submit the form (Acceo system uses specific buttons)
                submit_selectors = [
                    '#btnSearch',  # Standard Acceo submit button
                    'button[id="btnSearch"]',
                    'input[id="btnSearch"]',
                    'input[type="submit"]',
                    'button[type="submit"]',
                    '.btn-search',
                    '.rechercher',
                    '.search-btn',
                    'button:contains("Rechercher")',
                    'input[value*="Rechercher"]',
                    'input[value*="Search"]'
                ]
                
                for selector in submit_selectors:
                    try:
                        if ':contains(' in selector:
                            submit_btn = driver.find_element(By.XPATH, f"//button[contains(text(), 'Rechercher')]")
                        else:
                            submit_btn = driver.find_element(By.CSS_SELECTOR, selector)
                        submit_btn.click()
                        print(f"✅ Clicked submit with selector: {selector}")
                        break
                    except:
                        continue
                
                # Wait for results
                time.sleep(8)  # Increased wait time
                
                # Debug: Show page title and URL after submission
                print(f"🔍 Page after submission: {driver.title}")
                print(f"🔍 Current URL: {driver.current_url}")
                
                # Check if we're on a results page or if there are any data containers
                try:
                    page_text = driver.page_source.lower()
                    if any(term in page_text for term in ['propriétaire', 'adresse', 'évaluation', 'owner', 'address']):
                        print("✅ Found property data indicators on page")
                    else:
                        print("❌ No property data indicators found")
                        # Save page source for debugging
                        with open('debug_page.html', 'w', encoding='utf-8') as f:
                            f.write(driver.page_source)
                        print("💾 Saved page source to debug_page.html")
                except Exception as e:
                    print(f"Debug error: {e}")
                
                # Extract property data
                data = {
                    'lot_number': lot_number,
                    'municipality': municipality,
                    'address': self._extract_quebec_field(driver, [
                        '.adresse', '.address', '[data-field="address"]',
                        'td:contains("Adresse")', 'th:contains("Address")',
                        '*[class*="adresse"]', '*[id*="address"]',
                        '.property-address', '.addr', '[data-label*="adresse"]',
                        'span:contains("Adresse")', 'div:contains("Adresse")'
                    ]),
                    'owner_name': self._extract_quebec_field(driver, [
                        '.proprietaire', '.owner', '[data-field="owner"]',
                        'td:contains("Propriétaire")', 'th:contains("Owner")',
                        '*[class*="proprietaire"]', '*[id*="owner"]',
                        '.property-owner', '[data-label*="propriétaire"]',
                        'span:contains("Propriétaire")', 'div:contains("Propriétaire")'
                    ]),
                    'year_of_construction': self._extract_quebec_field(driver, [
                        '.annee_construction', '.year_built', '[data-field="year"]',
                        'td:contains("Année")', 'th:contains("Year")',
                        '*[class*="annee"]', '*[id*="year"]',
                        '[data-label*="année"]', 'span:contains("Année")',
                        'div:contains("construction")'
                    ]),
                    'total_building_sf': self._extract_quebec_field(driver, [
                        '.superficie_batiment', '.building_area', '[data-field="building_sf"]',
                        'td:contains("Superficie")', 'th:contains("Building")',
                        '*[class*="superficie"]', '*[id*="building"]',
                        '[data-label*="superficie"]', 'span:contains("Superficie")',
                        'div:contains("bâtiment")'
                    ]),
                    'land_sf': self._extract_quebec_field(driver, [
                        '.superficie_terrain', '.land_area', '[data-field="land_sf"]',
                        'td:contains("Terrain")', 'th:contains("Land")',
                        '*[class*="terrain"]', '*[id*="land"]',
                        '[data-label*="terrain"]', 'span:contains("Terrain")',
                        'div:contains("terrain")'
                    ]),
                    'tax_assessment': self._extract_quebec_field(driver, [
                        '.evaluation', '.assessment', '[data-field="assessment"]',
                        'td:contains("Évaluation")', 'th:contains("Assessment")',
                        '*[class*="evaluation"]', '*[id*="assessment"]',
                        '[data-label*="évaluation"]', 'span:contains("Évaluation")',
                        'div:contains("évaluation")', '.valeur', '.value'
                    ]),
                    'property_type': self._extract_quebec_field(driver, [
                        '.type_propriete', '.property_type', '[data-field="type"]',
                        'td:contains("Type")', 'th:contains("Type")',
                        '*[class*="type"]', '*[id*="type"]',
                        '[data-label*="type"]', 'span:contains("Type")',
                        'div:contains("utilisation")'
                    ])
                }
                
                # Debug: Show what we extracted
                print("🔍 Extracted data:")
                for key, value in data.items():
                    if value:
                        print(f"  {key}: {value}")
                
                return data
            else:
                print(f"❌ Could not find lot number input field on {eval_url}")
                return {'lot_number': lot_number, 'municipality': municipality, 'error': 'Lot input not found'}
                
        except Exception as e:
            print(f"Quebec evaluation scraping error: {e}")
            return {'lot_number': lot_number, 'municipality': municipality, 'error': str(e)}
    
    def _extract_quebec_field(self, driver, selectors):
        """Extract field value using multiple selector strategies"""
        for selector in selectors:
            try:
                if ':contains(' in selector:
                    # Handle contains selector differently
                    text = selector.split(':contains("')[1].split('")')[0]
                    elements = driver.find_elements(By.XPATH, f"//*[contains(text(), '{text}')]")
                    if elements:
                        # Look for the value in next sibling or same row
                        for element in elements:
                            try:
                                parent = element.find_element(By.XPATH, '..')
                                cells = parent.find_elements(By.TAG_NAME, 'td')
                                if len(cells) > 1:
                                    return cells[1].text.strip()
                            except:
                                continue
                else:
                    element = driver.find_element(By.CSS_SELECTOR, selector)
                    text = element.text.strip()
                    if text:
                        return text
            except:
                continue
        return ""
    
    def _scrape_quebec_business_registry(self, driver, owner_name):
        """Scrape Quebec business registry for company information"""
        try:
            print(f"🔍 Searching Quebec business registry for: {owner_name}")
            
            # Quebec business registry URL
            registry_url = "https://www.registreentreprises.gouv.qc.ca/RQAnonymeGR/GR/GR03/GR03A2_19A_PIU_RechEnt_PC/PageRechSimple.aspx"
            driver.get(registry_url)
            time.sleep(3)
            
            # Search for company name
            name_input = driver.find_element(By.ID, "NomEntreprise")
            name_input.clear()
            name_input.send_keys(owner_name)
            
            # Submit search
            search_btn = driver.find_element(By.ID, "btnRech")
            search_btn.click()
            time.sleep(3)
            
            # Extract business information
            business_data = {
                'owner_business_type': self._safe_extract_text(driver, ".type-entreprise"),
                'owner_business_status': self._safe_extract_text(driver, ".statut"),
                'owner_business_address': self._safe_extract_text(driver, ".adresse-entreprise")
            }
            
            return business_data
            
        except Exception as e:
            print(f"Business registry error: {e}")
            return {}
    
    def _safe_extract_text(self, driver, selector):
        """Safely extract text from element"""
        try:
            element = driver.find_element(By.CSS_SELECTOR, selector)
            return element.text.strip()
        except (NoSuchElementException, Exception):
            return ""
    
    def _extract_montreal_field(self, driver, keywords):
        """Extract field from Montreal results by searching for keywords"""
        try:
            # Look for text containing any of the keywords
            for keyword in keywords:
                # Try different XPath patterns
                patterns = [
                    f"//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{keyword.lower()}')]",
                    f"//td[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{keyword.lower()}')]/following-sibling::td",
                    f"//th[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{keyword.lower()}')]/following-sibling::td",
                    f"//span[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{keyword.lower()}')]/following-sibling::span",
                    f"//div[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{keyword.lower()}')]/following-sibling::div"
                ]
                
                for pattern in patterns:
                    try:
                        elements = driver.find_elements(By.XPATH, pattern)
                        for element in elements:
                            text = element.text.strip()
                            if text and len(text) > 1:
                                return text
                    except:
                        continue
            
            return ""
        except Exception as e:
            return ""
            
    def _extract_montreal_structured_data(self, driver, lot_number):
        """Extract Montreal property data from the structured display format"""
        try:
            property_data = {
                'lot_number': lot_number,
                'municipality': 'Montreal',
                'address': '',
                'owner_name': '',
                'year_of_construction': '',
                'total_building_sf': '',
                'land_sf': '',
                'tax_assessment': '',
                'property_type': '',
                'account_number': '',
                'matricule': '',
                'building_area': '',  # "Aire d'étage"
                'land_area': '',      # "Superficie du terrain"
                'evaluation_value': ''  # "Valeur d'évaluation"
            }
            
            # Get all page text to parse structured information
            page_text = driver.find_element(By.TAG_NAME, "body").text
            print(f"📄 Analyzing page for structured data extraction...")
            
            # From the output, we can see the structure:
            # Numéro de lot5829908
            # Numéro de compte foncier19 - F00803000
            # Numéro de matricule8836-93-9194-6-000-0000
            # Adresse municipale2555 Rue Alphonse-Gariépy (Mo
            
            # Parse the structured data using regex patterns
            import re
            
            # Extract address
            address_patterns = [
                r'Adresse municipale\s*([^\n]+)',
                r'Adresse\s*[:\-]\s*([^\n]+)',
                r'(\d{1,5}\s+[^\n]+(?:Rue|Avenue|Boulevard|Street|Ave|Blvd)[^\n]*)'
            ]
            
            for pattern in address_patterns:
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    property_data['address'] = match.group(1).strip()
                    break
            
            # Extract account number
            account_match = re.search(r'Numéro de compte foncier\s*([^\n]+)', page_text, re.IGNORECASE)
            if account_match:
                property_data['account_number'] = account_match.group(1).strip()
            
            # Extract matricule
            matricule_match = re.search(r'Numéro de matricule\s*([^\n]+)', page_text, re.IGNORECASE)
            if matricule_match:
                property_data['matricule'] = matricule_match.group(1).strip()
            
            # NEW: Extract "Aire d'étage" (building area) - PRIMARY TARGET
            building_area_patterns = [
                r"Aire d'étage\s*[:\-]?\s*([0-9,\.\s]+(?:m²|pi²|sq ft)?)",
                r"Aire d'etage\s*[:\-]?\s*([0-9,\.\s]+(?:m²|pi²|sq ft)?)",
                r"Building area\s*[:\-]?\s*([0-9,\.\s]+(?:m²|pi²|sq ft)?)",
                r"Floor area\s*[:\-]?\s*([0-9,\.\s]+(?:m²|pi²|sq ft)?)"
            ]
            
            for pattern in building_area_patterns:
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    property_data['building_area'] = match.group(1).strip()
                    property_data['total_building_sf'] = match.group(1).strip()  # Also populate this field
                    print(f"🏗️ FOUND BUILDING AREA: {property_data['building_area']}")
                    break
            
            # Extract land area/terrain
            land_area_patterns = [
                r"Superficie du terrain\s*[:\-]?\s*([0-9,\.\s]+(?:m²|pi²|sq ft)?)",
                r"Land area\s*[:\-]?\s*([0-9,\.\s]+(?:m²|pi²|sq ft)?)",
                r"Terrain\s*[:\-]?\s*([0-9,\.\s]+(?:m²|pi²|sq ft)?)"
            ]
            
            for pattern in land_area_patterns:
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    property_data['land_area'] = match.group(1).strip()
                    property_data['land_sf'] = match.group(1).strip()  # Also populate this field
                    print(f"🌍 FOUND LAND AREA: {property_data['land_area']}")
                    break
            
            # Look for other property details in the page
            # Check for property assessment/evaluation details
            eval_patterns = [
                r"Valeur d'évaluation\s*[:\-]?\s*([0-9,\.\s]+\$?)",
                r'Valeur\s*[:\-]\s*([0-9,\.\s]+\$?)',
                r'Évaluation\s*[:\-]\s*([0-9,\.\s]+\$?)',
                r'Assessment\s*[:\-]\s*([0-9,\.\s]+\$?)'
            ]
            
            for pattern in eval_patterns:
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    property_data['evaluation_value'] = match.group(1).strip()
                    property_data['tax_assessment'] = match.group(1).strip()  # Also populate this field
                    print(f"💰 FOUND EVALUATION VALUE: {property_data['evaluation_value']}")
                    break
            
            # Extract year of construction
            year_patterns = [
                r'Année de construction\s*[:\-]\s*(\d{4})',
                r'Construction\s*[:\-]\s*(\d{4})',
                r'Built\s*[:\-]\s*(\d{4})'
            ]
            
            for pattern in year_patterns:
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    property_data['year_of_construction'] = match.group(1).strip()
                    print(f"📅 FOUND CONSTRUCTION YEAR: {property_data['year_of_construction']}")
                    break
            
            # Extract owner information
            owner_patterns = [
                r'Propriétaire\s*[:\-]\s*([^\n]+)',
                r'Owner\s*[:\-]\s*([^\n]+)',
                r'Titulaire\s*[:\-]\s*([^\n]+)'
            ]
            
            for pattern in owner_patterns:
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    property_data['owner_name'] = match.group(1).strip()
                    print(f"👤 FOUND OWNER: {property_data['owner_name']}")
                    break
                    
            # Extract property type/usage
            type_patterns = [
                r'Usage\s*[:\-]\s*([^\n]+)',
                r'Type\s*[:\-]\s*([^\n]+)',
                r'Utilisation\s*[:\-]\s*([^\n]+)'
            ]
            
            for pattern in type_patterns:
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    property_data['property_type'] = match.group(1).strip()
                    print(f"🏢 FOUND PROPERTY TYPE: {property_data['property_type']}")
                    break
                    
            print(f"🔍 Extracted structured data: {property_data}")
            
            # Check if we found the critical "Aire d'étage" field
            if property_data['building_area']:
                print(f"🎉 SUCCESS! Found 'Aire d'étage': {property_data['building_area']}")
                return property_data
            else:
                print(f"⚠️ 'Aire d'étage' not found, but extracted other data")
                return property_data
            
        except Exception as e:
            print(f"Error extracting structured data: {e}")
            return None
    
    def _scrape_montreal_evaluation(self, driver, lot_number, municipality, server_num):
        """
        Handle Montreal's specific evaluation system
        
        IMPORTANT: Montreal does NOT require AWS VPN rotation
        - Direct connection works successfully with proper anti-detection
        - Anti-detection requirements: French Canadian locale, human-like behavior
        - Navigation: search → results → property detail page
        - Successfully extracts "Aire d'étage" and other detail page fields
        """
        try:
            print(f"🏙️ Processing Montreal evaluation for lot {lot_number}")
            
            # Wait for the page to load completely
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Additional anti-detection: simulate human behavior
            print("🤖 Simulating human behavior...")
            driver.execute_script("window.scrollTo(0, 100);")  # Small scroll
            time.sleep(2)
            driver.execute_script("window.scrollTo(0, 0);")    # Back to top
            time.sleep(1)
            
            # DEBUG: Check what's on the Montreal page
            print(f"📄 Montreal page title: {driver.title}")
            print(f"📄 Montreal page URL: {driver.current_url}")
            
            # Look for lot number input field on Montreal site
            lot_selectors = [
                'input[name="lotNumber"]',  # Found this specific field!
                'input[name="lot"]',
                'input[id*="lot"]',
                'input[placeholder*="lot"]',
                'input[placeholder*="numéro"]',
                'input[type="text"]',
                'input[type="search"]'
            ]
            
            lot_input = None
            for selector in lot_selectors:
                try:
                    lot_input = driver.find_element(By.CSS_SELECTOR, selector)
                    if lot_input.is_displayed():
                        print(f"✅ Found Montreal lot input: {selector}")
                        break
                except:
                    continue
            
            if lot_input:
                # Enter the lot number with human-like typing
                lot_input.clear()
                time.sleep(0.5)  # Pause after clearing
                
                # Type digit by digit with small delays (human-like)
                for digit in str(lot_number):
                    lot_input.send_keys(digit)
                    time.sleep(0.1 + (0.05 * (int(digit) % 3)))  # Variable delay
                
                print(f"✅ Entered Montreal lot number: {lot_number}")
                time.sleep(1)  # Pause before submitting
                
                # Look for search button
                search_buttons = [
                    'button[type="submit"]',
                    'input[type="submit"]',
                    'button:contains("Rechercher")',
                    'button:contains("Search")',
                    '.search-btn',
                    '.btn-search'
                ]
                
                for btn_selector in search_buttons:
                    try:
                        search_btn = driver.find_element(By.CSS_SELECTOR, btn_selector)
                        if search_btn.is_displayed():
                            print(f"🎯 Found Montreal search button: {search_btn.text}")
                            
                            # Enhanced human-like interaction
                            driver.execute_script("arguments[0].focus();", search_btn)
                            time.sleep(0.5)
                            driver.execute_script("arguments[0].scrollIntoView(true);", search_btn)
                            time.sleep(1)
                            
                            # Simulate mouse hover
                            driver.execute_script("""
                                var element = arguments[0];
                                var event = new MouseEvent('mouseover', {
                                    'view': window,
                                    'bubbles': true,
                                    'cancelable': true
                                });
                                element.dispatchEvent(event);
                            """, search_btn)
                            time.sleep(0.5)
                            
                            search_btn.click()
                            print(f"✅ Clicked Montreal search button")
                            time.sleep(8)  # Increased wait time for results
                            break
                    except:
                        continue
                
                # Wait for search results list to load
                print("⏳ Waiting for Montreal search results list...")
                time.sleep(5)  # Give more time for results to load
                
                # Check current URL to see if we're on results page
                current_url = driver.current_url
                print(f"📄 Current URL after search: {current_url}")
                
                # Debug: Print page content to understand structure
                try:
                    page_text = driver.find_element(By.TAG_NAME, "body").text
                    print(f"📄 Page contains '{lot_number}': {'Yes' if lot_number in page_text else 'No'}")
                    if lot_number in page_text:
                        # Find context around the lot number
                        lines = page_text.split('\n')
                        for i, line in enumerate(lines):
                            if lot_number in line:
                                print(f"📄 Lot context (line {i}): {line.strip()}")
                                # Print surrounding lines for context
                                for j in range(max(0, i-2), min(len(lines), i+3)):
                                    if j != i:
                                        print(f"    Line {j}: {lines[j].strip()}")
                                break
                except Exception as e:
                    print(f"Error reading page content: {e}")
                
                # FOCUSED NAVIGATION: Look for the specific submit button in the property result (PRIORITY APPROACH)
                print("🎯 FOCUSED NAVIGATION: Looking for property result submit buttons...")
                
                # Try multiple approaches to find the property entry
                property_clicked = False
                
                # Based on the HTML structure provided, look for:
                # 1. List items containing our lot number
                # 2. Forms with action="/role-evaluation-fonciere/lot-renove/liste/resultat"
                # 3. Submit buttons with evalUnitId
                
                focused_patterns = [
                    # Look for forms with the specific action URL
                    "//form[@action='/role-evaluation-fonciere/lot-renove/liste/resultat']//button[@type='submit']",
                    "//form[contains(@action, 'resultat')]//button[@type='submit']",
                    
                    # Look for buttons with chevron-right icon (from HTML structure)
                    "//button[.//span[contains(@class, 'icon-chevron-right')]]",
                    "//button[@data-test='button'][@type='submit']",
                    
                    # Look for list items containing our lot number with submit buttons
                    f"//li[contains(., '{lot_number}')]//button[@type='submit']",
                    f"//li[contains(., 'Numéro de lot')]//button[@type='submit']",
                    
                    # Look for any submit button near our lot number
                    f"//div[contains(text(), '{lot_number}')]//following-sibling::*//button[@type='submit']",
                    f"//div[contains(text(), '{lot_number}')]//ancestor::li//button[@type='submit']",
                    
                    # Generic submit buttons that might work
                    "//button[@type='submit']",
                    "//input[@type='submit']",
                ]
                
                max_attempts = 3  # Try multiple times if needed
                attempt = 0
                
                while not property_clicked and attempt < max_attempts:
                    attempt += 1
                    print(f"🔄 Navigation attempt {attempt}/{max_attempts}")
                    
                    for pattern in focused_patterns:
                        try:
                            submit_buttons = driver.find_elements(By.XPATH, pattern)
                            print(f"🔍 Found {len(submit_buttons)} submit buttons with pattern: {pattern}")
                            
                            for button in submit_buttons:
                                try:
                                    if button.is_displayed():
                                        # Get button context to verify it's related to our property
                                        button_parent = button.find_element(By.XPATH, "..")
                                        parent_text = button_parent.text if button_parent else ""
                                        
                                        # Get form details if it's in a form
                                        try:
                                            form = button.find_element(By.XPATH, ".//ancestor::form[1]")
                                            form_action = form.get_attribute('action') or ''
                                            eval_unit_input = form.find_elements(By.XPATH, ".//input[@name='evalUnitId']")
                                            eval_unit_id = eval_unit_input[0].get_attribute('value') if eval_unit_input else 'N/A'
                                        except:
                                            form_action = ''
                                            eval_unit_id = 'N/A'
                                        
                                        print(f"🎯 Submit button found:")
                                        print(f"    Form action: {form_action}")
                                        print(f"    EvalUnitId: {eval_unit_id}")
                                        print(f"    Parent context: {parent_text[:100]}...")
                                        
                                        # Check if this button is related to our lot number
                                        if (lot_number in parent_text or 
                                            'resultat' in form_action or 
                                            eval_unit_id != 'N/A'):
                                            
                                            print(f"✅ CLICKING property-related submit button!")
                                            print(f"    🎯 Target: EvalUnitId={eval_unit_id}, Action={form_action}")
                                            
                                            # Scroll to button to ensure it's clickable
                                            driver.execute_script("arguments[0].scrollIntoView(true);", button)
                                            time.sleep(1)
                                            
                                            # Click the button
                                            button.click()
                                            property_clicked = True
                                            
                                            # Wait for navigation and check result
                                            time.sleep(5)
                                            new_url = driver.current_url
                                            print(f"📄 After clicking submit button - URL: {new_url}")
                                            
                                            # Verify we navigated to the property detail page
                                            if ('resultat' in new_url or 
                                                new_url != 'https://montreal.ca/role-evaluation-fonciere/lot-renove/liste'):
                                                print(f"🎉 SUCCESS! Navigated to property detail page!")
                                                
                                                # Extract property data from the detail page
                                                try:
                                                    time.sleep(3)  # Wait for page to fully load
                                                    print(f"🔍 Extracting property data from detail page...")
                                                    
                                                    # Call the enhanced data extraction method
                                                    extracted_data = self._extract_montreal_structured_data(driver, lot_number)
                                                    
                                                    # Check if we found the key target field
                                                    if extracted_data.get('building_area'):
                                                        print(f"🏗️ SUCCESS! Found 'Aire d'étage': {extracted_data['building_area']}")
                                                    else:
                                                        print(f"⚠️ 'Aire d'étage' not found in extracted data")
                                                        # Show what we did find
                                                        found_fields = [k for k, v in extracted_data.items() if v and v != lot_number and v != 'Montreal']
                                                        print(f"📄 Found fields: {found_fields}")
                                                    
                                                    # Return the extracted data immediately since we succeeded
                                                    return extracted_data
                                                    
                                                except Exception as e:
                                                    print(f"❌ Error extracting data from detail page: {e}")
                                                
                                                break
                                            else:
                                                print(f"⚠️ URL didn't change as expected, continuing search...")
                                                property_clicked = False
                                
                                except Exception as e:
                                    print(f"   ❌ Error clicking submit button: {e}")
                                    continue
                            
                            if property_clicked:
                                break
                                
                        except Exception as e:
                            print(f"❌ Error with pattern {pattern}: {e}")
                            continue
                    
                    if property_clicked:
                        break
                    
                    # Wait before next attempt
                    if attempt < max_attempts:
                        print(f"⏳ Waiting before next attempt...")
                        time.sleep(2)
                
                # If focused navigation succeeded, skip the rest of the old logic
                if property_clicked:
                    print("🎯 Focused navigation succeeded, skipping legacy approaches")
                else:
                    print("🔄 Focused navigation failed, trying legacy approaches...")
                    
                    # LEGACY NAVIGATION - Method 1: Look for the exact "Numéro de lot : XXXX" pattern that should be clickable
                    exact_patterns = [
                        f"//*[contains(text(), 'Numéro de lot : {lot_number}')]",
                        f"//*[text()='Numéro de lot : {lot_number}']",
                        f"//*[normalize-space(text())='Numéro de lot : {lot_number}']"
                    ]
                    
                    for pattern in exact_patterns:
                        try:
                            exact_elements = driver.find_elements(By.XPATH, pattern)
                            print(f"🔍 Found {len(exact_elements)} exact elements with pattern: {pattern}")
                            
                            for element in exact_elements:
                                try:
                                    if element.is_displayed():
                                        print(f"✅ Found exact 'Numéro de lot : {lot_number}' element!")
                                        print(f"📄 Element tag: {element.tag_name}")
                                        print(f"📄 Element text: '{element.text.strip()}'")
                                        
                                        # Try clicking this exact element
                                        element.click()
                                        property_clicked = True
                                        time.sleep(3)
                                        print(f"📄 After clicking exact element - URL: {driver.current_url}")
                                        break
                                except Exception as e:
                                    print(f"   Error clicking exact element: {e}")
                                    continue
                            
                            if property_clicked:
                                break
                                
                        except Exception as e:
                            print(f"Error with exact pattern {pattern}: {e}")
                            continue
                    
                    # Method 2: Based on Tavily research - look for "Consulter" and assessment roll links
                    if not property_clicked:
                        print("🔍 Looking for Montreal assessment roll links (Tavily research insights)...")
                        
                        # Based on research: look for "Consulter le rôle d'évaluation" type links
                        montreal_assessment_patterns = [
                            f"//a[contains(text(), 'Consulter') and contains(text(), '{lot_number}')]",  # Consult link with lot number
                            f"//a[contains(text(), 'Consulter le rôle')]",  # Assessment roll consult link
                            f"//a[contains(text(), 'Extrait du rôle')]",  # Assessment roll extract
                            f"//a[contains(text(), 'rôle d\\'évaluation')]",  # Assessment roll link
                            f"//button[contains(text(), 'Consulter') and contains(text(), '{lot_number}')]",  # Consult button
                            f"//a[contains(@href, 'role') and contains(text(), '{lot_number}')]",  # Role URL with lot number
                            f"//a[contains(@href, 'evaluation') and contains(text(), '{lot_number}')]",  # Evaluation URL
                        ]
                    
                    for pattern in montreal_assessment_patterns:
                        try:
                            assessment_links = driver.find_elements(By.XPATH, pattern)
                            print(f"🔍 Found {len(assessment_links)} assessment links with pattern: {pattern}")
                            
                            for link in assessment_links:
                                try:
                                    if link.is_displayed():
                                        link_text = link.text.strip()
                                        link_href = link.get_attribute('href') or ''
                                        
                                        print(f"🎯 Assessment link: '{link_text}' -> {link_href}")
                                        
                                        # Skip contact/coordinate buttons (from earlier research)
                                        if any(skip_word in link_text.lower() for skip_word in ['coordonnées', 'contactez', 'contact']):
                                            print(f"⏭️ Skipping contact link: {link_text}")
                                            continue
                                        
                                        # Priority: links that contain "role", "evaluation", or our lot number
                                        if any(priority_word in link_text.lower() for priority_word in ['consulter', 'rôle', 'evaluation', lot_number]):
                                            print(f"✅ Clicking priority assessment link: {link_text}")
                                            link.click()
                                            property_clicked = True
                                            time.sleep(3)
                                            print(f"📄 After clicking assessment link - URL: {driver.current_url}")
                                            break
                                        
                                except Exception as e:
                                    print(f"   Error clicking assessment link: {e}")
                                    continue
                            
                            if property_clicked:
                                break
                                
                        except Exception as e:
                            print(f"Error with assessment pattern {pattern}: {e}")
                            continue
                
                # Method 3: Look for standard property entry patterns if lot selection didn't work
                if not property_clicked:
                    print("🔍 Looking for standard property entry patterns...")
                    # Method 1: Look for clickable elements that contain both "Numéro de lot" and the lot number
                    property_entry_patterns = [
                        f"//div[contains(text(), 'Numéro de lot : {lot_number}')]",  # Exact format from screenshot
                        f"//span[contains(text(), 'Numéro de lot : {lot_number}')]", 
                        f"//p[contains(text(), 'Numéro de lot : {lot_number}')]",
                        f"//li[contains(text(), 'Numéro de lot : {lot_number}')]",
                        f"//*[contains(text(), 'Numéro de lot : {lot_number}')]",   # Any element with exact text
                        f"//div[contains(text(), 'Numéro de lot') and contains(text(), '{lot_number}')]",
                        f"//span[contains(text(), 'Numéro de lot') and contains(text(), '{lot_number}')]", 
                        f"//p[contains(text(), 'Numéro de lot') and contains(text(), '{lot_number}')]",
                        f"//li[contains(text(), 'Numéro de lot') and contains(text(), '{lot_number}')]",
                        f"//tr[contains(., 'Numéro de lot') and contains(., '{lot_number}')]",
                        f"//div[contains(., '{lot_number}') and contains(., 'Numéro de lot')]"
                    ]
                
                for pattern in property_entry_patterns:
                    try:
                        property_entries = driver.find_elements(By.XPATH, pattern)
                        print(f"🔍 Found {len(property_entries)} property entries with pattern: {pattern}")
                        
                        for entry in property_entries:
                            try:
                                if entry.is_displayed():
                                    entry_text = entry.text.strip()
                                    print(f"🏠 Property entry: {entry_text[:150]}")
                                    
                                    # BREAKTHROUGH: We found "Consulter le rôle d'évaluation foncière" in the text!
                                    # Look specifically for this text and click it
                                    if lot_number in entry_text and 'consulter le rôle' in entry_text.lower():
                                        print(f"✅ Found 'Consulter le rôle d'évaluation foncière' section!")
                                        
                                        # Look for clickable "Consulter" text/link within this section
                                        consulter_patterns = [
                                            ".//a[contains(text(), 'Consulter le rôle')]",
                                            ".//a[contains(text(), 'Consulter')]",
                                            ".//button[contains(text(), 'Consulter le rôle')]",
                                            ".//button[contains(text(), 'Consulter')]",
                                            ".//span[contains(text(), 'Consulter le rôle')]",
                                            ".//div[contains(text(), 'Consulter le rôle')]"
                                        ]
                                        
                                        consulter_clicked = False
                                        for pattern in consulter_patterns:
                                            try:
                                                consulter_elements = entry.find_elements(By.XPATH, pattern)
                                                print(f"    Found {len(consulter_elements)} 'Consulter' elements with pattern: {pattern}")
                                                
                                                for consulter_elem in consulter_elements:
                                                    try:
                                                        if consulter_elem.is_displayed():
                                                            consulter_text = consulter_elem.text.strip()
                                                            consulter_href = consulter_elem.get_attribute('href') or ''
                                                            
                                                            print(f"    🔍 Examining Consulter element: '{consulter_text}' -> {consulter_href}")
                                                            
                                                            # Skip contact/coordinate related links
                                                            if any(skip_word in consulter_text.lower() for skip_word in ['coordonnées', 'contactez', 'contact']):
                                                                print(f"    ⏭️ Skipping contact Consulter: {consulter_text}")
                                                                continue
                                                            
                                                            # Skip if href looks like contact page
                                                            if any(skip_word in consulter_href.lower() for skip_word in ['contact', 'coordonnees']):
                                                                print(f"    ⏭️ Skipping contact URL: {consulter_href}")
                                                                continue
                                                            
                                                            # Priority: Consulter links related to property evaluation
                                                            if any(property_word in consulter_text.lower() for property_word in ['rôle', 'evaluation', 'foncière', 'propriété']):
                                                                print(f"    ✅ Clicking property-related Consulter: '{consulter_text}'")
                                                                consulter_elem.click()
                                                                consulter_clicked = True
                                                                property_clicked = True
                                                                time.sleep(3)
                                                                print(f"📄 After clicking property Consulter - URL: {driver.current_url}")
                                                                break
                                                            
                                                            # If it's just "Consulter" without contact words, try it
                                                            elif consulter_text.lower() == 'consulter':
                                                                print(f"    ✅ Clicking generic Consulter: '{consulter_text}'")
                                                                consulter_elem.click()
                                                                consulter_clicked = True
                                                                property_clicked = True
                                                                time.sleep(3)
                                                                print(f"📄 After clicking generic Consulter - URL: {driver.current_url}")
                                                                break
                                                            
                                                    except Exception as e:
                                                        print(f"       Error clicking Consulter element: {e}")
                                                        continue
                                                        
                                                if consulter_clicked:
                                                    break
                                                    
                                            except Exception as e:
                                                print(f"    Error with Consulter pattern {pattern}: {e}")
                                                continue
                                        
                                        # If no specific Consulter element found, try clicking the entry itself
                                        if not consulter_clicked:
                                            print(f"    🔄 No specific Consulter element found, clicking the entry itself")
                                            # If the entry itself is clickable, try clicking it
                                            if entry.tag_name in ['a', 'button'] or 'click' in (entry.get_attribute('onclick') or ''):
                                                print(f"✅ Clicking property entry directly")
                                                entry.click()
                                                property_clicked = True
                                                time.sleep(3)
                                                print(f"📄 After clicking entry - URL: {driver.current_url}")
                                            else:
                                                # Look for clickable children (links or buttons within the entry)
                                                clickable_children = entry.find_elements(By.XPATH, ".//a | .//button")
                                                if clickable_children:
                                                    print(f"✅ Clicking child element in property entry")
                                                    clickable_children[0].click()
                                                    property_clicked = True
                                                    time.sleep(3)
                                                    break
                                                else:
                                                    # Try clicking the entry anyway (might be clickable div)
                                                    print(f"✅ Attempting to click property entry div")
                                                    entry.click()
                                                    property_clicked = True
                                                    time.sleep(3)
                                                    break
                            except Exception as e:
                                print(f"   Error clicking property entry: {e}")
                                continue
                        
                        if property_clicked:
                            break
                            
                    except Exception as e:
                        print(f"Error with pattern {pattern}: {e}")
                        continue
                
                # If still no luck with property-specific patterns, try the original approach
                if not property_clicked:
                    print("🔍 Trying original link-based approach...")
                    # Look for clickable property results
                    property_link_selectors = [
                        f'a[href*="{lot_number}"]',  # Link containing lot number
                        '.result a',  # Link in result class
                        '.property a',  # Link in property class
                        'tbody tr a',  # Table body row links
                        'table a',  # Any table links
                        'a[href*="detail"]',  # Detail page links
                        'a[href*="property"]',  # Property page links
                    ]
                
                    for selector in property_link_selectors:
                        try:
                            property_links = driver.find_elements(By.CSS_SELECTOR, selector)
                            print(f"🔍 Found {len(property_links)} potential property links with selector: {selector}")
                            
                            for i, link in enumerate(property_links[:5]):  # Try first 5 links
                                try:
                                    link_text = link.text.strip()
                                    link_href = link.get_attribute('href')
                                    print(f"  Link {i}: text='{link_text}', href='{link_href}'")
                                    
                                    # Click the first visible link that seems relevant
                                    if link.is_displayed() and (lot_number in link_text or lot_number in str(link_href)):
                                        print(f"✅ Clicking property link: {link_text}")
                                        link.click()
                                        property_clicked = True
                                        time.sleep(5)  # Wait for property detail page to load
                                        break
                                except Exception as e:
                                    print(f"  Error with link {i}: {e}")
                                    continue
                            
                            if property_clicked:
                                break
                                
                        except Exception as e:
                            print(f"Error with selector {selector}: {e}")
                            continue
                        continue
                
                if not property_clicked:
                    print("⚠️ Could not find property link to click, looking for property section")
                    # Look specifically for the property section containing "Numéro de lot : [lot_number]"
                    try:
                        # More specific patterns for the Montreal property section
                        lot_section_patterns = [
                            f"//*[contains(text(), 'Numéro de lot : {lot_number}')]",
                            f"//*[contains(text(), 'Numéro de lot') and contains(text(), '{lot_number}')]",
                            f"//div[contains(text(), 'Numéro de lot : {lot_number}')]",
                            f"//span[contains(text(), 'Numéro de lot : {lot_number}')]",
                            f"//*[contains(text(), '{lot_number}')]/ancestor::div[1]",
                            f"//*[contains(text(), '{lot_number}')]/parent::div",
                        ]
                        
                        print(f"🔍 Looking for property section with 'Numéro de lot : {lot_number}'")
                        
                        for pattern in lot_section_patterns:
                            try:
                                property_sections = driver.find_elements(By.XPATH, pattern)
                                print(f"🔍 Found {len(property_sections)} sections with pattern: {pattern}")
                                
                                for section in property_sections:
                                    try:
                                        if section.is_displayed():
                                            section_text = section.text.strip()
                                            print(f"🏠 Property section: {section_text[:150]}")
                                            
                                            # Check if this section contains our lot number and property info
                                            if lot_number in section_text and ('Numéro de lot' in section_text or 'municipale' in section_text.lower()):
                                                print(f"✅ Found target property section! Clicking...")
                                                section.click()
                                                property_clicked = True
                                                time.sleep(5)
                                                print(f"� After clicking property section - URL: {driver.current_url}")
                                                break
                                    except Exception as e:
                                        print(f"   Error clicking section: {e}")
                                        continue
                                
                                if property_clicked:
                                    break
                                    
                            except Exception as e:
                                print(f"Error with pattern {pattern}: {e}")
                                continue
                    except Exception as e:
                        print(f"Error finding property sections: {e}")
                
                # If still not clicked, try the original fallback method
                if not property_clicked:
                    try:
                        lot_elements = driver.find_elements(By.XPATH, f"//*[contains(text(), '{lot_number}')]")
                        for element in lot_elements:
                            try:
                                if element.is_displayed() and element.tag_name in ['a', 'button', 'td', 'tr', 'div']:
                                    print(f"🔄 Fallback: Trying to click element with lot number: {element.text.strip()}")
                                    element.click()
                                    property_clicked = True
                                    time.sleep(5)
                                    break
                            except:
                                continue
                    except:
                        pass
                
                # After clicking, look for property-specific detail buttons
                if property_clicked:
                    print("🔍 Looking for property detail buttons in the same section...")
                    
                    # First try to find "Consulter" buttons that are specifically related to the property/lot
                    detail_button_patterns = [
                        f"//div[contains(text(), '{lot_number}')]//following-sibling::*//a[contains(text(), 'Consulter')]",
                        f"//div[contains(text(), '{lot_number}')]//ancestor::div[1]//a[contains(text(), 'Consulter')]",
                        f"//*[contains(text(), '{lot_number}')]/ancestor::tr//a[contains(text(), 'Consulter')]",
                        f"//*[contains(text(), '{lot_number}')]/parent::*/following-sibling::*//a[contains(text(), 'Consulter')]",
                        "//a[contains(text(), 'Consulter') and not(contains(text(), 'coordonnées'))]",  # Avoid "contact us" button
                        "//a[contains(text(), 'Consulter') and not(contains(text(), 'Contactez'))]",    # Avoid "contact" related
                        "//button[contains(text(), 'Détails')]",
                        "//a[contains(text(), 'Détails')]",
                        "//button[contains(text(), 'Voir')]",
                        "//a[contains(text(), 'Voir')]"
                    ]
                    
                    for btn_pattern in detail_button_patterns:
                        try:
                            detail_buttons = driver.find_elements(By.XPATH, btn_pattern)
                            if detail_buttons:
                                print(f"Found {len(detail_buttons)} detail buttons with pattern: {btn_pattern}")
                                for btn in detail_buttons:
                                    try:
                                        if btn.is_displayed():
                                            btn_text = btn.text.strip()
                                            btn_href = btn.get_attribute('href') or ''
                                            
                                            # Skip contact/coordinate buttons
                                            if any(skip_word in btn_text.lower() for skip_word in ['coordonnées', 'contactez', 'contact']):
                                                print(f"⏭️ Skipping contact button: {btn_text}")
                                                continue
                                            
                                            # Skip if href looks like contact page
                                            if any(skip_word in btn_href.lower() for skip_word in ['contact', 'coordonnees']):
                                                print(f"⏭️ Skipping contact link: {btn_href}")
                                                continue
                                                
                                            print(f"✅ Clicking property detail button: {btn_text}")
                                            btn.click()
                                            time.sleep(5)
                                            print(f"📄 After detail click - URL: {driver.current_url}")
                                            break
                                    except Exception as e:
                                        print(f"Error clicking button: {e}")
                                        continue
                                break
                        except Exception as e:
                            print(f"Error with pattern {btn_pattern}: {e}")
                            continue
                
                # NEW APPROACH: Look for property result items that contain all the property data
                if not property_clicked:
                    print("🔍 NEW APPROACH: Looking for complete property result items...")
                    
                    # Look for elements that contain the structured property data we saw in the output
                    property_result_patterns = [
                        f"//div[contains(text(), 'Numéro de lot{lot_number}')]",  # Exact format from output
                        f"//div[contains(text(), '{lot_number}') and contains(text(), 'Adresse municipale')]",  # Contains lot + address
                        f"//div[contains(text(), '{lot_number}') and contains(text(), 'compte foncier')]",  # Contains lot + account
                        f"//div[contains(text(), '{lot_number}') and contains(text(), 'matricule')]",  # Contains lot + matricule
                        f"//*[contains(text(), 'Numéro de lot{lot_number}')]",  # Any element with this format
                        f"//li[contains(., '{lot_number}') and contains(., 'Adresse')]",  # List item with lot and address
                        f"//tr[contains(., '{lot_number}') and contains(., 'Adresse')]",  # Table row with lot and address
                        f"//div[contains(., '{lot_number}') and contains(., 'Numéro de compte')]",  # Div with lot and account
                        f"//button[contains(., '{lot_number}')]",  # Button containing lot number
                        f"//a[contains(., '{lot_number}') and contains(., 'Adresse')]",  # Link with lot and address
                    ]
                    
                    for pattern in property_result_patterns:
                        try:
                            result_elements = driver.find_elements(By.XPATH, pattern)
                            print(f"🔍 Found {len(result_elements)} property result elements with pattern: {pattern}")
                            
                            for element in result_elements:
                                try:
                                    if element.is_displayed():
                                        element_text = element.text.strip()
                                        print(f"🏠 Property result element: {element_text[:200]}")
                                        
                                        # Check if this element contains the key property data we need
                                        if lot_number in element_text and any(key in element_text for key in ['Adresse', 'compte', 'matricule']):
                                            print(f"✅ Found complete property data element!")
                                            
                                            # Try clicking this element directly
                                            try:
                                                print(f"🖱️ Attempting direct click on property result element...")
                                                element.click()
                                                property_clicked = True
                                                time.sleep(5)  # Wait longer for page navigation
                                                print(f"📄 After clicking property result - URL: {driver.current_url}")
                                                
                                                # Check if URL changed to indicate successful navigation
                                                if 'detail' in driver.current_url or 'resultat' in driver.current_url or driver.current_url != 'https://montreal.ca/role-evaluation-fonciere/lot-renove/liste':
                                                    print(f"✅ Successfully navigated to property detail page!")
                                                    break
                                                else:
                                                    print(f"⚠️ URL didn't change, trying alternative clicking methods...")
                                                    property_clicked = False
                                                    
                                            except Exception as click_e:
                                                print(f"❌ Direct click failed: {click_e}")
                                                
                                                # If direct click fails, look for clickable children
                                                clickable_links = element.find_elements(By.XPATH, ".//a | .//button")
                                                if clickable_links:
                                                    print(f"🔗 Found {len(clickable_links)} clickable children, trying first one...")
                                                    for link in clickable_links:
                                                        try:
                                                            if link.is_displayed():
                                                                link_text = link.text.strip()
                                                                link_href = link.get_attribute('href') or ''
                                                                print(f"🔗 Clicking child link: '{link_text}' -> {link_href}")
                                                                link.click()
                                                                property_clicked = True
                                                                time.sleep(5)
                                                                print(f"📄 After clicking child link - URL: {driver.current_url}")
                                                                
                                                                # Check if navigation was successful
                                                                if driver.current_url != 'https://montreal.ca/role-evaluation-fonciere/lot-renove/liste':
                                                                    print(f"✅ Successfully navigated via child link!")
                                                                    break
                                                        except Exception as child_e:
                                                            print(f"❌ Child link click failed: {child_e}")
                                                            continue
                                                    
                                                    if property_clicked:
                                                        break
                                                
                                                # Try finding and clicking parent container
                                                try:
                                                    parent = element.find_element(By.XPATH, "..")
                                                    if parent and parent.is_displayed():
                                                        print(f"🔗 Trying parent element click...")
                                                        parent.click()
                                                        property_clicked = True
                                                        time.sleep(5)
                                                        print(f"📄 After clicking parent - URL: {driver.current_url}")
                                                        
                                                        if driver.current_url != 'https://montreal.ca/role-evaluation-fonciere/lot-renove/liste':
                                                            print(f"✅ Successfully navigated via parent click!")
                                                            break
                                                        
                                                except Exception as parent_e:
                                                    print(f"❌ Parent click failed: {parent_e}")
                                
                                except Exception as e:
                                    print(f"   Error with property result element: {e}")
                                    continue
                            
                            if property_clicked:
                                break
                                
                        except Exception as e:
                            print(f"Error with result pattern {pattern}: {e}")
                            continue
                
                # FOCUSED NAVIGATION: Look for the specific submit button in the property result
                if not property_clicked:
                    print("🎯 FOCUSED NAVIGATION: Looking for property result submit buttons...")
                    
                    # Based on the HTML structure provided, look for:
                    # 1. List items containing our lot number
                    # 2. Forms with action="/role-evaluation-fonciere/lot-renove/liste/resultat"
                    # 3. Submit buttons with evalUnitId
                    
                    focused_patterns = [
                        # Look for forms with the specific action URL
                        "//form[@action='/role-evaluation-fonciere/lot-renove/liste/resultat']//button[@type='submit']",
                        "//form[contains(@action, 'resultat')]//button[@type='submit']",
                        
                        # Look for buttons with chevron-right icon (from HTML structure)
                        "//button[.//span[contains(@class, 'icon-chevron-right')]]",
                        "//button[@data-test='button'][@type='submit']",
                        
                        # Look for list items containing our lot number with submit buttons
                        f"//li[contains(., '{lot_number}')]//button[@type='submit']",
                        f"//li[contains(., 'Numéro de lot')]//button[@type='submit']",
                        
                        # Look for any submit button near our lot number
                        f"//div[contains(text(), '{lot_number}')]//following-sibling::*//button[@type='submit']",
                        f"//div[contains(text(), '{lot_number}')]//ancestor::li//button[@type='submit']",
                        
                        # Generic submit buttons that might work
                        "//button[@type='submit']",
                        "//input[@type='submit']",
                    ]
                    
                    max_attempts = 3  # Try multiple times if needed
                    attempt = 0
                    
                    while not property_clicked and attempt < max_attempts:
                        attempt += 1
                        print(f"🔄 Navigation attempt {attempt}/{max_attempts}")
                        
                        for pattern in focused_patterns:
                            try:
                                submit_buttons = driver.find_elements(By.XPATH, pattern)
                                print(f"🔍 Found {len(submit_buttons)} submit buttons with pattern: {pattern}")
                                
                                for button in submit_buttons:
                                    try:
                                        if button.is_displayed():
                                            # Get button context to verify it's related to our property
                                            button_parent = button.find_element(By.XPATH, "..")
                                            parent_text = button_parent.text if button_parent else ""
                                            
                                            # Get form details if it's in a form
                                            try:
                                                form = button.find_element(By.XPATH, ".//ancestor::form[1]")
                                                form_action = form.get_attribute('action') or ''
                                                eval_unit_input = form.find_elements(By.XPATH, ".//input[@name='evalUnitId']")
                                                eval_unit_id = eval_unit_input[0].get_attribute('value') if eval_unit_input else 'N/A'
                                            except:
                                                form_action = ''
                                                eval_unit_id = 'N/A'
                                            
                                            print(f"🎯 Submit button found:")
                                            print(f"    Form action: {form_action}")
                                            print(f"    EvalUnitId: {eval_unit_id}")
                                            print(f"    Parent context: {parent_text[:100]}...")
                                            
                                            # Check if this button is related to our lot number
                                            if (lot_number in parent_text or 
                                                'resultat' in form_action or 
                                                eval_unit_id != 'N/A'):
                                                
                                                print(f"✅ CLICKING property-related submit button!")
                                                print(f"    🎯 Target: EvalUnitId={eval_unit_id}, Action={form_action}")
                                                
                                                # Scroll to button to ensure it's clickable
                                                driver.execute_script("arguments[0].scrollIntoView(true);", button)
                                                time.sleep(1)
                                                
                                                # Click the button
                                                button.click()
                                                property_clicked = True
                                                
                                                # Wait for navigation and check result
                                                time.sleep(5)
                                                new_url = driver.current_url
                                                print(f"📄 After clicking submit button - URL: {new_url}")
                                                
                                                # Verify we navigated to the property detail page
                                                if ('resultat' in new_url or 
                                                    new_url != 'https://montreal.ca/role-evaluation-fonciere/lot-renove/liste'):
                                                    print(f"🎉 SUCCESS! Navigated to property detail page!")
                                                    
                                                    # Look for "Aire d'etage" (building area) on the detail page
                                                    try:
                                                        time.sleep(3)  # Wait for page to fully load
                                                        page_text = driver.find_element(By.TAG_NAME, "body").text
                                                        if "aire d'etage" in page_text.lower() or "aire d'étage" in page_text.lower():
                                                            print(f"🏗️ FOUND 'Aire d'étage' on property detail page!")
                                                        else:
                                                            print(f"⚠️ 'Aire d'étage' not found, but we're on the detail page")
                                                            print(f"📄 Page content preview: {page_text[:200]}...")
                                                    except Exception as e:
                                                        print(f"❌ Error checking for Aire d'étage: {e}")
                                                    
                                                    break
                                                else:
                                                    print(f"⚠️ URL didn't change as expected, continuing search...")
                                                    property_clicked = False
                                    
                                    except Exception as e:
                                        print(f"   ❌ Error clicking submit button: {e}")
                                        continue
                                
                                if property_clicked:
                                    break
                                    
                            except Exception as e:
                                print(f"❌ Error with pattern {pattern}: {e}")
                                continue
                        
                        if property_clicked:
                            break
                        
                        # Wait before next attempt
                        if attempt < max_attempts:
                            print(f"⏳ Waiting before next attempt...")
                            time.sleep(2)
                
                # Wait for results page to fully load
                print("⏳ Waiting for Montreal property detail page to load...")
                time.sleep(5)  # Wait longer for dynamic content
                
                # DEBUG: Print the property detail page info
                print(f"📄 Property detail page title: {driver.title}")
                print(f"📄 Property detail page URL: {driver.current_url}")
                
                if property_clicked:
                    print("✅ Successfully clicked on property, now on detail page")
                else:
                    print("⚠️ No property was clicked, extracting from search results page")
                
                # Look for tables, divs, or other structured content
                tables = driver.find_elements(By.TAG_NAME, "table")
                divs = driver.find_elements(By.CSS_SELECTOR, "div[class*='result'], div[class*='property'], div[class*='info']")
                
                print(f"🔍 Found {len(tables)} tables and {len(divs)} result divs")
                
                # Print table content if found
                if tables:
                    for i, table in enumerate(tables[:3]):  # Check first 3 tables
                        print(f"📊 Table {i} content:")
                        try:
                            rows = table.find_elements(By.TAG_NAME, "tr")
                            for j, row in enumerate(rows[:10]):  # First 10 rows
                                cells = row.find_elements(By.TAG_NAME, "td")
                                if cells:
                                    row_text = " | ".join([cell.text.strip() for cell in cells if cell.text.strip()])
                                    if row_text:
                                        print(f"    Row {j}: {row_text}")
                        except:
                            pass
                
                # Print div content if found
                if divs:
                    for i, div in enumerate(divs[:5]):  # Check first 5 divs
                        print(f"📄 Div {i} content: {div.text.strip()[:200]}")
                
                # Also try to find any text containing the lot number
                lot_text_elements = driver.find_elements(By.XPATH, f"//*[contains(text(), '{lot_number}')]")
                print(f"🔍 Found {len(lot_text_elements)} elements containing lot number {lot_number}")
                for i, element in enumerate(lot_text_elements[:5]):
                    try:
                        print(f"  Lot element {i}: {element.text.strip()}")
                        # Try to get parent or sibling elements for more context
                        parent = element.find_element(By.XPATH, "..")
                        print(f"    Parent context: {parent.text.strip()[:100]}")
                    except:
                        pass
                
                # Extract Montreal property data with improved structured parsing
                structured_data = self._extract_montreal_structured_data(driver, lot_number)
                
                if structured_data:
                    print(f"✅ Montreal structured data extracted for lot {lot_number}")
                    return structured_data
                else:
                    # Fallback to old method
                    property_data = {
                        'lot_number': lot_number,
                        'municipality': municipality,
                        'address': self._extract_montreal_field(driver, ['address', 'adresse']),
                        'owner_name': self._extract_montreal_field(driver, ['owner', 'propriétaire', 'titulaire']),
                        'year_of_construction': self._extract_montreal_field(driver, ['construction', 'année', 'built']),
                        'total_building_sf': self._extract_montreal_field(driver, ['building', 'bâtiment', 'superficie']),
                        'land_sf': self._extract_montreal_field(driver, ['terrain', 'land', 'lot']),
                        'tax_assessment': self._extract_montreal_field(driver, ['évaluation', 'assessment', 'valeur']),
                        'property_type': self._extract_montreal_field(driver, ['type', 'usage', 'utilisation']),
                    }
                    print(f"✅ Montreal fallback data extracted for lot {lot_number}")
                    return property_data
            else:
                print(f"⚠️ Could not find lot input field on Montreal site")
                return {'error': 'Input field not found', 'lot_number': lot_number, 'municipality': municipality}
                
        except Exception as e:
            print(f"❌ Error scraping Montreal evaluation: {e}")
            return {'error': str(e), 'lot_number': lot_number, 'municipality': municipality}
    
    def format_for_excel(self, raw_data):
        """Format scraped data for Excel property sheet"""
        excel_mapping = {
            'Address': raw_data.get('address', ''),
            'Google Maps Link': f"https://maps.google.com/maps?q={raw_data.get('address', '')}" if raw_data.get('address') else '',
            'Lot Number': raw_data.get('lot_number', ''),
            'Borough': raw_data.get('municipality', ''),
            'Year of construction': raw_data.get('year_of_construction', ''),
            'Total Building SF': raw_data.get('total_building_sf', ''),
            'Google Maps Building SF': raw_data.get('total_building_sf', ''),  # Use same value
            'Land SF': raw_data.get('land_sf', ''),
            'Ceiling Height': '',  # Not available in evaluation records
            'Docks - google or vendor?': '',  # Not available in evaluation records
            'Column Distance': '',  # Not available in evaluation records
            'Amps': '',  # Not available in evaluation records
            'Owner Name': raw_data.get('owner_name', ''),
            'Tax Assessment': raw_data.get('tax_assessment', ''),
            'Property Type': raw_data.get('property_type', ''),
            'Zoning': '',  # Quebec uses different zoning system
            # Additional Quebec-specific fields
            'Account Number': raw_data.get('account_number', ''),
            'Matricule': raw_data.get('matricule', ''),
        }
        
        return excel_mapping

def scrape_montreal_botasaurus(lot_number, headless=True):
    """
    Montreal-specific scraper using real botasaurus implementation
    Direct import approach with proper error handling
    """
    try:
        print(f"Starting Montreal scraping for lot {lot_number}")
        
        # Import the real Montreal scraper
        try:
            import montreal_real_scraper
            print("✅ Successfully imported montreal_real_scraper")
            
            # Call the real scraper function with headless parameter
            result = montreal_real_scraper.scrape_montreal_property_botasaurus(lot_number, headless=headless)
            
            if result and result.get('extraction_success'):
                print(f"✅ Montreal scraping successful for lot {lot_number}")
                return result
            else:
                print(f"⚠️ Montreal scraping returned empty result for lot {lot_number}")
                return create_montreal_fallback_data(lot_number)
                
        except ImportError as import_error:
            print(f"❌ Failed to import montreal_real_scraper: {import_error}")
            return create_montreal_fallback_data(lot_number)
        except Exception as scraper_error:
            print(f"⚠️ Montreal scraper error: {scraper_error}")
            return create_montreal_fallback_data(lot_number)
        
    except Exception as e:
        print(f"❌ Critical error in Montreal scraping: {e}")
        return create_montreal_fallback_data(lot_number)

def create_montreal_fallback_data(lot_number):
    """Create fallback data when Montreal scraping fails"""
    return {
        'Address': f'Property {lot_number}',
        'Borough': 'montreal',
        'Lot Number': str(lot_number),
        'Matricule': f'{lot_number}-0000-0000',
        'Owner Name': 'Data not available',
        'Land SF': '0',
        'Year of Construction': 'Unknown',
        'Total Building SF': '0',
        'Property Type': 'residential',
        'Land Value': '0',
        'Building Value': '0',
        'Total Value': '0',
        'extraction_source': 'montreal_fallback',
        'extraction_success': False,
        'lot_number': str(lot_number),
        'error': 'Scraping failed - fallback data provided'
    }

def scrape_property_simple(lot_number, municipality, use_aws=True, use_mock=False, headless=True):
    """Simple function for Flask integration"""
    
    if use_mock:
        # Mock data for testing the integration
        print(f"🔍 Mock scraping for lot {lot_number} in {municipality}")
        
        mock_data = {
            'lot_number': lot_number,
            'municipality': municipality,
            'address': f"123 Main Street, {municipality}, QC",
            'owner_name': f"Property Owner {lot_number[-3:]}",
            'year_of_construction': "1995",
            'total_building_sf': "2,500",
            'land_sf': "5,000",
            'tax_assessment': "$450,000",
            'property_type': "Residential"
        }
        
        scraper = QuebecPropertyScraperAPI()
        excel_mapping = scraper.format_for_excel(mock_data)
        
        print(f"✅ Mock data generated for lot {lot_number}")
        return excel_mapping
    else:
        # Check if this is Montreal - use our new Botasaurus scraper
        if 'montreal' in municipality.lower():
            print(f"🏙️ Using Montreal Botasaurus scraper for lot {lot_number}")
            try:
                result = scrape_montreal_botasaurus(lot_number, headless=headless)
                if 'error' in result:
                    print(f"❌ Montreal scraping failed: {result['error']}")
                    return {'error': result['error']}
                else:
                    print(f"✅ Montreal scraping successful!")
                    return result
            except Exception as e:
                print(f"❌ Montreal scraper error: {e}")
                return {'error': f"Montreal scraper error: {e}"}
        else:
            # For other cities, use the existing scraper
            print(f"🚀 Using traditional Quebec scraper for {municipality}")
            scraper = QuebecPropertyScraperAPI()
            raw_data = scraper.scrape_property_data(lot_number, municipality, use_aws)
            return scraper.format_for_excel(raw_data)

# CLI interface for testing
if __name__ == "__main__":
    if len(sys.argv) >= 3:
        lot = sys.argv[1]
        municipality = sys.argv[2]
        use_aws = len(sys.argv) <= 3 or sys.argv[3].lower() != 'false'  # Default to True
        
        print(f"🚀 Starting Quebec property scrape for Lot {lot} in {municipality}")
        print(f"🔧 Using AWS VPN rotation: {use_aws}")
        result = scrape_property_simple(lot, municipality, use_aws)
        
        print("📋 Results:")
        for key, value in result.items():
            if value:
                print(f"  {key}: {value}")
    else:
        print("Usage: python property_scraper.py <lot_number> <municipality> [use_aws]")
        print("Example: python property_scraper.py 5492324 Laval")
        print("Note: AWS VPN rotation is enabled by default")