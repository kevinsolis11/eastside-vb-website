# Eastside Volleyball Mobile App - Testing Guide

**Date:** December 24, 2025  
**Status:** ✅ Ready for Testing

## 🧪 Pre-Test Verification

### Backend Status
✅ Django server running on `http://127.0.0.1:8000/`  
✅ All 7 API endpoints created and tested  
✅ Test user created: `testplayer`  
✅ Test password: `testpass`  
✅ Test data created (player profile, stats, announcements, videos)

### API Endpoints Verified
```
1. POST   /api/login/              ✅ Working
2. POST   /api/logout/             ✅ Working
3. GET    /api/player/profile/     ✅ Working
4. GET    /api/player/stats/       ✅ Working
5. GET    /api/player/summary/     ✅ Working
6. GET    /api/announcements/      ✅ Working (2 records)
7. GET    /api/videos/             ✅ Working (2 records)
```

### Frontend Status
✅ Metro Bundler configured  
✅ All 7 screens implemented  
✅ API client fixed with Token auth format  
✅ No TypeScript errors  
✅ Ready to build

---

## 🚀 How to Start Testing

### Step 1: Open Terminal
```bash
cd "/Users/klaysolis/eastside vb website/volleyball-app"
```

### Step 2: Start the App

#### Option A: iOS (requires Xcode)
```bash
npm run ios
```
This will:
- Launch Metro Bundler
- Compile TypeScript
- Open iOS Simulator
- Install app on simulator
- Auto-reload on changes

#### Option B: Android (requires Android Studio)
```bash
npm run android
```

#### Option C: Expo Go (easiest for quick testing)
```bash
npm start
# Scan QR code with Expo Go app on your phone
```

---

## ✅ Testing Checklist

### 1. App Launch
- [ ] App opens without crashing
- [ ] Login screen appears
- [ ] No error messages

### 2. Login Flow
- [ ] Enter username: `testplayer`
- [ ] Enter password: `testpass`
- [ ] Press "Sign In"
- [ ] Loading indicator appears
- [ ] Login succeeds
- [ ] Redirects to Dashboard screen

### 3. Navigation
- [ ] Bottom tab bar visible with 4 tabs
- [ ] Dashboard tab selected by default
- [ ] Can tap Announcements tab
- [ ] Can tap Videos tab
- [ ] Can tap Account tab
- [ ] Can tap Dashboard again

### 4. Dashboard Screen
- [ ] Player profile card displays
  - [ ] Shows player name
  - [ ] Shows player number
  - [ ] Shows position
- [ ] Four stat cards visible
  - [ ] Kills stat
  - [ ] Blocks stat
  - [ ] Aces stat
  - [ ] Digs stat
- [ ] Stats values load from API

### 5. Announcements Screen
- [ ] List of announcements displays
- [ ] "Championship Game Alert" shows with red urgent indicator
- [ ] "Team Practice Tomorrow" shows as normal announcement
- [ ] Announcement titles visible
- [ ] Pull-to-refresh works

### 6. Videos Screen
- [ ] List of videos displays
- [ ] "State Championship vs Lincoln High" shows
- [ ] "Highlights - Tournament Win" shows
- [ ] Video thumbnails attempt to load
- [ ] Video duration badges visible
- [ ] Video metadata shows (opponent, type, views)
- [ ] Pull-to-refresh works

### 7. Account Screen
- [ ] User information displays
  - [ ] Username shown
  - [ ] Email shown
- [ ] "Logout" button visible
- [ ] Tap logout button
- [ ] Confirmation alert appears
- [ ] Press "OK" to confirm
- [ ] Redirects to login screen
- [ ] Token cleared from storage

### 8. Return to Login
- [ ] Login screen shows
- [ ] Fields are empty
- [ ] Can login again with same credentials
- [ ] App should NOT auto-login (token was cleared)

---

## 📊 Test Data Available

### Test User
```
Username: testplayer
Password: testpass
Email: test@example.com
```

### Player Profile
```
Name: Test Account
Number: #99
Position: Outside Hitter
```

### Player Stats
```
Kills: 0
Blocks: 0
Aces: 0
Digs: 0
```
*(These show zeroes because using test data - you can update in Django admin)*

### Announcements (2 total)
```
1. Championship Game Alert ⚠️ URGENT
   "Championship game moved to Saturday at 2 PM!"

2. Team Practice Tomorrow
   "Practice at 4:00 PM at the gym"
```

### Game Videos (2 total)
```
1. State Championship vs Lincoln High
   Full game recording (48 minutes)

2. Highlights - Tournament Win vs Central Valley
   Highlight reel (8 minutes)
```

---

## 🐛 Troubleshooting

### Metro Bundler Won't Start
```bash
# Clear cache and rebuild
rm -rf .expo node_modules/.cache
npm install
npm run ios  # or android
```

### Login Fails
1. Verify testplayer exists:
   ```bash
   cd "/Users/klaysolis/eastside vb website/volleyball_site"
   python3 manage.py shell
   >>> from django.contrib.auth.models import User
   >>> User.objects.filter(username='testplayer').exists()
   # Should return: True
   ```
2. Check Django is running: `curl http://127.0.0.1:8000/healthz/`
3. Verify API endpoint: `curl http://127.0.0.1:8000/api/login/`

### Screens Don't Load Data
1. Check token is being sent (look at Network tab in React Native debugger)
2. Verify API endpoint exists: `curl http://127.0.0.1:8000/api/player/profile/ -H "Authorization: Token TOKEN_HERE"`
3. Check Django logs for 401 or 500 errors

### App Crashes on Launch
1. Check TypeScript errors: `npm run lint`
2. Check for missing imports in screens
3. Verify context providers in app/_layout.tsx

---

## 📱 Expected Behavior

### Successful Login
1. User enters credentials
2. App calls `/api/login/` endpoint
3. Django returns token + user data
4. Token stored in AsyncStorage
5. User redirected to Dashboard
6. All subsequent API calls include token in header

### Data Loading
1. Each screen calls API endpoint in useEffect
2. Loading indicator shows while fetching
3. Data displays on success
4. Alert shown on error
5. Pull-to-refresh available on list screens

### Token Persistence
1. App saves token to AsyncStorage after login
2. On app restart, token is read from storage
3. Bootstrap effect checks for token
4. If token exists, auto-login occurs
5. If no token, stay on login screen

---

## ✨ Success Criteria

You'll know testing is successful when:

✅ App launches without errors  
✅ Can login with testplayer/testpass  
✅ Dashboard loads with player data  
✅ All 4 tabs are clickable  
✅ Announcements list displays 2 items  
✅ Videos list displays 2 videos  
✅ User info shows on Account screen  
✅ Logout works and clears token  
✅ Can login again after logout  
✅ No unhandled errors in console

---

## 🔧 Advanced Testing

### Network Inspection (React Native Debugger)
1. Open React Native Debugger
2. Go to Network tab
3. Perform login
4. Check request headers include `Authorization: Token xxx`
5. Check response contains user data

### Performance Testing
1. Open Device monitor (Xcode for iOS / Android Studio for Android)
2. Check memory usage doesn't spike
3. Verify no excessive network requests
4. Check app responsiveness

### Error Handling
1. Disconnect from WiFi
2. Try to load data
3. Should show alert: "Failed to load profile"
4. Reconnect WiFi
5. Pull-to-refresh to retry
6. Should succeed

---

## 📝 Logging Issues Found

If you encounter issues, please note:
1. Screenshot of error
2. Steps to reproduce
3. Expected vs actual behavior
4. Network requests (from debugger)
5. Console logs/errors

---

## 🎯 Next Steps After Testing

### If All Tests Pass:
- [ ] Deploy to TestFlight (iOS)
- [ ] Deploy to Google Play (Android)
- [ ] Share with team for beta testing
- [ ] Gather user feedback
- [ ] Plan feature updates

### If Issues Found:
- [ ] Document the issue
- [ ] Identify root cause
- [ ] Fix in code
- [ ] Re-test
- [ ] Commit changes

---

## �� Support

**API Endpoints:** http://127.0.0.1:8000/api/  
**Django Admin:** http://127.0.0.1:8000/admin/  
**Admin Username:** admin  
**Admin Password:** (set in .env)

---

**Testing Date: December 24, 2025**  
**App Version: 1.0.0**  
**React Native: 0.81.5**  
**Django: 6.0**

