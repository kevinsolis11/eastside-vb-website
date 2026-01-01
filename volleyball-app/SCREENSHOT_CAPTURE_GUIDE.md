# Screenshot Capture Instructions

## App Store Screenshot Specs

### iOS Screenshots
- **Phone:** 1242×2688 (6.1") or 1170×2532 (5.8")
- **Count:** 5-8 screenshots
- **Format:** PNG or JPEG
- **Upload:** App Store Connect

### Android Screenshots  
- **Phone:** 1080×1920 or 1440×2560
- **Count:** 4-8 screenshots
- **Format:** PNG or JPEG
- **Upload:** Google Play Console

---

## Screens to Capture (7 Total)

1. **Login Screen** - Username/password login
2. **Player Dashboard** - Home with profile card and stats grid
3. **Player Profile** - Personal information
4. **Player Stats** - Kill/block/ace/dig statistics
5. **Announcements Feed** - Team announcements
6. **Video List** - Game videos
7. **Account Settings** - Account options & logout

---

## How to Capture on iOS Simulator

### Setup iOS Simulator
```bash
cd /Users/klaysolis/eastside\ vb\ website/volleyball-app
open ios/EastsideVolleyball.xcworkspace
```

In Xcode:
1. Select "EastsideVolleyball" scheme
2. Select "iPhone 15" device
3. Press Play (▶) to build and run

### Capture Screenshots in Simulator
```bash
# Method 1: Built-in Screenshot
# In Simulator: Cmd + S (saves to Desktop)

# Method 2: Using xcrun
xcrun simctl io booted screenshot ~/Screenshots/screen-1.png
```

### Resize for App Store
```bash
# iOS 6.1" (1242×2688)
convert screen-1.png -resize 1242x2688 screen-1-resized.png

# Or for 5.8" (1170×2532)
convert screen-1.png -resize 1170x2532 screen-1-resized.png
```

---

## How to Capture on Android Emulator

### Setup Android Emulator
```bash
# If you have Android Studio installed
open -a "Android Studio"

# Or via command line
emulator -avd Pixel_6_API_30
```

### Capture Screenshots
```bash
# Connect to running emulator
adb devices

# Capture screenshot
adb shell screencap -p /sdcard/screenshot.png

# Pull to computer
adb pull /sdcard/screenshot.png ~/Screenshots/android-screen-1.png

# Resize for App Store (1080×1920)
convert android-screen-1.png -resize 1080x1920 android-screen-1-resized.png
```

---

## Quick Script to Capture All

### iOS
```bash
#!/bin/bash
mkdir -p ~/Screenshots/ios

for i in {1..7}; do
  echo "Capture screenshot $i on iOS Simulator"
  read -p "Press Enter when ready..."
  xcrun simctl io booted screenshot ~/Screenshots/ios/screen-$i.png
done

echo "Converting to App Store size (1242x2688)..."
for f in ~/Screenshots/ios/screen-*.png; do
  convert "$f" -resize 1242x2688 "${f%.png}-1242x2688.png"
done
```

### Android
```bash
#!/bin/bash
mkdir -p ~/Screenshots/android

for i in {1..7}; do
  echo "Capture screenshot $i on Android"
  read -p "Press Enter when ready..."
  adb shell screencap -p /sdcard/screen-$i.png
  adb pull /sdcard/screen-$i.png ~/Screenshots/android/
done

echo "Converting to App Store size (1080x1920)..."
for f in ~/Screenshots/android/screen-*.png; do
  convert "$f" -resize 1080x1920 "${f%.png}-1080x1920.png"
done
```

---

## Upload to App Stores

### iOS App Store
1. Go to [App Store Connect](https://appstoreconnect.apple.com)
2. Select your app
3. Go to App Preview and Screenshots
4. Upload in order: Login → Dashboard → Profile → Stats → Announcements → Videos → Settings
5. Add captions to highlight features

### Google Play Store
1. Go to [Google Play Console](https://play.google.com/console)
2. Select your app
3. Go to Store Listing
4. Upload screenshots for each language/device type
5. Add promotional text

---

## Tips for Better Screenshots

1. **Use real data** - Mock data shows the app works
2. **Landscape some screens** - Shows versatility
3. **Add text overlays** - Highlight key features (optional but recommended)
4. **Test on actual devices** - Screenshots look better than simulator
5. **Use consistent branding** - Match your color scheme (blue #007AFF)

---

## Recommended Screenshot Order

1. **Login** - First impression
2. **Dashboard** - Main interface
3. **Stats** - Key feature highlight
4. **Videos** - Engagement feature
5. **Profile** - Personalization
6. **Announcements** - Communication
7. **Settings** - Control/logout

This shows the app's workflow and main features in order.
