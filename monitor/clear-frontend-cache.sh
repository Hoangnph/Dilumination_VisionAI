#!/bin/bash

echo "🧹 Clearing Frontend Cache and Restarting..."

echo "📱 Clearing Next.js cache..."
rm -rf .next
rm -rf node_modules/.cache

echo "🌐 Clearing browser cache instructions:"
echo "1. Open browser DevTools (F12)"
echo "2. Right-click on refresh button"
echo "3. Select 'Empty Cache and Hard Reload'"
echo "4. Or use Ctrl+Shift+R (Cmd+Shift+R on Mac)"

echo "🔄 Restarting development server..."
pkill -f "next dev" || true
sleep 2

echo "🚀 Starting fresh development server..."
npm run dev &

echo "✅ Frontend cache cleared and server restarted!"
echo "📝 Please refresh your browser with hard reload (Ctrl+Shift+R)"
