# Dual Login System - Enhancement Implementation Guide

This document provides detailed implementation guides for the remaining enhancement features for the dual login system.

## ✅ Implemented Features

1. **Login Analytics** - ✅ Complete
   - Tracks system-wide vs council-specific logins
   - Records IP, user agent, timestamp
   - Provides aggregated analytics API
   - See commit: f377090

---

## 📋 Remaining Enhancements

### 2. Email Customization - Council-Branded Email Templates

**Goal**: Send council-branded emails for password reset, welcome emails, and notifications.

#### Backend Implementation

**Step 1: Create Email Template DocType Extension**

```python
# In lodgeick/api.py

@frappe.whitelist()
def get_council_email_template(council_code, template_type):
    """
    Get council-specific email template

    Args:
        council_code: Council code
        template_type: 'password_reset', 'welcome', 'notification'

    Returns:
        dict: Template data with subject, body, footer
    """
    try:
        council = frappe.get_doc("Council", council_code)

        # Check if council has custom email settings
        if hasattr(council, f'{template_type}_email_subject'):
            return {
                "subject": getattr(council, f'{template_type}_email_subject'),
                "body": getattr(council, f'{template_type}_email_body'),
                "footer": council.email_footer or get_default_footer(),
                "logo": council.logo,
                "primary_color": council.primary_color
            }

        # Fall back to default template
        return get_default_email_template(template_type)

    except frappe.DoesNotExistError:
        return get_default_email_template(template_type)


@frappe.whitelist()
def send_council_email(council_code, email_type, recipient, **kwargs):
    """
    Send council-branded email

    Args:
        council_code: Council code
        email_type: Type of email (password_reset, welcome, etc)
        recipient: Recipient email address
        **kwargs: Additional template variables
    """
    template = get_council_email_template(council_code, email_type)

    # Render template with variables
    from jinja2 import Template

    subject = Template(template['subject']).render(**kwargs)
    body = Template(template['body']).render(
        council_name=template.get('council_name'),
        logo=template.get('logo'),
        primary_color=template.get('primary_color'),
        **kwargs
    )

    # Send email
    frappe.sendmail(
        recipients=[recipient],
        subject=subject,
        message=body,
        header=[template.get('subject'), 'green']
    )
```

**Step 2: Add Email Template Fields to Council DocType**

```json
{
  "fieldname": "email_settings_section",
  "fieldtype": "Section Break",
  "label": "Email Settings"
},
{
  "fieldname": "email_footer",
  "fieldtype": "HTML Editor",
  "label": "Email Footer"
},
{
  "fieldname": "password_reset_email_subject",
  "fieldtype": "Data",
  "label": "Password Reset Email Subject",
  "default": "Reset Your Password - {{council_name}}"
},
{
  "fieldname": "password_reset_email_body",
  "fieldtype": "HTML Editor",
  "label": "Password Reset Email Body"
},
{
  "fieldname": "welcome_email_subject",
  "fieldtype": "Data",
  "label": "Welcome Email Subject",
  "default": "Welcome to {{council_name}}"
},
{
  "fieldname": "welcome_email_body",
  "fieldtype": "HTML Editor",
  "label": "Welcome Email Body"
}
```

**Step 3: Override Frappe's Password Reset**

```python
# In lodgeick/hooks.py

override_whitelisted_methods = {
    "frappe.core.doctype.user.user.reset_password": "lodgeick.api.council_reset_password"
}
```

```python
# In lodgeick/api.py

@frappe.whitelist(allow_guest=True)
def council_reset_password(user, council_code=None):
    """
    Override Frappe's reset_password to send council-branded email
    """
    from frappe.core.doctype.user import user as user_module

    # Generate reset token (use Frappe's existing logic)
    key = user_module.generate_keys(user)

    if council_code:
        # Send council-branded email
        send_council_email(
            council_code=council_code,
            email_type='password_reset',
            recipient=user,
            reset_link=get_reset_password_link(key),
            user_name=frappe.db.get_value("User", user, "full_name")
        )
    else:
        # Fall back to default Frappe email
        user_module.reset_password(user)
```

**Step 4: Frontend Integration**

Update `CouncilForgotPassword.vue`:

```javascript
async function submit() {
  errorMessage.value = ''
  isLoading.value = true

  try {
    await call('lodgeick.api.council_reset_password', {
      user: email.value,
      council_code: councilCode.value  // Pass council code
    })
    emailSent.value = true
  } catch (error) {
    errorMessage.value = error.message || 'Failed to send reset email.'
  } finally {
    isLoading.value = false
  }
}
```

#### Email Template Examples

**Password Reset Template**:
```html
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; }
        .header { background-color: {{primary_color}}; padding: 20px; text-align: center; }
        .content { padding: 30px; }
        .button { background-color: {{primary_color}}; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; }
    </style>
</head>
<body>
    <div class="header">
        <img src="{{logo}}" alt="{{council_name}}" height="60">
    </div>
    <div class="content">
        <h2>Reset Your Password</h2>
        <p>Hello {{user_name}},</p>
        <p>We received a request to reset your password for your {{council_name}} account.</p>
        <p><a href="{{reset_link}}" class="button">Reset Password</a></p>
        <p>This link will expire in 24 hours.</p>
        <p>If you didn't request this, please ignore this email.</p>
    </div>
    <div class="footer">
        {{email_footer}}
    </div>
</body>
</html>
```

---

### 3. Custom Domains - Council-Specific Domain Support

**Goal**: Allow councils to use their own domains (e.g., auckland-council.com) while maintaining council context.

#### Backend Implementation

**Step 1: Domain Mapping API**

```python
# In lodgeick/api.py

@frappe.whitelist(allow_guest=True)
def get_council_by_domain(domain):
    """
    Get council code by custom domain

    Args:
        domain: Custom domain (e.g., 'auckland-council.com')

    Returns:
        dict: Council data including code
    """
    council = frappe.get_all(
        "Council",
        filters={"custom_domain": domain},
        fields=["council_code", "council_name", "primary_color", "logo"],
        limit=1
    )

    if council:
        return council[0]

    return None


@frappe.whitelist()
def register_custom_domain(council_code, domain):
    """
    Register custom domain for a council

    Validates:
    - Domain format
    - Domain uniqueness
    - DNS configuration
    """
    import re

    # Validate domain format
    domain_pattern = r'^([a-z0-9]+(-[a-z0-9]+)*\.)+[a-z]{2,}$'
    if not re.match(domain_pattern, domain.lower()):
        frappe.throw("Invalid domain format")

    # Check uniqueness
    existing = frappe.db.exists("Council", {"custom_domain": domain})
    if existing and existing != council_code:
        frappe.throw(f"Domain {domain} is already registered")

    # Update council
    council = frappe.get_doc("Council", council_code)
    council.custom_domain = domain
    council.save()

    return {"success": True, "domain": domain}
```

**Step 2: Middleware for Domain Detection**

```python
# In lodgeick/hooks.py

before_request = [
    "lodgeick.api.detect_council_domain"
]
```

```python
# In lodgeick/api.py

def detect_council_domain():
    """
    Detect if request is from a custom council domain
    Set council context in request
    """
    import frappe
    from urllib.parse import urlparse

    # Get request domain
    host = frappe.request.headers.get('Host', '').split(':')[0]

    # Check if custom domain
    council = get_council_by_domain(host)

    if council:
        # Set council context for this request
        frappe.local.council_code = council['council_code']
        frappe.local.is_custom_domain = True
```

**Step 3: Frontend Router Guard**

Add to `router.js` `beforeEach`:

```javascript
router.beforeEach(async (to, from, next) => {
  const councilStore = useCouncilStore()

  // Check if on custom domain
  const hostname = window.location.hostname

  // Skip localhost/IP addresses
  if (!hostname.includes('localhost') && !hostname.match(/^\d+\.\d+\.\d+\.\d+$/)) {
    try {
      const council = await call('lodgeick.api.get_council_by_domain', {
        domain: hostname
      })

      if (council) {
        // Auto-lock to this council
        await councilStore.setLockedCouncil(council.council_code)

        // Redirect to council landing if on root
        if (to.path === '/') {
          next({ name: 'CouncilLanding', params: { councilCode: council.council_code } })
          return
        }
      }
    } catch (error) {
      console.error('Failed to detect custom domain:', error)
    }
  }

  // Continue with existing logic...
  next()
})
```

#### DNS Configuration

**For Councils Using Custom Domains**:

1. **CNAME Record**:
   ```
   auckland-council.com → lodgeick.com
   ```

2. **SSL Certificate**:
   - Use Let's Encrypt with wildcard support
   - Or council-specific certificates

3. **Nginx Configuration**:
   ```nginx
   server {
       listen 443 ssl;
       server_name auckland-council.com;

       ssl_certificate /path/to/cert.pem;
       ssl_certificate_key /path/to/key.pem;

       location / {
           proxy_pass http://localhost:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
       }
   }
   ```

---

### 4. SSO Support - OAuth/SAML Integration

**Goal**: Allow councils to configure their own SSO providers (Azure AD, Google Workspace, SAML).

#### Backend Implementation

**Step 1: OAuth Provider Configuration**

Add to Council DocType:

```json
{
  "fieldname": "sso_settings_section",
  "fieldtype": "Section Break",
  "label": "SSO Settings"
},
{
  "fieldname": "enable_sso",
  "fieldtype": "Check",
  "label": "Enable SSO",
  "default": "0"
},
{
  "fieldname": "sso_provider",
  "fieldtype": "Select",
  "label": "SSO Provider",
  "options": "\nGoogle\nMicrosoft Azure AD\nOkta\nSAML 2.0",
  "depends_on": "eval:doc.enable_sso==1"
},
{
  "fieldname": "oauth_client_id",
  "fieldtype": "Data",
  "label": "OAuth Client ID",
  "depends_on": "eval:doc.enable_sso==1 && doc.sso_provider!='SAML 2.0'"
},
{
  "fieldname": "oauth_client_secret",
  "fieldtype": "Password",
  "label": "OAuth Client Secret",
  "depends_on": "eval:doc.enable_sso==1 && doc.sso_provider!='SAML 2.0'"
},
{
  "fieldname": "saml_metadata_url",
  "fieldtype": "Data",
  "label": "SAML Metadata URL",
  "depends_on": "eval:doc.enable_sso==1 && doc.sso_provider=='SAML 2.0'"
}
```

**Step 2: OAuth Flow Implementation**

```python
# In lodgeick/api.py

@frappe.whitelist(allow_guest=True)
def initiate_council_sso(council_code, provider):
    """
    Initiate SSO login for a council

    Args:
        council_code: Council code
        provider: SSO provider (google, azure, okta, saml)

    Returns:
        dict: Authorization URL and state
    """
    import secrets
    from urllib.parse import urlencode

    council = frappe.get_doc("Council", council_code)

    if not council.enable_sso:
        frappe.throw("SSO not enabled for this council")

    # Generate state token for CSRF protection
    state = secrets.token_urlsafe(32)

    # Store state in cache
    frappe.cache().setex(
        f"sso_state:{state}",
        600,  # 10 minutes
        {"council_code": council_code, "provider": provider}
    )

    # Build authorization URL based on provider
    if provider == 'Google':
        auth_url = build_google_auth_url(council, state)
    elif provider == 'Microsoft Azure AD':
        auth_url = build_azure_auth_url(council, state)
    elif provider == 'SAML 2.0':
        auth_url = build_saml_auth_url(council, state)
    else:
        frappe.throw(f"Unsupported SSO provider: {provider}")

    return {
        "authorization_url": auth_url,
        "state": state
    }


def build_google_auth_url(council, state):
    """Build Google OAuth URL"""
    from urllib.parse import urlencode

    params = {
        "client_id": council.oauth_client_id,
        "redirect_uri": f"{frappe.utils.get_url()}/api/method/lodgeick.api.sso_callback",
        "scope": "openid email profile",
        "response_type": "code",
        "state": state
    }

    return f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"


@frappe.whitelist(allow_guest=True)
def sso_callback(code, state):
    """
    Handle SSO callback

    Args:
        code: Authorization code
        state: State token

    Returns:
        Redirects to council dashboard with session
    """
    # Verify state
    cached_state = frappe.cache().get(f"sso_state:{state}")
    if not cached_state:
        frappe.throw("Invalid or expired state token")

    council_code = cached_state['council_code']
    provider = cached_state['provider']

    # Exchange code for token
    if provider == 'Google':
        user_info = exchange_google_code(code, council_code)
    elif provider == 'Microsoft Azure AD':
        user_info = exchange_azure_code(code, council_code)

    # Find or create user
    user_email = user_info['email']

    if not frappe.db.exists("User", user_email):
        # Create user
        user = frappe.get_doc({
            "doctype": "User",
            "email": user_email,
            "first_name": user_info.get('given_name', ''),
            "last_name": user_info.get('family_name', ''),
            "enabled": 1,
            "user_type": "Website User",
            "default_council": council_code
        })
        user.insert(ignore_permissions=True)

    # Log in user
    frappe.local.login_manager.login_as(user_email)

    # Track login
    track_login_event('council-specific', council_code)

    # Redirect to council dashboard
    return frappe.utils.get_url(f"/frontend/council/{council_code}/dashboard")
```

**Step 3: Frontend SSO Button**

Add to `CouncilLogin.vue`:

```vue
<template>
  <!-- After regular login form -->

  <div v-if="councilSettings?.enable_sso" class="mt-6">
    <div class="relative">
      <div class="absolute inset-0 flex items-center">
        <div class="w-full border-t border-gray-300"></div>
      </div>
      <div class="relative flex justify-center text-sm">
        <span class="px-2 bg-white text-gray-500">Or continue with</span>
      </div>
    </div>

    <button
      @click="initiateSSO"
      class="mt-4 w-full flex items-center justify-center gap-2 px-4 py-3 border border-gray-300 rounded-lg hover:bg-gray-50"
    >
      <img v-if="ssoProviderLogo" :src="ssoProviderLogo" class="h-5 w-5" />
      <span>Sign in with {{ councilSettings.sso_provider }}</span>
    </button>
  </div>
</template>

<script setup>
async function initiateSSO() {
  try {
    const response = await call('lodgeick.api.initiate_council_sso', {
      council_code: councilCode.value,
      provider: councilSettings.value.sso_provider
    })

    // Redirect to OAuth provider
    window.location.href = response.authorization_url
  } catch (error) {
    console.error('SSO initiation failed:', error)
  }
}

const ssoProviderLogo = computed(() => {
  const logos = {
    'Google': '/assets/lodgeick/images/google-logo.svg',
    'Microsoft Azure AD': '/assets/lodgeick/images/microsoft-logo.svg',
    'Okta': '/assets/lodgeick/images/okta-logo.svg'
  }
  return logos[councilSettings.value?.sso_provider]
})
</script>
```

---

### 5. Mobile App - Deep Linking Support

**Goal**: Support deep links from mobile apps to council-specific authentication flows.

#### Deep Link URL Scheme

```
lodgeick://council/AKL/login
lodgeick://council/AKL/register
lodgeick://council/AKL/dashboard
lodgeick://council/AKL/request/new
```

#### Backend Implementation

**Step 1: Deep Link Handler**

```python
# In lodgeick/api.py

@frappe.whitelist(allow_guest=True)
def handle_deep_link(action, council_code, **params):
    """
    Handle deep link from mobile app

    Args:
        action: Action to perform (login, register, dashboard, etc)
        council_code: Council code
        **params: Additional parameters

    Returns:
        dict: Redirect URL and metadata
    """
    # Validate council exists
    if not frappe.db.exists("Council", council_code):
        frappe.throw(f"Invalid council code: {council_code}")

    # Build web URL based on action
    base_url = frappe.utils.get_url()

    action_map = {
        'login': f'/frontend/council/{council_code}/login',
        'register': f'/frontend/council/{council_code}/register',
        'dashboard': f'/frontend/council/{council_code}/dashboard',
        'request_new': f'/frontend/request/new?council={council_code}&locked=true',
        'forgot_password': f'/frontend/council/{council_code}/forgot-password'
    }

    path = action_map.get(action)
    if not path:
        frappe.throw(f"Invalid deep link action: {action}")

    return {
        "url": f"{base_url}{path}",
        "council_code": council_code,
        "action": action
    }
```

#### Mobile App Integration (React Native Example)

**Step 2: Deep Link Configuration**

```javascript
// In mobile app (React Native)
import { Linking } from 'react-native'
import { useNavigation } from '@react-navigation/native'

// Configure deep linking
const linking = {
  prefixes: ['lodgeick://', 'https://lodgeick.com'],
  config: {
    screens: {
      CouncilAuth: 'council/:councilCode/:action'
    }
  }
}

// Handle incoming deep links
useEffect(() => {
  const handleDeepLink = async (event) => {
    const url = event.url
    const { councilCode, action } = parseDeepLink(url)

    // Call backend to get redirect URL
    const response = await fetch(
      `https://lodgeick.com/api/method/lodgeick.api.handle_deep_link`,
      {
        method: 'POST',
        body: JSON.stringify({ action, council_code: councilCode })
      }
    )

    const data = await response.json()

    // Open web view or native screen
    if (hasNativeScreen(action)) {
      navigation.navigate(getNativeScreen(action), { councilCode })
    } else {
      openWebView(data.url)
    }
  }

  Linking.addEventListener('url', handleDeepLink)

  return () => Linking.removeAllListeners('url')
}, [])
```

**Step 3: Universal Links (iOS) / App Links (Android)**

**iOS Configuration** (`apple-app-site-association`):
```json
{
  "applinks": {
    "apps": [],
    "details": [
      {
        "appID": "TEAM_ID.com.lodgeick.app",
        "paths": [
          "/council/*/login",
          "/council/*/register",
          "/council/*/dashboard"
        ]
      }
    ]
  }
}
```

**Android Configuration** (`AndroidManifest.xml`):
```xml
<intent-filter android:autoVerify="true">
    <action android:name="android.intent.action.VIEW" />
    <category android:name="android.intent.category.DEFAULT" />
    <category android:name="android.intent.category.BROWSABLE" />
    <data
        android:scheme="https"
        android:host="lodgeick.com"
        android:pathPrefix="/council" />
</intent-filter>
```

**Step 4: QR Code Generation**

```python
# In lodgeick/api.py

@frappe.whitelist()
def generate_council_qr_code(council_code, action='login'):
    """
    Generate QR code for mobile app deep link

    Args:
        council_code: Council code
        action: Deep link action

    Returns:
        str: Base64 encoded QR code image
    """
    import qrcode
    import io
    import base64

    # Build deep link URL
    deep_link = f"lodgeick://council/{council_code}/{action}"

    # Generate QR code
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(deep_link)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    # Convert to base64
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode()

    return f"data:image/png;base64,{img_str}"
```

**Frontend QR Code Display**:

Add to `CouncilLandingPage.vue`:

```vue
<template>
  <div class="mobile-app-section">
    <h3>Download Our Mobile App</h3>
    <p>Scan to login on mobile</p>
    <img :src="qrCode" alt="QR Code" class="w-48 h-48" />
  </div>
</template>

<script setup>
const qrCode = ref(null)

onMounted(async () => {
  qrCode.value = await call('lodgeick.api.generate_council_qr_code', {
    council_code: councilCode.value,
    action: 'login'
  })
})
</script>
```

---

## Testing Checklist

### Email Customization
- [ ] Council email templates render correctly
- [ ] Password reset emails contain correct branding
- [ ] Email variables populate properly
- [ ] Fallback to default templates works

### Custom Domains
- [ ] Domain detection works correctly
- [ ] Council auto-locks on custom domain
- [ ] SSL certificates configured
- [ ] DNS records properly set

### SSO Support
- [ ] OAuth flow completes successfully
- [ ] User creation/login works
- [ ] State verification prevents CSRF
- [ ] Multiple providers supported

### Mobile Deep Linking
- [ ] Deep links open correct screens
- [ ] Universal links work on iOS
- [ ] App links work on Android
- [ ] QR codes generate correctly

---

## Deployment Notes

1. **Email Templates**: Requires SMTP configuration
2. **Custom Domains**: Requires DNS management and SSL certificates
3. **SSO**: Requires OAuth app registration with each provider
4. **Mobile App**: Requires app store deployment

---

## Support & Maintenance

For questions or issues implementing these features, refer to:
- Frappe Framework documentation: https://frappeframework.com
- OAuth 2.0 spec: https://oauth.net/2/
- SAML 2.0 spec: http://docs.oasis-open.org/security/saml/

---

**Document Version**: 1.0
**Last Updated**: 2025-01-08
**Maintainer**: Lodgeick Development Team
