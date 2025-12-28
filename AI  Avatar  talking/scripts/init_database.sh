#!/bin/bash
# Database initialization script for Docker container

echo "========================================="
echo "AI Avatar Studio - Database Setup"
echo "========================================="

# Check if database file exists
DB_PATH="${DATABASE_PATH:-/app/data/database/projects.db}"
echo "Database path: $DB_PATH"

# Create directories if they don't exist
mkdir -p "$(dirname "$DB_PATH")"
mkdir -p /app/data/cache
mkdir -p /app/data/logs
mkdir -p /app/output/videos
mkdir -p /app/output/thumbnails

if [ -f "$DB_PATH" ]; then
    echo "✓ Database already exists"
    
    # Check database integrity
    echo "Checking database integrity..."
    sqlite3 "$DB_PATH" "PRAGMA integrity_check;" > /tmp/db_check.txt
    if grep -q "ok" /tmp/db_check.txt; then
        echo "✓ Database integrity check passed"
    else
        echo "⚠ Database integrity check failed!"
        cat /tmp/db_check.txt
    fi
    
    # Show database statistics
    echo ""
    echo "Database Statistics:"
    sqlite3 "$DB_PATH" "SELECT 
        (SELECT COUNT(*) FROM projects) as total_projects,
        (SELECT COUNT(*) FROM generations) as total_generations,
        (SELECT COUNT(*) FROM generations WHERE status='completed') as completed,
        (SELECT COUNT(*) FROM generations WHERE status='failed') as failed;"
else
    echo "→ Creating new database..."
    
    # Initialize database using Python
    python3 <<EOF
from utils.database import DatabaseManager
import os

db_path = os.getenv('DATABASE_PATH', '/app/data/database/projects.db')
db = DatabaseManager(db_path)
print(f"✓ Database initialized at: {db_path}")

# Set default preferences
db.set_preference('theme', 'dark')
db.set_preference('auto_save', 'true')
db.set_preference('show_console', 'true')
print("✓ Default preferences set")
EOF
fi

# Set permissions
chmod -R 755 /app/data
chmod 644 "$DB_PATH" 2>/dev/null || true

echo ""
echo "✓ Database setup complete!"
echo "========================================="
