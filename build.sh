#!/bin/bash
set -e

echo "🚀 Starting MAHSR-T3-DPR Streamlit Service on Render..."

# -----------------------------------------------------------------
# 1. Clean old Streamlit cache and static JS bundles
# -----------------------------------------------------------------
echo "🧹 Clearing Streamlit cache and static files..."
rm -rf ~/.streamlit/static
streamlit cache clear || true

# -----------------------------------------------------------------
# 2. Ensure correct environment and dependencies
# -----------------------------------------------------------------
echo "📦 Installing dependencies..."
pip install --upgrade pip wheel setuptools
pip install -r requirements.txt

# -----------------------------------------------------------------
# 3. Start Streamlit app
# -----------------------------------------------------------------
echo "🌐 Launching MAHSR-T3-DPR app..."
streamlit run app.py --server.port=$PORT --server.address=0.0.0.0 --server.enableXsrfProtection=false --server.enableCORS=false
