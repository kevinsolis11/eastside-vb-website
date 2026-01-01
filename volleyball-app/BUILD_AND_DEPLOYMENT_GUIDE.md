# Build and Deployment Guide

**Updated:** December 24, 2025  
**App Version:** 1.0.0

---

## 📱 Development Testing

### Option 1: Expo Go (Quickest)
Test on your phone with Expo Go app (no build needed):

```bash
cd /Users/klaysolis/eastside\ vb\ website/volleyball-app
npx expo start --clear

# Then:
# iOS: Scan QR code with Camera app
# Android: Scan QR code with Expo Go app
```

**Pros:** Instant testing, no compilation  
**Cons:** Limited to Expo-supported features  

### Option 2: Prebuild for Native Testing
Create native Android/iOS projects for full feature testing:

```bash
# Create native project files
npx expo prebuild --clean --platform all

# Then run on iOS Simulator
npx expo run:ios

# Or run on Android Emulator
npx expo run:android
```

**Pros:** Full native features, closer to production  
**Cons:** First build takes longer (compiles native code)

---

## 🔨 Production Build Process

### Prerequisites

Before building for production, ensure:

1. **Xcode installed** (for iOS):
   ```bash
   xcode-select --install
   ```

2. **Android SDK** (for Android): Install Android Studio

3. **Accounts created:**
   - Apple Developer Account ($99/year) for iOS
   - Google Play Developer Account ($25 one-time) for Android

### Step 1: Prebuild Native Projects

```bash
cd /Users/klaysolis/eastside\ vb\ website/volleyball-app

# Clean prebuild for production
npx expo prebuild --clean --platform all
```

This creates:
- `ios/` - iOS Xcode project
- `android/` - Android Gradle project

### Step 2: Configure Code Signing

#### For iOS:

```bash
# Open Xcode
open ios/volleyballApp.xcworkspace

# In Xcode:
# 1. Select project in navigator
# 2. Select "volleyball-app" target
# 3. Go to "Signing & Capabilities"
# 4. Select your team
# 5. Update Bundle Identifier (if needed)
# 6. Let Xcode manage signing
```

#### For Android:

```bash
# Create signing key (one-time)
keytool -genkey -v -keystore ~/my-release-key.keystore \
  -keyalg RSA -keysize 2048 -validity 10000 \
  -alias my-key-alias

# Create gradle.properties
cat > android/gradle.properties << 'EOF'
MYAPP_RELEASE_STORE_FILE=my-release-key.keystore
MYAPP_RELEASE_KEY_ALIAS=my-key-alias
MYAPP_RELEASE_STORE_PASSWORD=<password>
MYAPP_RELEASE_KEY_PASSWORD=<password>
EOF

# Update android/app/build.gradle to use signing config
```

### Step 3: Build for Production

#### iOS Build (via Xcode):

```bash
cd ios

# Build for iOS
xcodebuild -workspace volleyballApp.xcworkspace \
  -scheme volleyballApp \
  -configuration Release

# Or use Product > Archive in Xcode, then upload to App Store
```

#### Android Build (via Gradle):

```bash
cd android

# Create APK
./gradlew clean assembleRelease

# Or create AAB (recommended for Play Store)
./gradlew clean bundleRelease
```

### Step 4: Submit to App Stores

#### iOS App Store

1. Create an app record in App Store Connect
2. Upload `.ipa` file via Xcode Organizer or Transporter
3. Add app metadata (screenshots, description, etc.)
4. Submit for review (24-48 hours)

**Important Files:**
- Privacy Policy: Already created at `PRIVACY_POLICY.md`
- Terms of Service: Already created at `TERMS_OF_SERVICE.md`
- App Icon: `assets/icon.png` (1024x1024)
- Splash Screen: `assets/splash.png` (1242x2688)

#### Google Play Store

1. Create an app project in Google Play Console
2. Upload signed `.aab` file
3. Add app metadata (screenshots, description, etc.)
4. Set pricing and distribution
5. Submit for review (2-4 hours)

**Privacy Policy URL:** Configure in Play Console to point to online policy

---

## 📸 App Store Screenshots

### Required for Both Platforms

Take screenshots of these 7 screens:

1. **Login Screen** - Initial login flow
2. **Player Dashboard** - Home screen with profile card
3. **Player Profile** - Profile information tab
4. **Player Stats** - Statistics tab
5. **Announcements Feed** - Team announcements tab
6. **Video List** - Videos tab
7. **Account Settings** - Account settings tab

### Specification

**iOS:**
- iPhone: 1242x2688 (6.1") or 1170x2532 (5.8")
- iPad: 2048x2732
- Upload 5-8 screenshots per language

**Android:**
- Phone: 1080x1920 or 1440x2560
- Tablet: 1200x1920
- Upload 4-8 screenshots

---

## 🔐 API Configuration

Ensure your Django backend is properly configured for production:

```python
# Django settings.py

# CORS Configuration
CORS_ALLOWED_ORIGINS = [
    "https://eastsidevolleyball.com",
    # Add your production domain
]

# API Base URL (in app/api/client.ts)
const API_BASE_URL = 'https://api.eastsidevolleyball.com/api';
```

---

## ✅ Pre-Submission Checklist

- [ ] All 7 screens tested on real iOS device
- [ ] All 7 screens tested on real Android device
- [ ] API endpoints verified working with production backend
- [ ] App icon and splash screens converted to PNG
- [ ] Screenshots captured for all 7 screens
- [ ] Privacy Policy published online
- [ ] Terms of Service published online
- [ ] App metadata (title, description, keywords) finalized
- [ ] Version number confirmed (currently 1.0.0)
- [ ] Build numbers incremented
- [ ] No console errors or warnings
- [ ] App performance acceptable (<3 second launch)

---

## 🚀 Next Steps

1. **Test Locally:** Use `npx expo start` for quick testing
2. **Native Testing:** Use `npx expo prebuild` and `npx expo run:ios/android`
3. **Register Developer Accounts:** Apple ($99) and Google ($25)
4. **Build Natives:** Follow Step 2-3 above
5. **Capture Screenshots:** Required for store listings
6. **Submit for Review:** Follow Step 4 above

---

## 📚 Resources

- [Expo Prebuild Documentation](https://docs.expo.dev/build-reference/prebuild/)
- [iOS App Store Connect Guide](https://help.apple.com/app-store-connect/)
- [Google Play Console Guide](https://support.google.com/googleplay/android-developer)
- [React Native Production Build Guide](https://reactnative.dev/docs/signed-apk-android)

---

## 🆘 Troubleshooting

### Metro Bundler Issues
```bash
# Clear cache and restart
npx expo start --clear
```

### CocoaPods Issues (iOS)
```bash
cd ios
rm Podfile.lock
pod deintegrate
pod install
```

### Gradle Issues (Android)
```bash
cd android
./gradlew clean
./gradlew build
```

### Out of Memory
```bash
# Increase Node memory
export NODE_OPTIONS=--max-old-space-size=4096
```

---

**Current Status:** ✅ Ready for Testing & Deployment
