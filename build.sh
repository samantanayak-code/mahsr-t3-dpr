#!/bin/bash
set -euo pipefail

echo "🚀 Starting Render build (clean install)..."

# 1) Make sure pip is up-to-date
python -m pip install --upgrade pip setuptools wheel

# 2) Remove any known conflicting/old supabase related packages (if present)
pip uninstall -y supabase-py supabase_py supabase gotrue postgrest realtime storage3 || true

# 3) Force install correct supabase v2 and passlib (no pip cache)
pip install --no-cache-dir --force-reinstall supabase==2.4.0 "passlib[bcrypt]==1.7.4"

# 4) Then install everything else from requirements (no cache)
pip install --no-cache-dir -r requirements.txt

# 5) Clear possible Streamlit static cache to avoid old JS bundles
echo "🧹 Clearing Streamlit static cache..."
rm -rf ~/.streamlit/static || true
streamlit cache clear || true

# 6) Launch app (Render will run this as start command)
echo "🌐 Launching app..."
exec streamlit run app.py --server.port=$PORT --server.address=0.0.0.0 --server.enableCORS=false --server.enableXsrfProtection=false

