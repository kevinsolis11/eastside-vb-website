# App Store Deployment Guide

**Eastside Volleyball Mobile Application**  
**Version 1.0.0**

---

## 📋 Pre-Submission Checklist

### ✅ Technical Requirements
- [x] App built with React Native + Expo
- [x] TypeScript for type safety
- [x] API integration complete
- [x] Authentication implemented
- [x] All 7 screens implemented
- [x] App tested on device
- [x] app.json configured with metadata
- [x] eas.json configured for builds
- [x] Privacy policy created

### 📦 Assets Needed
- [ ] App Icon (1024x1024 PNG)
- [ ] Splash Screen (1242x2688 PNG)
- [ ] Screenshots for iOS (6 images: 1242x2208)
- [ ] Screenshots for Android (6 images: 1080x1920)
- [ ] Feature Graphic (1024x500 PNG)
- [ ] Privacy Policy URL
- [ ] Terms of Service URL
- [ ] Support Email

### 📝 Metadata Needed
- [x] App Name: "Eastside Volleyball"
- [x] Short Description (80 characters max)
- [x] Full Description (with features)
- [x] Keywords/Tags
- [x] Bundle IDs: com.eastsidevolleyball.app
- [x] Version: 1.0.0

---

## 🍎 iOS App Store Submission

### Step 1: Create Apple Developer Account
```bash
# Visit: https://developer.apple.com/account/
# Cost: $99/year
# Required: Apple ID, credit card
```

### Step 2: Create App in App Store Connect
1. Go to: https://appstoreconnect.apple.com
2. Click "My Apps" → "New App"
3. Fill in:
   - App Name: "Eastside Volleyball"
   - Bundle ID: com.eastsidevolleyball.app
   - SKU: Can be anything (e.g., eastside-vb-001)
   - User Access: Select access level

### Step 3: Configure App Information

**App Information:**
```
Name: Eastside Volleyball
Subtitle: (Leave blank or add brief tagline)
Primary Category: Sports
Secondary Category: Social Networking
Content Rights: Yes
Advertising ID: No
Age Rating: 4+
```

**Description:**
```
Stay connected with your Eastside Volleyball team!

Features:
✓ Player profiles with detailed stats
✓ Game videos and highlights
✓ Team announcements in real-time
✓ Season statistics tracking
✓ Secure team-only access

Access your player profile, view upcoming games, 
watch game footage, and stay updated with your 
teammates.
```

**Keywords:**
```
volleyball, sports, team, athlete, game, live, 
stats, videos, coaching, high school
```

### Step 4: Add Screenshots
Upload 6 screenshots for each device:
- iPhone (1242x2208 px)
- iPad (2048x2732 px)

**Screenshot Order:**
1. Login Screen
2. Dashboard with stats
3. Announcements Feed
4. Game Videos
5. Player Profile
6. Account Settings

### Step 5: Build & Upload with EAS

```bash
# Install EAS CLI
npm install -g eas-cli

# Login to Expo
eas login

# Build for iOS
eas build --platform ios

# When build completes, upload to App Store Connect
eas submit --platform ios --latest
```

### Step 6: Set Pricing & Availability
- Pricing: Free
- Availability: Select countries (minimum: USA)
- Release type: Automatic (releases when approved)

### Step 7: Add Privacy Policy
- Go to "App Privacy" in App Store Connect
- Add Privacy Policy URL: https://eastsidevolleyball.com/privacy
- Answer data collection questions

### Step 8: Submit for Review
- Review "Version Information"
- Review "Test Information" (optional but recommended)
- Click "Submit for Review"

**Review Time:** 24-48 hours typically

---

## 🤖 Google Play Store Submission

### Step 1: Create Google Play Developer Account
```bash
# Visit: https://play.google.com/console
# Cost: $25 one-time
# Required: Google Account, credit card
```

### Step 2: Create Application
1. Go to: Google Play Console
2. Click "Create App"
3. Fill in:
   - App Name: "Eastside Volleyball"
   - Default Language: English
   - App Category: Sports
   - App Type: Application

### Step 3: Set Up App Details

**Store Listing:**
```
Title: Eastside Volleyball
Short Description (80 chars):
"Connect with your volleyball team. Stats, 
videos, announcements in one app"

Full Description (4000 chars):
"Stay connected with your Eastside Volleyball team!

FEATURES:
✓ Player Profiles - View detailed player information
✓ Game Videos - Watch full games and highlights
✓ Live Stats - Track season statistics
✓ Team Announcements - Get updates from coaches
✓ Secure Access - Team members only

Perfect for players, coaches, and families who 
want to stay connected with the team."

Graphic Elements:
- Feature Graphic (1024x500 px)
- 4-8 Screenshots (1080x1920 px)
- Video Preview (optional)
```

### Step 4: Build & Upload with EAS

```bash
# Create keystore for signing
# EAS will handle this automatically

# Build for Android
eas build --platform android

# When build completes, upload to Google Play
eas submit --platform android --latest
```

### Step 5: Set Pricing & Distribution
- Pricing: Free
- Distribution: All countries
- Device categories: Phones & Tablets
- Target Android 12+

### Step 6: Add Privacy Policy
- Go to App Content → Privacy Policy
- Add URL: https://eastsidevolleyball.com/privacy

### Step 7: Content Rating Questionnaire
- Complete the IARC questionnaire
- Takes ~5 minutes
- Auto-generates ratings for all countries

### Step 8: Submit for Review
- Review all information
- Click "Publish"

**Review Time:** Usually 2-4 hours, but can take up to 24 hours

---

## 🎨 Creating App Assets

### App Icon (1024x1024 PNG)
Create in Figma, Adobe XD, or Canva:
- Square format (no rounded corners - OS handles it)
- Your volleyball/team branding
- Clear at small sizes (play with 180px preview)
- Use tools:
  - https://www.figma.com/templates
  - https://www.canva.com/create/app-icons/

### Screenshots Guide

**iOS Screenshots (1242x2208):**
```
Export dimensions: 1242x2208 px
Safe area: 60px margin on all sides
Text: 36-48px font, white text with shadow
```

**Android Screenshots (1080x1920):**
```
Export dimensions: 1080x1920 px
Safe area: 60px margin
Text: 24-32px font
```

**Tools for Screenshots:**
- Figma: https://www.figma.com/design
- Photoshop: Adobe Express (free)
- Online: https://www.mokups.io/

---

## 🚀 Build Commands

### Development Build
```bash
eas build --platform ios --profile development
# Quick build for testing on device
```

### Preview Build
```bash
eas build --platform ios --profile preview
# For internal testing, closer to production
```

### Production Build
```bash
eas build --platform ios --profile production
# For App Store submission
```

### Auto-Submit
```bash
# Submit immediately after successful build
eas submit --platform ios --latest
eas submit --platform android --latest
```

---

## 🔧 Environment Variables

### Create `.env.production`
```bash
EXPO_PUBLIC_API_URL=https://api.eastsidevolleyball.com/api
EXPO_PUBLIC_ENV=production
```

### Update `eas.json` to use environment
```json
{
  "build": {
    "production": {
      "env": {
        "EXPO_PUBLIC_API_URL": "https://api.eastsidevolleyball.com/api"
      }
    }
  }
}
```

---

## 🔒 Security Before Launch

### Checklist
- [ ] Remove console.log statements in production
- [ ] Update API URL to production endpoint
- [ ] Enable HTTPS only
- [ ] Implement certificate pinning (optional)
- [ ] Remove test credentials from code
- [ ] Enable App Transport Security (iOS)
- [ ] Implement crash reporting (Sentry)

### Crash Reporting Setup
```bash
npm install @sentry/react-native

# Initialize in app/_layout.tsx
import * as Sentry from "@sentry/react-native";
Sentry.init({
  dsn: "YOUR_SENTRY_DSN",
});
```

---

## 📊 Version Management

### Versioning Scheme
```
Format: X.Y.Z
- X (Major): Major features (1.0.0 → 2.0.0)
- Y (Minor): New features (1.0.0 → 1.1.0)
- Z (Patch): Bug fixes (1.0.0 → 1.0.1)
```

### Update for New Versions
1. Update version in `app.json`:
```json
{
  "expo": {
    "version": "1.1.0"
  }
}
```

2. Update build number in `eas.json`:
```json
{
  "build": {
    "production": {
      "ios": {
        "buildNumber": "2"
      },
      "android": {
        "versionCode": 2
      }
    }
  }
}
```

3. Rebuild and resubmit

---

## 🎯 Launch Timeline

### Week 1: Prepare
- Create developer accounts
- Design app icon & screenshots
- Host privacy policy
- Test app thoroughly

### Week 2: Submit
- Submit to App Store
- Submit to Google Play
- Monitor for reviews/questions

### Week 3: Monitor
- Check review status daily
- Prepare for launch
- Set up App Store listing

### Week 4: Launch
- App approved and live
- Monitor for crashes
- Gather user feedback
- Plan next features

---

## 📞 Support Resources

### Apple Support
- https://developer.apple.com/support/
- https://help.apple.com/app-store-connect/

### Google Play Support
- https://support.google.com/googleplay/
- https://developer.android.com/docs

### Expo Docs
- https://docs.expo.dev/build/introduction/
- https://docs.expo.dev/submit/introduction/

### Common Issues
```
Issue: App rejected for privacy policy
Solution: Ensure privacy policy URL is accessible

Issue: Build failures
Solution: Run locally first: npm run ios

Issue: Screenshots not accepted
Solution: Check exact dimensions and safe areas

Issue: App crashes on launch
Solution: Check API endpoint in production
```

---

## ✅ Final Checklist Before Submit

- [ ] Version bumped in app.json
- [ ] app.json has correct bundle IDs
- [ ] Privacy policy is hosted and accessible
- [ ] All screenshots are correct dimensions
- [ ] App icon is 1024x1024 PNG
- [ ] App tested on physical device
- [ ] No console.log or debug code
- [ ] API URL is correct for production
- [ ] All permissions documented
- [ ] Keywords are relevant
- [ ] Description is compelling
- [ ] EAS project is linked
- [ ] Developer accounts created
- [ ] Payment methods added

---

## 🎉 Post-Launch

### Monitoring
- Check crash reports daily
- Review user ratings
- Respond to reviews
- Track installs

### Updates
- Plan v1.1 with user feedback
- Fix bugs reported
- Add requested features
- Improve performance

### Marketing
- Share App Store link
- Post on social media
- Email to players
- Submit press release

---

**Good luck with your launch! 🚀**

*For questions, contact: deploy@eastsidevolleyball.com*
