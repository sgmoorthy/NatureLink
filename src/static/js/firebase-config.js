// Firebase configuration
const firebaseConfig = {
  apiKey: "YOUR_API_KEY",
  authDomain: "nature-link.firebaseapp.com",
  projectId: "nature-link",
  storageBucket: "nature-link.appspot.com",
  messagingSenderId: "YOUR_MESSAGING_SENDER_ID",
  appId: "YOUR_APP_ID"
};

// Initialize Firebase
firebase.initializeApp(firebaseConfig);
const auth = firebase.auth();

// Check authentication state
auth.onAuthStateChanged((user) => {
  if (!user && !window.location.pathname.includes('/login.html')) {
    window.location.href = '/static/login.html';
  }
});

// Gmail sign in function
async function signInWithGmail() {
  const provider = new firebase.auth.GoogleAuthProvider();
  try {
    const result = await auth.signInWithPopup(provider);
    if (result.user) {
      window.location.href = '/static/developer.html';
    }
  } catch (error) {
    console.error('Error signing in with Gmail:', error);
    alert('Failed to sign in with Gmail');
  }
}

// Sign out function
async function signOut() {
  try {
    await auth.signOut();
    window.location.href = '/static/login.html';
  } catch (error) {
    console.error('Error signing out:', error);
    alert('Failed to sign out');
  }
}