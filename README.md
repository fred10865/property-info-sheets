# Property Info Sheet Web App

## 🚀 Quick Deployment Options

### Option 1: Railway (Recommended - Free)
1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub
3. Click "Deploy from GitHub repo"
4. Connect this repository
5. Railway will auto-deploy
6. Get your public URL: `https://yourapp.railway.app`

### Option 2: Render (Free tier available)
1. Go to [render.com](https://render.com)
2. Connect your GitHub account
3. Create new "Web Service"
4. Connect this repository
5. Use these settings:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `bash start.sh`
6. Get your URL: `https://yourapp.onrender.com`

### Option 3: Heroku (Paid)
1. Install Heroku CLI
2. Run commands:
   ```bash
   heroku create your-app-name
   git push heroku main
   ```
3. Get URL: `https://your-app-name.herokuapp.com`

## 📋 CRM Integration

Once deployed, you'll get URLs like:
- Main page: `https://yourapp.domain.com/properties`
- Property pages: `https://yourapp.domain.com/property/Property_Name`

### How to use in your CRM:
1. For each property in your CRM, add a custom field
2. Put the direct property URL in that field
3. Click the link to instantly access the property info sheet

## 📁 Adding New Properties

1. Create new Excel files with property data
2. Upload them to your deployment
3. They'll automatically appear with their own URLs

## 🔧 Local Development

```bash
# Start Wave server
./wave-1.7.4-windows-amd64/waved.exe

# Start app
python production_wave.py
```

## 📞 Support

The app automatically creates backups when saving and handles multiple properties simultaneously.