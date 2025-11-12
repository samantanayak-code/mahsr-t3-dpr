#!/bin/bash
# Render launch script for MAHSR-T3-DPR
set -e
echo "🚀 Starting MAHSR-T3-DPR Streamlit service..."

# Clean static and cache
rm -rf ~/.streamlit/static
streamlit cache clear || true

# Run the app
streamlit run app.py --server.port=$PORT --server.address=0.0.0.0 --server.enableXsrfProtection=false
