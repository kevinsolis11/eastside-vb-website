# Quick Reference - Build & Test Commands

## 🚀 Fast Start

### Development Testing (No Build)
```bash
cd "/Users/klaysolis/eastside vb website/volleyball-app"
npx expo start --clear
# Scan QR code with phone camera
```

### Test on iOS (Requires Xcode)
```bash
# Option 1: Native build
npx expo run:ios

# Option 2: Xcode IDE
open ios/EastsideVolleyball.xcworkspace
# Then Product > Run in Xcode
```

### Test on Android (Requires Android Studio/Emulator)
```bash
npx expo run:android
```

---

## 📦 Production Builds

### For iOS App Store
```bash
cd "/Users/klaysolis/eastside vb website/volleyball-app/ios"

# Build with Xcode
xcodebuild -workspace EastsideVolleyball.xcworkspace \
  -scheme EastsideVolleyball \
  -configuration Release \
  -derivedDataPath build

# Or use Xcode GUI:
# 1. open EastsideVolleyball.xcworkspace
# 2. Select "EastsideVolleyball" scheme
# 3. Select "Generic iOS Device"
# 4. Product > Archive
```

### For Google Play Store
```bash
cd "/Users/klaysolis/eastside vb website/volleyball-app/android"

# Build AAB (recommended for Play Store)
./gradlew clean bundleRelease

# Or build APK (for testing)
./gradlew clean assembleRelease

# Output: 
# AAB: android/app/build/outputs/bundle/release/app-release.aab
# APK: android/app/build/outputs/apk/release/app-release.apk
```

---

## 🔧 Common Tasks

### Clear cache & rebuild
```bash
rm -rf node_modules package-lock.json
npm install
npx expo start --clear
```

### Clear iOS build cache
```bash
cd ios
rm -rf Podfile.lock Pods build
pod install
```

### Clear Android build cache
```bash
cd android
./gradlew clean
```

### Update dependencies
```bash
npm update
npx expo prebuild --clean --platform all
```

---

## 📱 Asset Files

| File | Dimensions | Size | Purpose |
|------|-----------|------|---------|
| `assets/icon.png` | 1024×1024 | 93KB | App icon |
| `assets/splash.png` | 1242×2688 | 291KB | Launch screen |
| `assets/icon.svg` | 1024×1024 | SVG | Keep as backup |
| `assets/splash.svg` | 1242×2688 | SVG | Keep as backup |

---

## 🗂️ Project Structure

```
volleyball-app/
├── ios/                    # iOS Xcode project
├── android/                # Android Gradle project
├── app/                    # React Native app code
│   ├── (tabs)/            # Tab screens
│   ├── screens/           # Screen components
│   ├── api/               # API client
│   ├── context/           # State management
│   └── _layout.tsx        # Root layout
├── assets/                # Images & icons
├── components/            # Reusable UI components
├── constants/             # App constants
├── app.json              # App configuration
├── eas.json              # EAS build config
├── tsconfig.json         # TypeScript config
├── package.json          # Dependencies
└── BUILD_AND_DEPLOYMENT_GUIDE.md  # Full guide
```

---

## 🎯 Key Endpoints

**Development:** `http://127.0.0.1:8000/api`  
**Production:** `https://api.eastsidevolleyball.com/api`

Update in: `app/api/client.ts`

---

## ✅ Pre-Build Checklist

- [ ] Node.js & npm installed
- [ ] All dependencies installed (`npm install`)
- [ ] No uncommitted git changes
- [ ] API server running (for development)
- [ ] Xcode installed (for iOS builds)
- [ ] Android Studio installed (for Android builds)

---

## 🆘 Troubleshooting

### Metro Bundler won't start
```bash
npx expo start --clear
# or
lsof -ti:8081 | xargs kill -9  # kill port
npx expo start
```

### CocoaPods issues
```bash
cd ios
pod deintegrate
pod install
```

### Android build fails
```bash
cd android
./gradlew clean
./gradlew build
```

### Out of memory
```bash
export NODE_OPTIONS=--max-old-space-size=8192
npx expo start
```

---

**Generated:** December 24, 2025  
**App Version:** 1.0.0  
**Status:** ✅ Ready for Testing & Deployment
