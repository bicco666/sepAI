#!/bin/bash

# Sync index.html script
# Creates a copy of index.html as index_alt.html

set -e

echo "Syncing index.html to index_alt.html..."

# Check if index.html exists
if [ ! -f "./frontend/index.html" ]; then
    echo "Error: ./frontend/index.html not found"
    exit 1
fi

# Copy index.html to index_alt.html
cp "./frontend/index.html" "./frontend/index_alt.html"

echo "✅ index.html synced to index_alt.html"
echo "Both files are now identical"