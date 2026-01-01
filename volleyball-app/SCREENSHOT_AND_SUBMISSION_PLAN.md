# 📸 App Store Submission - Complete Action Plan

**Status:** Ready for Screenshots & Submission  
**Date:** December 24, 2025

---

## ✅ What's Complete

- ✅ SVG assets converted to PNG
- ✅ Native projects created (iOS & Android)
- ✅ Mock data integrated (app works without backend)
- ✅ App metadata updated (keywords, category)
- ✅ Comprehensive documentation created

---

## 🎬 NEXT: Capture Screenshots

### Step 1: Start Dev Server

Run the app in your phone's Expo Go app or use the simulator.

**Option A: iPhone (Real Device)**
```bash
cd "/Users/klaysolis/eastside vb website/volleyball-app"
npx expo start
# Scan QR code with Camera app
# Use test credentials: (any username, mock data loads)
```

**Option B: iOS Simulator** 
```bash
# From the dev server terminal, press: i
# Or in a new terminal:
open ios/EastsideVolleyball.xcworkspace
# Then click Play in Xcode
```

### Step 2: Test Login

The app now has mock data built-in. You can:
- Use **any username** to test (mock data will load)
- Test credentials: `demo` / `password`
- Or just tap login and it will load mock player data

### Step 3: Capture 7 Screens

Navigate to each screen and screenshot:

1. **Login Screen**
   - Show: Username/password fields, login button
   - Caption: "Secure team login"

2. **Player Dashboard** (Home tab)
   - Show: Profile card, 4-stat grid, AI summary
   - Caption: "Real-time player stats and performance summary"

3. **Player Profile** (Profile icon in tab)
   - Show: Jersey #, position, height, year
   - Caption: "Detailed player profile information"

4. **Player Stats** (Stats icon in tab)
   - Show: Kill/block/ace/dig stats with season overview
   - Caption: "Advanced player statistics and season records"

5. **Announcements Feed** (Announcements tab)
   - Show: Team announcements with urgent highlights
   - Caption: "Stay updated with team announcements"

6. **Video List** (Videos tab)
   - Show: Game videos with thumbnails
   - Caption: "Watch game recordings and training videos"

7. **Account Settings** (Settings tab)
   - Show: User info, logout button
   - Caption: "Account management and settings"

---

## 📱 How to Screenshot

### On iPhone (Real Device)
```bash
# Hardware buttons:
# Press: Volume Up + Side Button simultaneously
# Screenshot saves to Photos app
```

### On iOS Simulator
```bash
# Method 1: Keyboard shortcut
Cmd + S
# Screenshot saves to Desktop

# Method 2: Menu
Simulator > File > New Screen Shot

# Method 3: Command line
xcrun simctl io booted screenshot ~/Desktop/screen-name.png
```

### Resize for App Store (if needed)
```bash
# iOS size: 1242×2688
convert screenshot.png -resize 1242x2688 screenshot-resized.png
```

---

## 📋 Screenshot Checklist

| Screen | iOS ✓ | Android ✓ | iOS File | Android File |
|--------|-------|-----------|----------|--------------|
| Login | [ ] | [ ] | login.png | login-android.png |
| Dashboard | [ ] | [ ] | dashboard.png | dashboard-android.png |
| Profile | [ ] | [ ] | profile.png | profile-android.png |
| Stats | [ ] | [ ] | stats.png | stats-android.png |
| Announcements | [ ] | [ ] | announcements.png | announcements-android.png |
| Videos | [ ] | [ ] | videos.png | videos-android.png |
| Settings | [ ] | [ ] | settings.png | settings-android.png |

---

## 🚀 After Screenshots: App Store Submission

### Create Apple Developer Account
1. Go to [developer.apple.com](https://developer.apple.com)
2. Sign in with Apple ID
3. Enroll in Apple Developer Program ($99/year)
4. Accept agreements

### Create Google Developer Account
1. Go to [play.google.com/console](https://play.google.com/console)
2. Sign in with Google Account
3. Create first app ($25 one-time fee)

### iOS App Store Submission
1. Open [App Store Connect](https://appstoreconnect.apple.com)
2. Create app record:
   - Name: "Eastside Volleyball"
   - Bundle ID: `com.eastsidevolleyball.app`
   - SKU: Any unique ID
3. Fill in metadata:
   - Description
   - Keywords
   - Category: Sports
   - Ratings
   - Screenshots (7)
4. Build & Code Sign
5. Submit for Review

### Android Play Store Submission
1. Open [Google Play Console](https://play.google.com/console)
2. Create app:
   - Name: "Eastside Volleyball"
   - Package: `com.eastsidevolleyball.app`
3. Fill in metadata:
   - Description
   - Screenshots (7)
   - Category: Sports
   - Content rating
4. Build APK/AAB
5. Upload build
6. Submit for Review

---

## 📦 Build for Production

### iOS (via Xcode)
```bash
cd ios
xcodebuild -workspace EastsideVolleyball.xcworkspace \
  -scheme EastsideVolleyball \
  -configuration Release \
  -derivedDataPath build
```

### Android (via Gradle)
```bash
cd android
./gradlew bundleRelease
# Or for APK:
./gradlew assembleRelease
```

---

## 📞 Test Credentials for Screenshots

Since the app uses mock data, any login works:

```
Username: demo
Password: password

Or try:
Username: coach
Password: test

Or just make up any credentials - mock data loads!
```

---

## 🎯 Current Status

| Task | Status | File |
|------|--------|------|
| Assets converted | ✅ | icon.png, splash.png |
| Native builds | ✅ | ios/, android/ |
| Mock data | ✅ | app/api/mockData.ts |
| App metadata | ✅ | app.json |
| Docs created | ✅ | Multiple guides |
| Screenshots | 📸 | In Progress |
| App Store submission | ⏳ | Next |
| Play Store submission | ⏳ | Next |

---

## 🔗 Quick Links

- **Expo Docs:** https://docs.expo.dev
- **App Store Connect:** https://appstoreconnect.apple.com
- **Google Play Console:** https://play.google.com/console
- **Eastside VB:** https://eastsidevolleyball.com

---

## 💡 Tips

1. **Use mock data** for faster testing
2. **Capture with real device** for best quality
3. **Use consistent colors** (blue #007AFF)
4. **Show all 7 screens** for completeness
5. **Add captions** if app store allows

---

**Next Step:** Start the dev server and capture screenshots!

```bash
cd "/Users/klaysolis/eastside vb website/volleyball-app"
npx expo start
```

Then follow the screenshot steps above. Let me know when you have them captured and I can help with the actual store submission process!
