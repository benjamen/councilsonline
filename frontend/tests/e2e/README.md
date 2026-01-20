# SPISC E2E Test Suite

Comprehensive end-to-end tests for SPISC application using Playwright.

## 🚀 Quick Start - Run After Every Code Change

```bash
cd /workspace/development/frappe-bench/apps/councilsonline/frontend/tests/e2e
./run-all-spisc-tests.sh
```

This master script runs:
- ✅ 10 entry point & authentication tests
- ✅ 1 complete submission test (login → fill form → upload → submit)
- ✅ Verifies file upload bug fix

**Total: 11 tests covering all SPISC functionality**

---

## 📋 Test Suites

### 1️⃣ Complete Submission Test (`spisc-complete-submission.spec.js`)

Tests the entire SPISC application flow end-to-end:

**Coverage:**
- ✅ Login at `/frontend/login`
- ✅ Navigate to SPISC application
- ✅ **Step 1**: Personal Information (name, DOB, sex, civil status, mobile, address with province/municipality/barangay)
- ✅ **Step 2**: Household Information (size, living arrangement, income)
- ✅ **Step 3**: Identity Verification (optional fields)
- ✅ **Step 4**: Document Uploads (6 files: cert of indigency, birth cert, valid ID, photo, medical cert, indigency cert)
- ✅ **Step 5**: Declaration & Submission (checkboxes + signature)
- ✅ **Submit** application successfully

**File Upload Bug Fix Verified:**
- All file uploads converted from arrays to URL strings
- No 417 errors
- No "cannot be a list" errors

**Run:**
```bash
npx playwright test spisc-complete-submission.spec.js --project=chromium-desktop
```

**Watch it run:**
```bash
npx playwright test spisc-complete-submission.spec.js --headed --project=chromium-desktop
```

---

### 2️⃣ Entry Points & Authentication Tests (`spisc-entry-points.spec.js`)

Tests all 10 ways users can access SPISC:

| # | Entry Point | What It Tests | Status |
|---|-------------|---------------|--------|
| 1 | Council Portal Homepage | Navigation from portal | ✅ |
| 2 | Direct URL to New Request | `/request/new?council=X` | ✅ |
| 3 | Direct URL with Type | `/request/new?council=X&type=SPISC` | ✅ |
| 4 | Browser Back/Forward | History navigation | ✅ |
| 5 | Bookmark/Saved Link | Cold start access | ✅ |
| 6 | Logout & Re-login | Session clearing | ✅ |
| 7 | Multiple Tabs | Session sharing | ✅ |
| 8 | Session Expiry | Auth token handling | ✅ |
| 9 | Deep Links | Email notification links | ✅ |
| 10 | Invalid URLs | Error handling | ✅ |

**Run:**
```bash
npx playwright test spisc-entry-points.spec.js --project=chromium-desktop
```

**Run specific entry point:**
```bash
npx playwright test spisc-entry-points.spec.js -g "Entry Point 2" --project=chromium-desktop
```

---

## 🔧 Reusable Test Fixtures

### Authentication (`fixtures/auth.js`)

```javascript
import { login, logout, ensureLoggedIn } from './fixtures/auth.js'

// Login
await login(page, {
    username: 'Administrator',
    password: 'admin123',
    baseUrl: 'http://localhost:8080'
})

// Logout
await logout(page)

// Ensure logged in (login if needed)
await ensureLoggedIn(page, { baseUrl: 'http://localhost:8080' })
```

### Request Flow (`fixtures/request-flow.js`)

```javascript
import {
    navigateToNewRequest,
    selectRequestType,
    clickNext,
    clickUnderstandButton,
    startSPISCApplication
} from './fixtures/request-flow.js'

// Complete SPISC navigation
await startSPISCApplication(page, {
    councilCode: 'TAYTAY-PH',
    baseUrl: 'http://localhost:8080'
})
```

### SPISC Form Data (`fixtures/spisc-data.js`)

```javascript
import {
    fillPersonalInformation,
    fillHouseholdInformation,
    fillDeclaration,
    uploadSPISCDocuments,
    fillCompleteSPISCForm
} from './fixtures/spisc-data.js'

// Fill individual steps
await fillPersonalInformation(page)
await fillHouseholdInformation(page)
await fillDeclaration(page, testImagePath)

// Upload documents
await uploadSPISCDocuments(page, testImagePath)

// Fill entire form at once
await fillCompleteSPISCForm(page, testImagePath)
```

---

## 🎯 Running Tests

### Run All Tests (Recommended)
```bash
./run-all-spisc-tests.sh
```

### Run Individual Test Suites
```bash
# Complete submission test
npx playwright test spisc-complete-submission.spec.js --project=chromium-desktop

# Entry points test
npx playwright test spisc-entry-points.spec.js --project=chromium-desktop

# All SPISC tests
npx playwright test spisc-*.spec.js --project=chromium-desktop
```

### Visual/Headed Mode (Watch Browser)
```bash
npx playwright test spisc-complete-submission.spec.js --headed --project=chromium-desktop
```

### Run Specific Test
```bash
npx playwright test spisc-entry-points.spec.js -g "Direct URL" --project=chromium-desktop
```

### Parallel Execution
```bash
npx playwright test spisc-*.spec.js --workers=4 --project=chromium-desktop
```

### Generate HTML Report
```bash
npx playwright test spisc-*.spec.js --project=chromium-desktop --reporter=html
npx playwright show-report
```

---

## 🐛 File Upload Bug Fix (Verified)

### The Bug
File uploads were being saved as arrays instead of URL strings:
```javascript
// WRONG (caused 417 errors):
"indigency_certificate": [
    {
        "file": {},
        "file_url": "/files/test-upload.png"
    }
]

// CORRECT (what backend expects):
"indigency_certificate": "/files/test-upload.png"
```

### The Fix
**File:** `src/stores/requestStore.js`

Added sanitization logic to convert file arrays to URL strings before sending to API:

```javascript
// Convert file arrays to URL strings (Bug #6 fix)
if (Array.isArray(value) && value.length > 0) {
    const isFileArray = value.some(item => item && typeof item === 'object' && item.file_url)
    if (isFileArray) {
        const fileUrl = value[0].file_url
        if (fileUrl && typeof fileUrl === 'string') {
            console.log(`[RequestStore] Converting file array to URL string for ${key}:`, fileUrl)
            sanitizedData[key] = fileUrl
            continue
        }
    }
}
```

### Verification
The complete submission test verifies:
- ✅ No 417 errors
- ✅ No "cannot be a list" errors
- ✅ All files stored as URL strings
- ✅ Application submits successfully

**Last verified:** SPISC-2025-230 submitted successfully

---

## 📊 Test Results Summary

**Last Run:** 2025-12-17

| Test Suite | Tests | Passed | Duration |
|------------|-------|--------|----------|
| Entry Points & Auth | 10 | ✅ 10 | 2.2 min |
| Complete Submission | 1 | ✅ 1 | 1.0 min |
| **TOTAL** | **11** | **✅ 11** | **~3 min** |

---

## 📝 Key Findings

### Authentication Behavior
- ✅ Login required for protected routes
- ✅ Session persists across page navigation
- ✅ Session shared across multiple tabs
- ⚠️ Logout may not fully clear cookies (design decision)
- ⚠️ No immediate redirect on session expiry (checked at API level)

### URL Handling
- ✅ Direct URLs with parameters work
- ✅ Browser back/forward maintains state
- ✅ Invalid parameters show errors
- ✅ Deep links redirect to login when unauthenticated

---

## 🔍 Troubleshooting

### Servers Not Running
```bash
# Start backend
cd /workspace/development/frappe-bench
bench start

# Start frontend (in another terminal)
cd apps/councilsonline/frontend
npm run dev
```

### Test Fails on Login
- Check password is `admin123` (not `admin`)
- Verify frontend is on port `8080`
- Check auth.js fixture is using correct URL

### File Upload Test Fails
- Ensure requestStore.js has file array sanitization
- Check browser console for file upload errors
- Verify test image is being created

---

## 📚 Documentation

- **[Entry Points Test Details](./README-ENTRY-POINTS.md)** - Detailed documentation of all 10 entry point tests
- **Test Runner Script**: `run-all-spisc-tests.sh` - Master test runner
- **Fixtures**: Reusable test components in `fixtures/` directory

---

## ✅ Checklist: When to Run Tests

Run the full test suite:
- ✅ After changing authentication code
- ✅ After changing routing/navigation
- ✅ After changing form fields
- ✅ After changing file upload logic
- ✅ Before committing code
- ✅ Before deploying to production

---

## 🎓 Test Development Guidelines

1. **Use Fixtures**: Reuse common functionality from `fixtures/`
2. **Add Logging**: Capture console logs for debugging
3. **Document**: Comment complex test logic
4. **Descriptive Names**: Use clear test descriptions
5. **Wait Properly**: Use appropriate waits for async operations
6. **Clean Up**: Close contexts/pages when done

---

## 🚀 Next Steps

After tests pass, you can:
1. Check backend for submitted application (e.g., SPISC-2025-230)
2. Verify all files are URL strings in database
3. Deploy changes with confidence
4. Add these tests to CI/CD pipeline

---

**Remember:** Run `./run-all-spisc-tests.sh` after every code change! 🎯
