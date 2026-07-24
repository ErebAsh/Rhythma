# Rhythma — System Architecture

## Overview

Rhythma follows an **offline-first, privacy-first** architecture designed for low-connectivity environments in tier-2 and tier-3 India.

```
┌────────────────────────────────────────────────────────────────┐
│                        Flutter App                              │
│                                                                 │
│  ┌──────────┐  ┌──────────┐  ┌───────────┐  ┌─────────────┐   │
│  │   Home   │  │  Cycle   │  │ Assistant │  │  Insights   │   │
│  └──────────┘  └──────────┘  └───────────┘  └─────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Hive (Local Storage) ← AES-256 encrypted               │   │
│  └──────────────────────────┬────────────────────────────┘   │
│                             │ sync (when online)              │
└─────────────────────────────┼───────────────────────────────┘
                              │
                    ┌─────────▼──────────┐
                    │   FastAPI Backend   │
                    │                    │
                    │ /assistant ──► Gemini API
                    │ /cycle     ──► Firestore
                    │ /insights  ──► XGBoost + LR models
                    │ /sms       ──► Twilio
                    └────────────────────┘
```

## Data Flow

### Offline Mode
1. User logs cycle data / symptoms → stored in Hive (encrypted locally)
2. CVI / MHS scores computed on-device
3. AI assistant queries cached or gracefully degraded

### Online Mode
1. Hive data syncs to Firestore when connectivity detected
2. Gemini API handles multilingual assistant queries via FastAPI
3. Twilio dispatches weekly SMS summaries

## Privacy Design

- All health data encrypted with AES-256 before being written to Hive
- No data leaves the device unless user explicitly enables cloud sync
- Firestore security rules restrict read/write to authenticated user's own documents
- Backend never stores raw health data in logs

## ML Models

| Model | Purpose | Training Data |
|-------|---------|---------------|
| XGBoost | Cycle Variability Index (CVI) — 0–100 score | Synthetic + anonymized cycle datasets |
| Logistic Regression | Menstrual Health Score (MHS) — 0–100 score | Multi-factor wellness inputs |

Models are exported via `joblib` and bundled for on-device inference (planned: TFLite conversion for Flutter).

## Planned: WhatsApp Integration

```
User (WhatsApp) ──► Twilio / Meta Cloud API ──► FastAPI webhook
                                                      │
                                               Gemini API (multilingual)
                                                      │
                                              Response back to user
```
### Frontend Coexistence & Strategy (`web/` vs `rhythma_flutter/`)

The repository currently contains two frontend implementations:

* **`rhythma_flutter/` (Primary):** The primary cross-platform codebase targeting Android, iOS, and Web. **All new features and user-facing capabilities should be built here.**
* **`web/` (Legacy Scaffold):** A minimal, React-based authentication scaffold (`web/src/pages/HomePage.tsx`) built early in the project to test backend API integration.

> **Target Frontend Policy:**
> `web/` is currently maintained solely as a simple auth scaffold and is planned to be superseded by the official **Flutter Web** build (tracked in [#68](https://github.com/ishita2740/Rhythma/issues/68) / [#142](https://github.com/ishita2740/Rhythma/issues/142)). **Do not add new application features or pages to `web/`.** All new feature development must be directed to `rhythma_flutter/`.
## Known Dev-Only Shortcuts

The following configuration choices and fallbacks are currently enabled to simplify local development, but are **not production-ready**.

| Dev Shortcut | File / Location | Why it's for Dev Only | Production Requirement | Tracking Issue |
| :--- | :--- | :--- | :--- | :--- |
| **Mock Firestore Fallback** | `backend/services/firestore_service.py`, `rhythma_flutter/lib/services/firestore_service.dart` | Allows local development without requiring live Firebase credentials by falling back to mock or stubbed data. | Require an active Firebase configuration with strict database security rules enforced. | N/A |
| **Cleartext Traffic Enabled** | `rhythma_flutter/android/app/src/main/AndroidManifest.xml` | Permits unencrypted HTTP communication for testing on local Android emulators/devices. | Enforce HTTPS exclusively (`android:usesCleartextTraffic="false"`) and configure a Network Security Config. | N/A |
| **Default HTTP `API_BASE_URL`** | `rhythma_flutter/lib/config/app_config.dart`, `rhythma_flutter/.env.example`, `README.md` | Defaults to non-secure `http://` local server URLs for quick setup. | Enforce secure `https://` base URLs passed via environment variables/production build configurations. | N/A |
| **30-minute JWT with No Refresh Flow** | `backend/auth.py` | Uses a fixed token expiration window without automated refresh token mechanisms. | Implement short-lived access tokens coupled with a secure HTTP-only refresh token renewal flow. | N/A |
