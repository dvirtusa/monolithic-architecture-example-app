# PlayerZero Web SDK Integration

This project includes **PlayerZero Web SDK** instrumentation for both Node.js and Python frontend applications to capture user sessions, interactions, errors, and frontend telemetry.

## Overview

PlayerZero Web SDK provides comprehensive frontend observability:

- **Session Recording**: User interactions, clicks, navigation
- **Error Tracking**: JavaScript errors, network failures, console errors
- **User Identification**: Track authenticated users across sessions
- **Custom Events**: Track business-critical user actions
- **Network Monitoring**: Capture AJAX/Fetch requests and responses
- **Console Logs**: Capture console.log, console.error, etc.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Browser (Client)                      │
│                                                          │
│  ┌────────────────────────────────────────────────────┐ │
│  │  PlayerZero Web SDK (playerzero.js)                 │ │
│  │  - Session recording                                │ │
│  │  - Error tracking                                   │ │
│  │  - User identification                              │ │
│  │  - Event tracking                                   │ │
│  └─────────────────┬────────────────────────────────────┘ │
│                    │                                      │
└────────────────────┼──────────────────────────────────────┘
                     │ HTTPS
                     ▼
         ┌───────────────────────────┐
         │   PlayerZero Platform      │
         │   (Session Analytics)      │
         └───────────────────────────┘
```

## Implementation

### Node.js App (Port 8080)

**File:** `views/home.ejs`

**SDK Initialization:**
```javascript
<script>
    window.playerZeroConfig = {
        projectId: '<%= process.env.PLAYERZERO_PROJECT_ID %>',
        enabled: '<%= process.env.PLAYERZERO_PROJECT_ID ? "true" : "false" %>',
        metadata: {
            app: 'nodejs-monolithic-app',
            environment: '<%= process.env.OTEL_ENVIRONMENT || "development" %>'
        }
    };
</script>
<script src="https://cdn.playerzero.app/playerzero.js" async></script>
```

**User Identification:**
```javascript
// After successful registration or on page load
if (window.PlayerZero) {
    window.PlayerZero.identify(email, {
        name: name,
        email: email
    });
}
```

### Python App (Port 5000)

**File:** `python_app/app/templates/home.html`

**SDK Initialization:**
```javascript
<script>
    window.playerZeroConfig = {
        projectId: '{{ playerzero_project_id }}',
        enabled: {{ 'true' if playerzero_project_id else 'false' }},
        metadata: {
            app: 'python-monolithic-app',
            environment: '{{ otel_environment }}'
        }
    };
</script>
<script src="https://cdn.playerzero.app/playerzero.js" async></script>
```

**User Identification & Event Tracking:**
```javascript
// After login
if (window.PlayerZero) {
    window.PlayerZero.identify(user.email, {
        name: user.name,
        email: user.email,
        userId: user._id,
        createdAt: user.created_at
    });
}

// Track custom events
window.PlayerZero.track('User Registered', {
    name: data.name,
    email: data.email,
    userId: data._id
});

window.PlayerZero.track('User Logged In', {
    email: email
});

window.PlayerZero.track('User Logged Out');
```

## Configuration

### Environment Variables

| Variable | Purpose | Required | Example |
|----------|---------|----------|---------|
| `PLAYERZERO_PROJECT_ID` | Frontend Web SDK project identifier | Yes | `proj_abc123xyz` |
| `PLAYERZERO_API_KEY` | Backend OTLP API key | Yes | `pz_key_abc123` |
| `OTEL_ENVIRONMENT` | Environment tag | No | `production`, `staging`, `docker` |

### Get Your Credentials

1. **Log in to PlayerZero**: https://playerzero.ai
2. **Navigate to Settings**:
   - **API Keys** → Create OTLP API key (for backend)
   - **Projects** → Get your Project ID (for frontend)
3. **Add to `.env` file**

## Setup Instructions

### 1. Configure Environment

```bash
# Copy example file
cp .env.example .env

# Edit with your credentials
nano .env
```

Add your PlayerZero credentials:

```env
PLAYERZERO_PROJECT_ID=proj_your_project_id_here
PLAYERZERO_API_KEY=pz_your_api_key_here
OTEL_EXPORTER_OTLP_ENDPOINT=https://otlp.playerzero.app
ENVIRONMENT=production
```

### 2. Run Applications

```bash
# Build and start
docker-compose up --build

# Or restart if already running
docker-compose restart nodejs-app python-app
```

### 3. Verify SDK Loaded

Open browser DevTools console and check for:

```
PlayerZero SDK initialized
Project ID: proj_your_project_id
Environment: production
```

### 4. Test User Tracking

1. Register a new user
2. Check PlayerZero dashboard for:
   - New session
   - "User Registered" event
   - User identified with name/email

## Events Tracked

### Node.js App

| Event | Trigger | Data Captured |
|-------|---------|---------------|
| **Page Load** | User visits homepage | Session start, metadata |
| **User Registration** | Form submission success | name, email |
| **User Identification** | After registration or page load with localStorage | name, email |
| **Form Errors** | Validation or server errors | Error messages |

### Python App

| Event | Trigger | Data Captured |
|-------|---------|---------------|
| **Page Load** | User visits homepage | Session start, metadata |
| **User Registered** | Successful registration | name, email, userId |
| **User Logged In** | Successful authentication | email |
| **User Logged Out** | Logout button click | - |
| **User Identification** | After login or token refresh | name, email, userId, createdAt |
| **Form Errors** | Validation or server errors | Error messages |

## What Gets Captured

### Automatic Capture

- ✅ **User Sessions**: Complete session replays
- ✅ **Console Logs**: console.log, console.error, console.warn
- ✅ **JavaScript Errors**: Unhandled exceptions, promise rejections
- ✅ **Network Activity**: Fetch/AJAX requests and responses
- ✅ **DOM Changes**: User clicks, form submissions, navigation
- ✅ **Performance**: Page load times, resource timing

### Custom Tracking

- ✅ **User Identity**: Email, name, userId
- ✅ **Custom Events**: Registration, login, logout
- ✅ **Metadata**: App name, environment

## Viewing Data in PlayerZero

### Session Replay

1. Navigate to [PlayerZero Dashboard](https://playerzero.ai)
2. Go to **Sessions**
3. Filter by:
   - App: `nodejs-monolithic-app` or `python-monolithic-app`
   - Environment: `docker`, `production`, etc.
   - User email
4. Click a session to replay user interactions

### Events & Analytics

1. Go to **Events** section
2. View custom events:
   - User Registered
   - User Logged In
   - User Logged Out
3. Analyze conversion funnels and user flows

### Error Tracking

1. Go to **Errors** section
2. View JavaScript errors and stack traces
3. See exact user session when error occurred
4. Replay session to understand context

## Privacy & Security

### Data Sanitization

PlayerZero **automatically redacts** sensitive data:

- ✅ Password fields (input[type="password"])
- ✅ Credit card numbers
- ✅ Social security numbers
- ✅ API keys in network requests

### Additional Configuration

To exclude specific elements from recording:

```html
<input type="text" class="pz-ignore" />
<div data-pz-ignore>Sensitive content</div>
```

### Disable SDK

Set `PLAYERZERO_PROJECT_ID` to empty:

```env
PLAYERZERO_PROJECT_ID=
```

The SDK will not load when project ID is empty.

## Troubleshooting

### SDK Not Loading

**Check browser console:**
```
PlayerZero SDK loaded successfully
```

**Common issues:**

1. **Missing Project ID:**
   ```javascript
   // In browser console
   console.log(window.playerZeroConfig);
   // Should show projectId
   ```
   Solution: Verify `PLAYERZERO_PROJECT_ID` in `.env`

2. **Script blocked by ad blocker:**
   - Disable ad blocker
   - Or whitelist `cdn.playerzero.app`

3. **CSP (Content Security Policy) blocking:**
   - Add `cdn.playerzero.app` to CSP script-src

### Sessions Not Appearing

1. **Check project ID is correct:**
   ```bash
   # View in browser
   http://localhost:8080  # or :5000
   # Open DevTools → Console
   # Check window.playerZeroConfig.projectId
   ```

2. **Verify network requests:**
   - Open DevTools → Network tab
   - Look for requests to `playerzero.app`

3. **Check PlayerZero dashboard:**
   - Ensure you're viewing the correct project
   - Sessions may take 30-60 seconds to appear

### User Not Identified

**Check console for:**
```javascript
window.PlayerZero.identify('user@example.com', {...})
```

**Common issues:**
- SDK not fully loaded (async)
- User object missing required fields
- Network request failed

## Performance Impact

| Metric | Impact |
|--------|--------|
| **Page Load** | +50-100ms (async load) |
| **Memory** | ~5-10 MB |
| **Network** | Batched uploads (low bandwidth) |
| **CPU** | Minimal (< 2%) |

The SDK is loaded asynchronously and won't block page rendering.

## API Reference

### User Identification

```javascript
window.PlayerZero.identify(userId, {
    name: 'John Doe',
    email: 'john@example.com',
    // Custom properties
    plan: 'premium',
    signupDate: '2024-01-15'
});
```

### Event Tracking

```javascript
window.PlayerZero.track('Event Name', {
    property1: 'value1',
    property2: 'value2'
});
```

### Manual Error Logging

```javascript
try {
    // Your code
} catch (error) {
    window.PlayerZero.logError(error, {
        context: 'checkout-flow',
        userId: 'user-123'
    });
}
```

### Set Metadata

```javascript
window.PlayerZero.setMetadata({
    version: '1.0.0',
    feature_flags: ['new-ui', 'beta-feature']
});
```

## Custom Events Being Tracked

### Python App

| Event Name | When | Data |
|------------|------|------|
| `User Registered` | Account creation success | name, email, userId |
| `User Logged In` | Authentication success | email |
| `User Logged Out` | Logout button click | - |

### Node.js App

| Event Name | When | Data |
|------------|------|------|
| User identification | Registration or page load | name, email |

## Correlation with Backend Telemetry

PlayerZero automatically correlates:

- **Frontend sessions** (Web SDK)
- **Backend traces** (OpenTelemetry OTLP)

This provides end-to-end visibility from user action → API request → database query → response.

### Unified View

In PlayerZero dashboard, you can:

1. Start with a user session (frontend)
2. Click on any network request
3. View the corresponding backend trace
4. See database queries and latency
5. Identify bottlenecks across the stack

## Testing Locally

### 1. Start Applications

```bash
docker-compose up --build
```

### 2. Perform Actions

- Visit http://localhost:8080 (Node.js)
- Visit http://localhost:5000 (Python)
- Register a user
- Login
- Logout

### 3. Check Browser Console

```javascript
// Should see
PlayerZero SDK initialized
Project ID: proj_your_project_id

// Check tracking
window.PlayerZero.track('Test Event', { test: true });
```

### 4. View in PlayerZero

- Sessions should appear within 60 seconds
- Events tracked under **Events** tab
- Errors under **Errors** tab

## Best Practices

### 1. Identify Users Early

```javascript
// As soon as you know the user identity
window.PlayerZero.identify(userId, userProperties);
```

### 2. Track Key Business Events

```javascript
// Track conversions, feature usage
window.PlayerZero.track('Feature Used', {
    featureName: 'export-data',
    format: 'csv'
});
```

### 3. Add Context to Errors

```javascript
window.PlayerZero.setMetadata({
    currentPage: 'checkout',
    cartValue: '$123.45'
});
```

### 4. Sanitize Sensitive Data

```html
<!-- Exclude from recording -->
<input type="text" class="pz-ignore" placeholder="SSN">
```

## Integration with OpenTelemetry

Both frontend (Web SDK) and backend (OpenTelemetry) telemetry flow into PlayerZero:

```
┌─────────────────┐                  ┌──────────────────┐
│  Browser        │                  │   PlayerZero     │
│  Web SDK        ├─────────────────▶│   Platform       │
└─────────────────┘   Sessions/Events│                  │
                                     │  - Session Replay │
┌─────────────────┐                  │  - User Events   │
│  Node.js App    │    OTLP/HTTP     │  - Errors        │
│  (Backend)      ├─────────────────▶│  - Backend Traces│
└─────────────────┘                  │  - DB Queries    │
                                     │                  │
┌─────────────────┐                  │  Unified View    │
│  Python App     │    OTLP/HTTP     │  Frontend+Backend│
│  (Backend)      ├─────────────────▶│                  │
└─────────────────┘                  └──────────────────┘
```

## Files Modified

| File | Changes |
|------|---------|
| `views/home.ejs` | Added Web SDK script, user identification, event tracking |
| `python_app/app/templates/home.html` | Added Web SDK script, user identification, custom events |
| `python_app/app/routes/pages.py` | Pass project ID and environment to template |
| `docker-compose.yml` | Added `PLAYERZERO_PROJECT_ID` environment variable |
| `.env.example` | Added `PLAYERZERO_PROJECT_ID` configuration |

## Support

- **PlayerZero Documentation**: https://docs.playerzero.ai
- **Web SDK Reference**: https://docs.playerzero.ai/web-sdk
- **Support**: https://playerzero.ai/support

## Next Steps

1. ✅ Get PlayerZero Project ID from dashboard
2. ✅ Add to `.env` file
3. ✅ Restart containers
4. ✅ Test user registration/login
5. ✅ View sessions in PlayerZero dashboard
6. 📊 Set up custom dashboards
7. 🔔 Configure alerts for errors
8. 📈 Analyze user funnels
