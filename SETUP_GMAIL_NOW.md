# STEP-BY-STEP EMAIL SETUP (5 MINUTES)

## STEP 1: Enable 2FA on Gmail (Skip if already done)
1. Go to https://myaccount.google.com/security
2. Find "2-Step Verification"
3. Click "Enable"
4. Follow prompts (will ask for phone)
5. Done with 2FA

## STEP 2: Get Your App Password
1. After 2FA is enabled, go to https://myaccount.google.com/apppasswords
2. If it asks to sign in again, do it
3. Select dropdown "Mail" (should be default)
4. Select dropdown "Windows Computer" (or your OS)
5. Click "GENERATE"
6. **Copy the 16-character password** (will look like: abcd efgh ijkl mnop)
7. Paste it somewhere safe temporarily

## STEP 3: Add to Railway
1. Open https://railway.app/dashboard
2. Click your "eastside-vb-website" project
3. Click "Settings" (gear icon)
4. Click "Variables" on left menu
5. Add these 4 variables (copy exactly):

```
EMAIL_HOST
smtp.gmail.com

EMAIL_HOST_USER
your-email@gmail.com

EMAIL_HOST_PASSWORD
xxxx xxxx xxxx xxxx   (the password from step 2)

DEFAULT_FROM_EMAIL
your-email@gmail.com
```

6. Click "Save"

## STEP 4: Railway Will Auto-Deploy
- Wait 30 seconds
- Dashboard will show "Deployment" status
- Wait for green checkmark "UP"

## STEP 5: Test It Works
1. Go to your site: https://your-railway-domain.com
2. Log in as coach (kevinsolis / admin123)
3. Click "Generate Access Codes" (in navigation)
4. Fill in form:
   - Role: Player
   - Count: 1
   - Email: YOUR EMAIL (test with your own email)
5. Click "Generate Codes"
6. Should see GREEN message: "✓ Invite email(s) queued for your-email@gmail.com"
7. Wait 1 minute
8. Check your email inbox
9. Should have email from Gmail with access code

## If Email Doesn't Arrive
Check these in order:
1. Spam folder (add to contacts)
2. Railway logs (look for errors)
3. Gmail account 2FA enabled (required)
4. Variables copied exactly (no extra spaces)

---

**That's it! 5 steps, ~5 minutes total.**

Need help with any step? Let me know which one and I'll walk you through it more.
