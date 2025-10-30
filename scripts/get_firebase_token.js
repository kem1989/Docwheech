/**
 * Helper script to get Firebase Authentication Token
 * 
 * Usage:
 *   node scripts/get_firebase_token.js
 */

const readline = require('readline');

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

console.log('🔑 Firebase Token Helper\n');
console.log('This script will help you get your Firebase token.\n');
console.log('Options:');
console.log('1. Show instructions for browser console');
console.log('2. Show how to extract from network requests');
console.log('3. Exit\n');

rl.question('Choose an option (1-3): ', (choice) => {
  switch(choice) {
    case '1':
      showBrowserConsoleInstructions();
      break;
    case '2':
      showNetworkInstructions();
      break;
    case '3':
      console.log('\nGoodbye!');
      rl.close();
      break;
    default:
      console.log('\nInvalid option. Please choose 1-3.');
      rl.close();
  }
});

function showBrowserConsoleInstructions() {
  console.log('\n📋 Browser Console Method:\n');
  console.log('1. Open your browser: http://localhost:3000');
  console.log('2. Login with your credentials');
  console.log('3. Open Developer Console (F12 or Cmd+Option+I on Mac)');
  console.log('4. Go to the Console tab');
  console.log('5. Copy and paste this command:\n');
  console.log('```javascript');
  console.log('firebase.auth().currentUser.getIdToken().then(token => {');
  console.log('  console.log("Firebase Token:", token);');
  console.log('  copy(token);  // Copies to clipboard (Chrome/Edge only)');
  console.log('});');
  console.log('```\n');
  console.log('6. Copy the token that appears');
  console.log('7. Use this token in your API calls!\n');
  rl.close();
}

function showNetworkInstructions() {
  console.log('\n🌐 Network Tab Method:\n');
  console.log('1. Open your browser: http://localhost:3000');
  console.log('2. Login with your credentials');
  console.log('3. Open Developer Tools (F12)');
  console.log('4. Go to the Network tab');
  console.log('5. Make any API request (e.g., upload a file)');
  console.log('6. Find the request in the list');
  console.log('7. Click on it to see details');
  console.log('8. Go to "Headers" section');
  console.log('9. Look for "Authorization: Bearer ..."');
  console.log('10. Copy the token after "Bearer "\n');
  console.log('💡 Tip: You can also check the browser\'s Application/Local Storage\n');
  rl.close();
}





