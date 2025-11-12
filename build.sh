#!/bin/bash
set -e
echo "🚀 Starting MAHSR-T3-DPR Streamlit service..."
rm -rf ~/.streamlit/static
streamlit cache clear || true
streamlit run app.py --server.port=$PORT --server.address=0.0.0.0 --server.enableXsrfProtection=false

