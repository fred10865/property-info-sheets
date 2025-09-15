# Property Info Sheets Web App - Knowledge Base

**Last Updated**: September 14, 2025  
**Repository**: https://github.com/fred10865/property-info-sheets  
**Live URL**: https://property-info-sheets-production.up.railway.app  

## 🎯 PROJECT OVERVIEW

**Primary Goal**: Convert Excel workbook 'Info Sheet.xlsx' into a browser-based editor that matches the Excel layout EXACTLY, with multi-property support and cloud deployment.

**Key Requirements**:
- Non-technical browser interface with tabs matching Excel layout
- Edit values and save back to Excel with timestamped backups
- Multi-property support (each property = separate .xlsx file)
- CRM integration URLs for external linking
- Public cloud deployment (not localhost)
- EXACT visual match to Excel screenshot layout

## 🏗️ ARCHITECTURE DECISIONS

### Technology Stack Evolution
1. **Streamlit** (Initial) → UI mismatch issues
2. **H2O Wave** (Intermediate) → ASGI deployment complications  
3. **Flask** (Final) → Better HTML/CSS control, easier deployment

### Final Tech Stack
- **Flask**: Web framework for precise UI control
- **pandas + openpyxl**: Excel I/O operations
- **Railway**: Cloud hosting platform
- **GitHub**: Source control with auto-deployment
- **HTML/CSS**: Custom templates for exact Excel layout matching

## 🗂️ FILE STRUCTURE

```
Info Sheet/
├── flask_app.py              # Main Flask application
├── requirements.txt          # Dependencies (pinned versions)
├── start.sh                  # Unix deployment script
├── Procfile                  # Railway/Heroku deployment
├── .gitignore               # Excludes backups, local files
├── README.md                # Deployment instructions
├── LICENSE                  # Apache 2.0
├── PROJECT_KNOWLEDGE_BASE.md # This file
├── backups/                 # Auto-generated timestamped backups
├── Info Sheet.xlsx          # Main property file
├── Sample_Property.xlsx     # Demo data
└── templates/
    └── property_form.html   # Custom HTML template
```

## 🔧 CRITICAL TECHNICAL KNOWLEDGE

### Data Extraction Logic - CRITICAL BUG FIXED

**⚠️ MOST IMPORTANT LESSON**: Always use `if` statements (NOT `elif`) for section parsing!

**The Bug**: Using `elif` caused sections to be skipped once one matched
**The Fix**: Changed all `elif` to `if` in `load_property_data()` function

```python
# ❌ WRONG - Causes missing fields
if condition1:
    # process section 1
elif condition2:  # This gets skipped if condition1 was true!
    # process section 2

# ✅ CORRECT - All sections processed
if condition1:
    # process section 1  
if condition2:    # This always gets checked
    # process section 2
```

### Excel Layout Mapping (Zero-indexed)

**Owner Information**: Rows 1-4, Columns E-F (4, 5)
**Property Information**: Rows 6-11, Columns A-B (0, 1)  
**Title Information**: Rows 6-11, Columns E-F (4, 5)
**Important Info**: Rows 13-18, Columns E-F (4, 5)
**Building Breakdown**: Rows 16-21, Columns A-B (0, 1)
**Our Offer vs Vendor's Asking**: Rows 23-28, Columns A-C (0, 1, 2)
**Income**: Rows 30-37, Columns A-B (0, 1)
**Questions**: Row 29+, Columns E-F (4, 5)

### Multi-Property Detection
- Each property = separate `.xlsx` file in root directory
- Auto-detected by scanning for `*.xlsx` files
- Property ID = filename without extension
- URL structure: `/property/{property_id}`

## 🚀 DEPLOYMENT KNOWLEDGE

### Railway Deployment
1. **GitHub Integration**: Auto-deploys on push to `main` branch
2. **Environment**: Automatically detects Python, uses `requirements.txt`
3. **Start Command**: Defined in `Procfile` - `web: python flask_app.py`
4. **Port Binding**: App binds to `0.0.0.0:$PORT` (Railway provides PORT env var)

### Critical Deployment Files
- `requirements.txt`: Pinned versions prevent build failures
- `Procfile`: Tells Railway how to start the app
- `start.sh`: Backup script for Unix-based deployments
- `.gitignore`: Excludes backups/ and local files

### Build Process
1. Push to GitHub triggers Railway build
2. Railway installs dependencies from `requirements.txt`
3. Railway runs command from `Procfile`
4. App becomes available on public URL

## 💾 DATA MANAGEMENT

### Excel Backup System
- **Location**: `backups/` directory
- **Format**: `{property_id}_{YYYYMMDD_HHMMSS}.xlsx`
- **Trigger**: Every save operation creates backup before writing
- **Auto-creation**: Directory created if doesn't exist

### Form Data Processing
- Form fields map to Excel cells via exact field name matching
- Vendor asking values stored in column C (for Our Offer section)
- All other data in column B
- Preserves existing Excel formatting and structure

## 🐛 DEBUGGING HISTORY

### Major Issues Solved

1. **Missing Owner Info/Building Breakdown** (CRITICAL)
   - **Cause**: `elif` statements preventing multiple section processing
   - **Solution**: Changed to `if` statements
   - **Test**: `load_property_data()` now returns 4 owner_info fields, 5 building_breakdown fields

2. **UI Layout Mismatch**
   - **Cause**: Generic form generation
   - **Solution**: Custom HTML template with exact Excel section structure

3. **Deployment Failures**
   - **Cause**: Unpinned dependencies, wrong start commands
   - **Solution**: Pinned `requirements.txt`, proper `Procfile`

### Testing Commands for Verification
```bash
# Check field extraction counts
python -c "from flask_app import load_property_data; data = load_property_data('Info Sheet'); print('Owner Info fields:', len(data.get('owner_info', []))); print('Building Breakdown fields:', len(data.get('building_breakdown', [])))"

# Expected Output:
# Owner Info fields: 4
# Building Breakdown fields: 5
```

## 🔗 INTEGRATION FEATURES

### CRM URL Generation
- Pattern: `https://your-crm.com/property/{property_id}`
- Enables external systems to link directly to specific properties
- Property ID extracted from Excel filename

### Multi-Property Navigation
- Main landing page lists all available properties
- Click property name to edit that specific property
- Breadcrumb navigation back to property list

## 📋 DEVELOPMENT WORKFLOW

### Local Development
1. `cd "C:\Users\Administrator\Desktop\Programs\Info Sheet"`
2. `python flask_app.py`
3. Open `http://127.0.0.1:8000`
4. Test all sections have fields present

### Deployment Workflow  
1. Make changes locally
2. `git add .`
3. `git commit -m "descriptive message"`
4. `git push origin main`
5. Railway auto-deploys in ~2 minutes
6. Verify at production URL

### Critical Testing Checklist
- [ ] Owner Information section shows 4 fields
- [ ] Building Breakdown section shows 5 fields  
- [ ] All Excel sections present in web UI
- [ ] Save functionality creates backups
- [ ] Multi-property navigation works
- [ ] Production deployment successful

## 🚨 CRITICAL REMINDERS

1. **NEVER use `elif` for section parsing** - Always use `if`
2. **Always test field counts** after data extraction changes
3. **Pin all versions** in `requirements.txt` for stable deployments
4. **Create backups** before any Excel modifications
5. **Test locally** before pushing to production
6. **Use PowerShell syntax** for Windows terminal commands (`;` not `&&`)

## 📞 USER REQUIREMENTS EVOLUTION

**Original**: "Create a small VS Code project that turns the attached Excel workbook 'Info Sheet.xlsx' into a non-technical, browser-based editor with tabs."

**Final**: "LOOK AT THIS SCREENSHOT COPY IT EXACTLY, RUN TESTS TO VERIFY YOURSELF."

**Key Evolution Points**:
- Single property → Multi-property support
- Local only → Public cloud deployment  
- Generic layout → Exact Excel screenshot match
- Basic functionality → CRM integration ready
- Manual testing → Automated verification

## 🎯 SUCCESS METRICS

**✅ Achieved**:
- Exact Excel layout reproduction
- All sections and fields present (Owner Info: 4 fields, Building Breakdown: 5 fields)
- Multi-property support with auto-detection
- Public cloud deployment on Railway
- Automatic backups on save
- CRM-ready URL structure

**📊 Performance**:
- Local startup: ~2 seconds
- Cloud deployment: ~2 minutes
- Excel load time: <1 second per file
- Backup creation: <500ms

---

*This knowledge base should be referenced for ALL future development on this project to avoid repeating solved issues and maintain the exact requirements that were hard-won through iteration.*