#!/bin/bash

echo "🚀 Safe People Counter Backend Startup..."

# Check if Next.js is running
if lsof -i :3000 > /dev/null 2>&1; then
    echo "✅ Next.js server is running on port 3000"
else
    echo "❌ Next.js server is not running on port 3000"
    echo "Please start Next.js server first: npm run dev"
    exit 1
fi

# Check if port 8000 is available
if lsof -i :8000 > /dev/null 2>&1; then
    echo "❌ Port 8000 is already in use"
    echo "Please stop the process using port 8000 or use a different port"
    exit 1
else
    echo "✅ Port 8000 is available"
fi

# Check database connection
if pg_isready -h localhost -p 5432 > /dev/null 2>&1; then
    echo "✅ Database is accessible"
else
    echo "❌ Database is not accessible"
    echo "Please check PostgreSQL service"
    exit 1
fi

echo ""
echo "🎯 Starting People Counter Backend on port 8000..."
echo "This will run independently from Next.js frontend"

# Change to people-counter directory
cd /Users/macintoshhd/Project/DIlumination/Dilumination_VisionAI/app/people-counter

# Run people-counter with specific port
echo "Running: python run_demo.py --port 8000"
python run_demo.py --port 8000
