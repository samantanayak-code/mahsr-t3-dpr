#!/bin/bash
echo "Starting MAHSR-T3-DPR-App (Streamlit)..."
source venv/bin/activate
streamlit run app.py --server.port=8501 --server.address=0.0.0.0 --server.headless=true
