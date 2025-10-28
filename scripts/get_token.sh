#!/bin/bash

# Helper script to get Firebase Token
# This script makes it easier to get your authentication token

echo "🔑 Firebase Token Helper"
echo "========================"
echo ""
echo "This script will show you how to get your Firebase token."
echo ""

# Check if user wants to see instructions
echo "Choose a method:"
echo "1. Browser Console (Easiest)"
echo "2. Browser Network Tab"
echo "3. Show all methods"
echo ""

read -p "Enter your choice (1-3): " choice

case $choice in
  1)
    echo ""
    echo "📋 Browser Console Method:"
    echo "=========================="
    echo ""
    echo "1. Open: http://localhost:3000"
    echo "2. Login with your credentials"
    echo "3. Press F12 (or Cmd+Option+I on Mac)"
    echo "4. Go to Console tab"
    echo "5. Copy and paste this:"
    echo ""
    echo "firebase.auth().currentUser.getIdToken().then(token => console.log(token));"
    echo ""
    echo "6. Copy the token that appears"
    echo ""
    ;;
    
  2)
    echo ""
    echo "🌐 Network Tab Method:"
    echo "======================"
    echo ""
    echo "1. Open: http://localhost:3000"
    echo "2. Login"
    echo "3. Press F12 → Network tab"
    echo "4. Make any request (upload a file)"
    echo "5. Find the request, click it"
    echo "6. Go to 'Headers' section"
    echo "7. Look for 'Authorization: Bearer ...'"
    echo "8. Copy the token"
    echo ""
    ;;
    
  3)
    echo ""
    echo "📋 Browser Console Method (Recommended):"
    echo "========================================"
    echo "1. Open browser console (F12)"
    echo "2. Run: firebase.auth().currentUser.getIdToken().then(token => console.log(token));"
    echo ""
    
    echo "🌐 Network Tab Method:"
    echo "======================"
    echo "1. Check network requests in DevTools"
    echo "2. Find Authorization header"
    echo ""
    
    echo "💡 Quick Copy Script:"
    echo "===================="
    echo "Copy this to browser console:"
    echo ""
    cat << 'EOF'
firebase.auth().currentUser.getIdToken().then(token => {
  console.log('\n🔥 Your Firebase Token:\n');
  console.log(token);
  console.log('\n');
  // If in Chrome/Edge, copy to clipboard:
  if (navigator.clipboard) {
    navigator.clipboard.writeText(token).then(() => {
      console.log('✅ Token copied to clipboard!');
    });
  }
});
EOF
    echo ""
    ;;
esac

echo ""
echo "💡 Once you have the token, you can use it like this:"
echo ""
echo "export FIREBASE_TOKEN='your-token-here'"
echo "curl -H \"Authorization: Bearer \$FIREBASE_TOKEN\" http://localhost:8000/api/..."
echo ""




