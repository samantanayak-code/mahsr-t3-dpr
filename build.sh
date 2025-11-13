#!/bin/bash
set -e

echo "🚀 Starting MAHSR-T3-DPR Streamlit Service on Render..."

# Clean Streamlit cache
rm -rf ~/.streamlit/static
streamlit cache clear || true

# Install dependencies
pip install --upgrade pip wheel setuptools
pip install -r requirements.txt

# Start Streamlit
exec streamlit run app.py --server.port=$PORT --server.address=0.0.0.0 --server.enableXsrfProtection=false --server.enableCORS=false


