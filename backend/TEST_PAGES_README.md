# Phishing Test Pages

## Overview
These are realistic phishing test pages to validate PhishGuard's detection capabilities.

## Test Pages

### 1. PayPal Phishing (`visual_trap.html`)
**URL to test:** `http://localhost:8000/visual_trap.html` or `http://192.168.1.1/visual_trap.html`

**Expected Detection:**
- ✅ High phishing score (75+)
- ✅ Reason: "Visuals show 'PayPal' but URL is different"
- ✅ Content triggers: "verify your account", "unusual activity", "suspension"
- ✅ URL risk: IP address or non-PayPal domain

**Phishing Indicators:**
- Urgency alert ("Account Verification Required")
- Suspicious keywords ("unusual activity", "avoid suspension")
- Fake PayPal branding
- Password request on suspicious domain

---

### 2. Netflix Phishing (`test_netflix.html`)
**URL to test:** `http://suspicious-domain.tk/test_netflix.html`

**Expected Detection:**
- ✅ High phishing score (70+)
- ✅ Reason: "Visuals show 'Netflix' but URL is different"
- ✅ Content triggers: "subscription has expired", "update your payment"
- ✅ URL risk: Suspicious TLD (.tk)

**Phishing Indicators:**
- Fake subscription expiry alert
- Payment update request
- Netflix branding on non-Netflix domain
- Dark patterns (urgent messaging)

---

### 3. Google Phishing (`test_google.html`)
**URL to test:** `http://accounts-google-verify.com/test_google.html`

**Expected Detection:**
- ✅ High phishing score (80+)
- ✅ Reason: "Visuals show 'Google' but URL is different"
- ✅ Content triggers: "security alert", "verify your identity"
- ✅ URL risk: Fake Google domain

**Phishing Indicators:**
- Security alert message
- Identity verification request
- Google branding on fake domain
- Credential harvesting form

---

## How to Test

### Method 1: Local Server
```bash
# Start backend server (if not running)
cd backend
python -m uvicorn app.main:app --reload

# Access test pages
http://localhost:8000/visual_trap.html
http://localhost:8000/test_netflix.html
http://localhost:8000/test_google.html
```

### Method 2: Extension Testing
1. Open test page in browser
2. Click PhishGuard extension icon
3. Click "SCAN PAGE"
4. Verify detection results

### Method 3: API Testing
```bash
# Test PayPal page
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "url": "http://192.168.1.1/login",
    "text": "Account Verification Required. We've detected unusual activity. Please verify your account immediately to avoid suspension.",
    "request_id": "test-paypal"
  }'
```

---

## Expected Results

| Test Page | URL Score | Content Score | Visual Score | Final Verdict |
|-----------|-----------|---------------|--------------|---------------|
| PayPal | 60+ (IP) | 50+ (keywords) | 95 (brand mismatch) | PHISHING |
| Netflix | 25+ (TLD) | 40+ (keywords) | 95 (brand mismatch) | PHISHING |
| Google | 30+ (fake domain) | 50+ (keywords) | 95 (brand mismatch) | PHISHING |

---

## Phishing Techniques Demonstrated

### 1. Visual Spoofing
- Exact brand colors (PayPal blue, Netflix red, Google colors)
- Logo mimicry
- UI/UX cloning

### 2. Social Engineering
- Urgency ("immediately", "expired", "suspension")
- Authority (security alerts, verification)
- Fear (account loss, service interruption)

### 3. Technical Deception
- Fake domains
- IP addresses
- Suspicious TLDs (.tk, .ml, etc.)

---

## Testing Checklist

- [ ] Test each page with extension
- [ ] Verify all three risk scores display
- [ ] Check kill switch triggers (score ≥ 75)
- [ ] Confirm keyword chips appear
- [ ] Test with different URLs (IP, fake domain, suspicious TLD)
- [ ] Verify visual analysis detects brand logos
- [ ] Check warning page displays correctly

---

## Adding More Test Pages

### Template Structure
```html
<!DOCTYPE html>
<html>
<head>
    <title>[Brand] - [Action]</title>
    <style>
        /* Brand-specific colors and styling */
    </style>
</head>
<body>
    <!-- Logo/Branding -->
    <!-- Urgency Alert -->
    <!-- Login Form -->
    <!-- Phishing Keywords -->
</body>
</html>
```

### Key Elements
1. **Authentic branding** - Colors, fonts, logos
2. **Urgency message** - Alert box with warning
3. **Credential form** - Email/password inputs
4. **Phishing keywords** - "verify", "urgent", "suspended"
5. **Fake domain** - Non-official URL

---

## Notes

- These pages are for **testing purposes only**
- Do not use for actual phishing attacks
- Helps validate detection accuracy
- Improves training data for ML models
- Tests all three analysis methods (URL, Content, Visual)
