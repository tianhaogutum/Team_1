#!/bin/bash
# Test script to verify the reset database functionality

set -e

echo "================================================"
echo "Testing Database Reset Functionality"
echo "================================================"
echo ""

# Check if backend is running
echo "1. Checking if backend is running..."
if ! curl -s http://localhost:8000/docs > /dev/null 2>&1; then
    echo "❌ Backend is not running on http://localhost:8000"
    echo "Please start the backend first: cd backend && ./restart_backend.sh"
    exit 1
fi
echo "✅ Backend is running"
echo ""

# Show current profiles before deletion
echo "2. Checking current profiles in database..."
cd backend
PROFILE_COUNT=$(python3 -c "
import sqlite3
conn = sqlite3.connect('data/app.db')
cursor = conn.cursor()
cursor.execute('SELECT COUNT(*) FROM demo_profiles')
count = cursor.fetchone()[0]
print(count)
conn.close()
")
echo "Found $PROFILE_COUNT profile(s) in database"

if [ "$PROFILE_COUNT" -eq 0 ]; then
    echo "⚠️  No profiles to delete. Creating a test profile first..."
    echo ""
    
    # Create a test profile
    echo "3. Creating test profile..."
    curl -s -X POST http://localhost:8000/api/profiles \
        -H "Content-Type: application/json" \
        -d '{
            "fitness": "intermediate",
            "type": ["natural-scenery", "history-culture"],
            "narrative": "adventure"
        }' | python3 -m json.tool
    echo ""
    echo "✅ Test profile created"
    echo ""
fi

# Show profiles before deletion
echo "4. Profiles before deletion:"
python3 -c "
import sqlite3
import json
conn = sqlite3.connect('data/app.db')
cursor = conn.cursor()
cursor.execute('SELECT id, total_xp, level FROM demo_profiles ORDER BY id')
rows = cursor.fetchall()
for row in rows:
    print(f'  - Profile ID: {row[0]}, XP: {row[1]}, Level: {row[2]}')
conn.close()
"
echo ""

# Call the DELETE /api/profiles endpoint
echo "5. Calling DELETE /api/profiles (delete all profiles)..."
RESPONSE=$(curl -s -X DELETE http://localhost:8000/api/profiles)
echo "Response: $RESPONSE" | python3 -m json.tool
echo ""

# Verify deletion
echo "6. Verifying deletion..."
NEW_COUNT=$(python3 -c "
import sqlite3
conn = sqlite3.connect('data/app.db')
cursor = conn.cursor()
cursor.execute('SELECT COUNT(*) FROM demo_profiles')
count = cursor.fetchone()[0]
print(count)
conn.close()
")

if [ "$NEW_COUNT" -eq 0 ]; then
    echo "✅ SUCCESS: All profiles deleted from database"
else
    echo "❌ FAILURE: $NEW_COUNT profile(s) still remain in database"
    exit 1
fi

echo ""
echo "================================================"
echo "✅ All tests passed!"
echo "================================================"

