#!/bin/bash

# Portfolio Backend Cleanup Script
# Removes temporary files, cache, and logs

echo "🧹 Starting cleanup..."

# Remove Python cache files
echo "🐍 Removing Python cache files..."
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true

# Remove log files
echo "📋 Removing log files..."
rm -f *.log
rm -f logs/*.log 2>/dev/null || true

# Remove temporary files
echo "🗑️ Removing temporary files..."
rm -f *.tmp
rm -f *.temp
rm -f debug_*.py
rm -f setup_*.py

# Remove cache directories
echo "💾 Removing cache directories..."
rm -rf .cache/ 2>/dev/null || true
rm -rf .pytest_cache/ 2>/dev/null || true

echo "✅ Cleanup completed!"
echo "📊 Current directory size:"
du -sh . 2>/dev/null || echo "Directory size check failed"