#!/bin/bash

echo "🔍 Diagnosing People Counter Backend Issues..."

echo "📊 Checking running processes..."
echo "Next.js processes:"
ps aux | grep next | grep -v grep

echo ""
echo "Python processes:"
ps aux | grep python | grep -v grep

echo ""
echo "Port 3000 usage:"
lsof -i :3000

echo ""
echo "Database status:"
pg_isready -h localhost -p 5432

echo ""
echo "🔧 Potential Solutions:"
echo "1. If people-counter is running on port 3000, stop it first"
echo "2. Run people-counter on a different port (e.g., 8000)"
echo "3. Check people-counter database connection"
echo "4. Ensure people-counter doesn't interfere with Next.js API endpoints"

echo ""
echo "💡 Recommended approach:"
echo "1. Stop any people-counter processes"
echo "2. Run people-counter on port 8000: python run_demo.py --port 8000"
echo "3. Keep Next.js on port 3000 for frontend"
echo "4. Configure people-counter to use different API endpoints if needed"
