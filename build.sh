#!/bin/bash
set -e

echo "🚀 Starting MAHSR-T3-DPR Streamlit Service on Render..."

# Install dependencies
echo "📦 Installing dependencies..."
pip install --upgrade pip wheel setuptools
pip install -r requirements.txt

# Clear Streamlit cache AFTER installing Streamlit
echo "🧹 Clearing Streamlit cache and static files..."
rm -rf ~/.streamlit/static
streamlit cache clear || true

# Launch app
echo "🌐 Launching MAHSR-T3-DPR app..."
exec streamlit run app.py --server.port=$PORT --server.address=0.0.0.0 \
    --server.enableXsrfProtection=false --server.enableCORS=false
