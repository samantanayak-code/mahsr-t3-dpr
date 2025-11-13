#!/bin/bash
set -e

echo "🚀 Starting MAHSR-T3-DPR Streamlit Service on Render..."

# -----------------------------------------------------------------
# INSTALL DEPENDENCIES FIRST
# -----------------------------------------------------------------
echo "📦 Installing dependencies..."
pip install --upgrade pip wheel setuptools
pip install -r requirements.txt

# -----------------------------------------------------------------
# NOW clean Streamlit cache (AFTER streamlit is installed!)
# -----------------------------------------------------------------
echo "🧹 Clearing Streamlit cache and static files..."
rm -rf ~/.streamlit/static
streamlit cache clear || true

# -----------------------------------------------------------------
# START APP
# -----------------------------------------------------------------
echo "🌐 Launching MAHSR-T3-DPR app..."
exec streamlit run app.py --server.port=$PORT --server.address=0.0.0.0 \
    --server.enableXsrfProtection=false --server.enableCORS=false



