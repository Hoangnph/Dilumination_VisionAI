#!/bin/bash

echo "🔄 Force Refreshing Frontend State..."

echo "📱 Clearing all caches..."
rm -rf .next
rm -rf node_modules/.cache

echo "🔄 Restarting development server..."
pkill -f "next dev" || true
sleep 3

echo "🚀 Starting fresh development server..."
npm run dev &

echo "⏳ Waiting for server to start..."
sleep 10

echo "🧪 Testing API endpoints..."
echo "Sessions API:"
curl -s http://localhost:3000/api/sessions | jq '.data.total'

echo "Dashboard Stats API:"
curl -s http://localhost:3000/api/dashboard/stats | jq '.data.active_sessions'

echo "✅ Server restarted and APIs tested!"
echo "📝 Please refresh your browser with hard reload (Ctrl+Shift+R)"
echo "🎯 Frontend should now show 0 sessions"
