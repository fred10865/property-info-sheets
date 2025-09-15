#!/bin/bash
# Download and start H2O Wave server
wget -O waved.tar.gz https://github.com/h2oai/wave/releases/download/v1.7.4/wave-1.7.4-linux-amd64.tar.gz
tar -xzf waved.tar.gz
cd wave-1.7.4-linux-amd64
chmod +x waved
./waved &
cd ..
sleep 5
#!/bin/bash
# Production start script - works with Railway, Render, Heroku

# Set environment variables
export PYTHONPATH="${PYTHONPATH}:."
export PORT=${PORT:-8000}

# Create required directories
mkdir -p backups
mkdir -p properties

# Start the application
echo "Starting Property Info Sheet App on port $PORT..."
python production_wave.py