# Railway Email Configuration Guide

## Quick Setup (5 minutes)

### Step 1: Get Gmail App Password
1. Go to https://myaccount.google.com/apppasswords
2. Sign in if prompted
3. Select **Mail** and **Windows Computer** (or your OS)
4. Click **Generate**
5. Copy the 16-character password (without spaces)

### Step 2: Add to Railway Environment
1. Open Railway Dashboard
2. Go to your project → Settings → Variables
3. Add these 4 variables:
   ```
   EMAIL_HOST=smtp.gmail.com
   EMAIL_HOST_USER=your-email@gmail.com
   EMAIL_HOST_PASSWORD=xxxx xxxx xxxx xxxx
   DEFAULT_FROM_EMAIL=your-email@gmail.com
   ```
4. Click Save

### Step 3: Deploy & Test
1. Railway auto-deploys with new variables (no need to push)
2. Wait for build to complete (~30 seconds)
3. Log in as coach → Generate Access Codes
4. Enter your test email and click "Generate Codes"
5. Check inbox for email (arrives within 1 minute)

---

## Status Indicators

### When Email Works ✅
- Green banner: "✓ Invite email(s) queued for player@gmail.com"
- Email arrives in inbox within 1 minute
- Codes shown in list regardless

### When Email NOT Configured ⚠️
- Red banner: "⚠️ Email not configured on server..."
- Codes are still generated
- Coach must share codes manually
- No error to fix (just set environment variables)

### When Email Fails ❌
- Red banner: "❌ Failed to send invite email..."
- Codes are still generated
- Check Railway logs for specific error
- Possible causes:
  - Gmail 2FA not enabled for app password
  - Password typed incorrectly
  - SMTP server unreachable
  - Rate limited by Gmail

---

## Common Issues

### Issue: "Failed to send invite email: Connection refused"
**Cause:** EMAIL_HOST_USER is empty or EMAIL_HOST doesn't exist
**Fix:** 
1. Verify variables are set in Railway Settings
2. Redeploy (or just wait, sometimes takes 1-2 min to apply)
3. Test again

### Issue: "Authentication failed for user"
**Cause:** Wrong Gmail app password or account isn't Gmail
**Fix:**
1. Go to https://myaccount.google.com/apppasswords
2. Verify 2FA is enabled on Gmail account
3. Generate NEW app password
4. Copy full 16 characters (no spaces)
5. Update in Railway
6. Test again

### Issue: "Email sent but player never received it"
**Cause:** Might be in spam folder
**Fix:**
1. Check Gmail spam folder
2. Ask player to add to contacts
3. Try sending from coach Gmail account instead

---

## Alternative Email Providers

### SendGrid (Recommended)
More reliable for production. Free tier: 100 emails/day

```
EMAIL_HOST=smtp.sendgrid.net
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=SG.xxxxxxxxxx  (your API key)
DEFAULT_FROM_EMAIL=noreply@your-domain.com
```

### AWS SES
Best for high volume. ~$0.10 per 1000 emails

```
EMAIL_HOST=email-smtp.us-east-1.amazonaws.com
EMAIL_HOST_USER=AKIA...
EMAIL_HOST_PASSWORD=xxxx...
DEFAULT_FROM_EMAIL=verified-email@domain.com
```

---

## Fallback: Manual Code Distribution

If email never works:
1. Coach generates codes without email
2. Codes appear in "All Codes" list
3. Coach copies codes
4. Coach shares via:
   - Text message
   - Phone call
   - Message on team chat
   - Posted on team website
5. Players use codes to sign up

**No functionality lost - just more manual process**

---

## Monitoring Email

### Check if working
1. Generate a code with your own email
2. Should arrive within 1 minute
3. If it does → fully working ✓

### View Error Logs
Railway Dashboard → Logs → Search for "email"

Look for:
- "✓ Email sent" = success
- "❌ Failed to send" = error
- "Email not configured" = missing env vars

---

## Admin Checklist

- [ ] Gmail account with 2FA enabled
- [ ] App password created and copied
- [ ] All 4 env vars set in Railway:
  - [ ] EMAIL_HOST
  - [ ] EMAIL_HOST_USER
  - [ ] EMAIL_HOST_PASSWORD
  - [ ] DEFAULT_FROM_EMAIL
- [ ] Railway build completed successfully
- [ ] Test email sent and received
- [ ] Coaches trained on using the system
- [ ] Player FAQ updated with "how to get codes"

---

## Support

**If email still fails after all steps:**

1. Check Railway logs for specific error message
2. Verify env variables are exactly correct (no extra spaces)
3. Try alternative email provider (SendGrid)
4. Contact Railway support if SMTP connection fails
5. Consider using manual code distribution as fallback

**Key Point:** Coaches can always distribute codes manually - email is optional for convenience, not required for functionality.
