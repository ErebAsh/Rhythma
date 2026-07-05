[![Rhythma logo](https://github.com/ishita2740/Rhythma/raw/main/landing-page/public/logo1.png)](/ishita2740/Rhythma/blob/main/landing-page/public/logo1.png)

# Rhythma 🌸

*Her Rhythm. Her Health. Her Power.*

A multilingual, offline-capable AI-powered women's health companion built for women in India.

[![Flutter](https://img.shields.io/badge/Flutter-3.x-blue?logo=flutter)](https://flutter.dev) [![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green?logo=fastapi)](https://fastapi.tiangolo.com) [![Gemini API](https://img.shields.io/badge/Gemini-API-orange?logo=google)](https://ai.google.dev) [![License: MIT](https://img.shields.io/badge/License-MIT-purple.svg)](https://github.com/ishita2740/Rhythma/blob/main/LICENSE) [![Status](https://img.shields.io/badge/Status-Active%20Development-yellow)](#project-status)

---

> **A note on this README:** This document is kept in sync with the actual code in this repository, not with the long-term vision for the product. If a feature isn't in the code yet, it's listed under **Future Features**, not under **Implemented**. See [Project Status](#project-status) for the full breakdown.

---

## 🎯 The Problem

1 in 5 Indian women have PCOD — yet **70% of cases go undetected for years**. Women in tier-2 and tier-3 cities face a uniquely difficult combination of challenges:

- Popular apps (Flo, Clue) assume 28-day cycles, English fluency, and stable internet
- Limited access to gynecologists in smaller cities
- Deep social stigma that prevents open conversations about menstrual health
- No dedicated, age-appropriate guidance for girls experiencing their first period
- No AI-powered early detection tool built specifically for Indian languages and contexts

**Rhythma was built from the ground up for Indian women — not adapted from a solution built for another market.**

---

## Solution

Rhythma aims to be an offline-first, multilingual women's health companion for tier-2 and tier-3 Indian cities — supporting cycle tracking, an AI health assistant, and personalized wellness scoring in regional languages.

Today, the repository contains:

- A **polished, mostly-static Flutter UI** for five core screens (Home, Cycle, AI Assistant, Insights, Profile) plus Settings, in 5 languages, with light/dark theming.
- A **working FastAPI backend** with real authentication (JWT + bcrypt) and a Firestore-backed user store.
- A **directly-integrated Gemini AI assistant** in the Flutter app (calls Google's API straight from the client).
- Local **Hive** storage for profile, settings, and emergency contacts.
- Scaffolded (not yet trained) **CVI/MHS scoring logic** on the backend.
- A separate **Next.js marketing landing page**, unrelated to the app's functionality.

Several pieces (cloud sync, on-device encryption, cycle-log persistence, SMS delivery from the app, WhatsApp access, first-period onboarding, Ayurvedic content) are **not yet functional** — see [Implemented Features](#implemented-features) vs. [Features In Progress](#features-in-progress) vs. [Future Features](#future-features) below for the exact line.

---

## Platforms

Rhythma is planned as **two front ends sharing one backend**, not two separate products:

1. **Flutter mobile app** (`rhythma_flutter/`) — the primary experience today. Most of the UI described in this README lives here.
2. **Website** — a planned browser-based client with **the same features as the app** (cycle tracking, AI Assistant, Insights, Profile), talking to the same FastAPI backend, for women who don't have or don't want to install a mobile app.

**This does not exist yet.** The only web-facing thing in the repo today is `landing-page/`, a Next.js **marketing** site — it explains the product, it does not run any of the product's functionality (no login, no cycle tracking, no AI assistant). Don't confuse the two when navigating the codebase. Building the real web app is tracked under [Future Features](#future-features) and [Roadmap Phase 6](#phase-6--platform-expansion); it will need the backend integration work in Phases 1–2 to land first, since the website would consume the same `/auth`, `/cycle`, `/insights`, and `/assistant` endpoints the Flutter app is only partway through using.

---

## Who Rhythma Is For

Rhythma is designed to grow into support for multiple groups of Indian women, each with different needs. Not all of these are served by the app yet — this is the target scope, not a claim about current functionality.

| Group | Age / context | What they need |
| --- | --- | --- |
| **Teen girls (first period journey)** | 12–17 | Simple, non-clinical first-period guidance and menstrual education — **planned, not yet built** (see [First Period Guidance](#future-features)) |
| **College students & working women** | 18–35 | Irregular-cycle tracking, PCOD/PCOS awareness, hormonal health support — **primary users of the current app** |
| **Women with irregular cycles** | 18–35+ | Long-term pattern detection (CVI), not single-cycle guesswork | 
| **Community / self-help groups** | Extended ecosystem (NGOs, rural users, shared devices) | Offline access, SMS support, and eventually WhatsApp-based access without needing to install an app — **partially planned** |

Contributors working on onboarding flows, content, or accessibility should keep these different personas in mind, especially the gap between the current adult-focused experience and the still-unbuilt teen-focused one.

---

## Screenshots

*(Screenshots below reflect UI mockups for screens that are visually complete but, in some cases, not yet wired to real data — see [Project Status](#project-status).)*

| Dashboard | Cycle Calendar | AI Assistant |
| --- | --- | --- |
| [![Dashboard](https://github.com/ishita2740/Rhythma/raw/main/screenshots/dashboard.png)](/ishita2740/Rhythma/blob/main/screenshots/dashboard.png) | [![Calendar](https://github.com/ishita2740/Rhythma/raw/main/screenshots/calender.png)](/ishita2740/Rhythma/blob/main/screenshots/calender.png) | [![AI Assistant](https://github.com/ishita2740/Rhythma/raw/main/screenshots/AI_assistant.png)](/ishita2740/Rhythma/blob/main/screenshots/AI_assistant.png) |

| Health Insights | CVI Score | MHS Score | SMS Summary |
| --- | --- | --- | --- |
| [![Health Insights](https://github.com/ishita2740/Rhythma/raw/main/screenshots/Health_Insights.png)](/ishita2740/Rhythma/blob/main/screenshots/Health_Insights.png) | [![CVI](https://github.com/ishita2740/Rhythma/raw/main/screenshots/CVI.png)](/ishita2740/Rhythma/blob/main/screenshots/CVI.png) | [![MHS](https://github.com/ishita2740/Rhythma/raw/main/screenshots/MHS.png)](/ishita2740/Rhythma/blob/main/screenshots/MHS.png) | [![SMS](https://github.com/ishita2740/Rhythma/raw/main/screenshots/SMS.png)](/ishita2740/Rhythma/blob/main/screenshots/SMS.png) |

---

## 🚀 Key Features

| Feature | Description | Status |
| --- | --- | --- |
| 🌸 **Smart Cycle Tracking** | Handles irregular cycles. No fixed 28-day assumption. Tracks flow, mood, and daily symptoms. | ⚠️ UI only — see [status](#features-in-progress) |
| 🤖 **Gemini-Powered AI Assistant** | Multilingual health education and wellness guidance in Hindi, Marathi, Tamil, English, and more. | ✅ Implemented (client-side) |
| 📊 **Cycle Variability Index™ (CVI)** | Proprietary 0–100 score quantifying hormonal instability over rolling 6–12 months. | ⚠️ Logic exists, not trained, not wired to UI |
| ❤️ **Menstrual Health Score™ (MHS)** | Holistic composite score: CVI + lifestyle + sleep + stress + symptoms. | ⚠️ Logic exists, not trained, not wired to UI |
| 🏥 **Hormonal Risk Indicator** | 3-tier alert system (Low / Medium / High) based on cycle gaps and symptom clusters. (Awareness tool, not a diagnosis.) | ⚠️ Backend logic only |
| 📱 **Offline-First Architecture** | Hive local storage → Firestore cloud sync when connectivity is available. | ⚠️ Local storage done; sync stubbed |
| 🔒 **Privacy-First Design** | On-device encryption. No data leaves the phone without explicit user consent. | ❌ Not implemented |
| 🌍 **Indian Regional Languages** | Full UI localization across Indian languages. | ✅ Implemented (English, Hindi, Marathi, Tamil, Telugu) |
| 📩 **SMS Health Summaries** | Weekly summaries via Twilio SMS for users in low-data areas. | ⚠️ Backend done; not linked in app |
| 🩸 **First Period Guidance** | A dedicated, age-appropriate onboarding and education flow for first-time users (ages 12–17) — separate tone, content, and simplicity level from the adult cycle-tracking experience. | ❌ Not implemented — see [Future Features](#future-features) |
| 🌿 **Ayurvedic Correlation Layer** | Educational wellness insights that connect lifestyle and cycle patterns with traditional Ayurvedic wellness concepts, for cultural relevance (educational only, not medical advice). | ❌ Not implemented — see [Future Features](#future-features) |
| 💬 **WhatsApp Bot Integration** | Gemini-powered WhatsApp assistant (via Twilio/Meta Cloud API) for cycle tracking and health Q&A without requiring an app install — aimed at community/self-help-group users on shared or low-end devices. | ❌ Not implemented — see [Future Features](#future-features) |
| 🌐 **Website (feature parity)** | A browser-based client offering the same cycle tracking, AI Assistant, Insights, and Profile features as the Flutter app, on the same backend. | ❌ Not implemented — see [Platforms](#platforms) |

---

### Implemented Features

These exist in the code today and function as described:

- **Backend authentication** — registration and login with bcrypt password hashing and JWT issuance (`backend/core/auth.py`, `backend/core/auth_router.py`). Protected routes verify the token via `get_current_user`.
- **AI Assistant (client-side)** — the Flutter app talks directly to the Gemini API (`gemini_service.dart`) with a system prompt tuned for menstrual health guidance, graceful fallback text when no API key is configured, and multi-turn chat history.
- **Local storage (Hive)** — user profile, app settings, and emergency contacts are saved and loaded from on-device Hive boxes (`local_storage_service.dart`). This data persists across app restarts.
- **Profile management** — full create/edit flow with input validation (name, age, cycle length), backed by Hive.
- **Emergency contacts** — full add/edit/delete flow with phone number validation, backed by Hive.
- **Local notifications** — permission requests, scheduled reminders, and instant test notifications via `flutter_local_notifications` (`notification_service.dart`), wired to toggles in Settings.
- **Theming** — light/dark mode and a selectable accent color, persisted to Hive and applied app-wide via `ThemeProvider`.
- **Localization** — full UI translation into English, Hindi, Marathi, Tamil, and Telugu (~125 keys each), switchable in-app and persisted.
- **Settings screen** — notification toggles, language/theme navigation, permission shortcuts, and a logout confirmation flow.
- **Backend health/CORS/router scaffolding** — a real FastAPI app with a lifespan hook, CORS middleware, and modular routers.
- **Backend Firestore integration (users only)** — real create/read/update operations against a Firestore `users` collection.
- **Backend tests** — 4 passing `pytest` tests covering login success/failure, protected-route rejection, and SMS rate limiting, with Gemini mocked out.

### Features In Progress

These have partial code, UI, or backend logic, but are **not end-to-end functional**:

- **Cycle tracking** — the calendar UI exists (`cycle_screen.dart`), but it currently renders hardcoded state; nothing the user taps is saved. The Hive methods to persist cycle logs already exist but aren't yet called from this screen.
- **Symptoms / mood / sleep / stress logging** — the backend data model (`CycleLog`) supports these fields, but no Flutter screen currently collects them.
- **Cycle history** — a `GET /cycle/{user_id}/history` endpoint exists but returns an empty, hardcoded list; there's no database read behind it yet.
- **Health Insights (CVI / MHS)** — the scoring math exists on the backend (`cvi_model.py`, `mhs_model.py`) with a heuristic fallback (no trained model file is committed yet), but the Insights screen in Flutter currently shows static UI, not real scores from these endpoints.
- **AI Assistant (backend endpoint)** — a fully built `/assistant/chat` FastAPI endpoint exists (with the same system prompt design), but the Flutter app does not call it yet; it currently talks to Gemini directly instead. One of these two paths will be deprecated as the architecture consolidates.
- **SMS summaries** — the backend has a real Twilio integration with rate limiting, and Flutter has a complete `SmsScreen` UI, but the screen isn't yet linked into app navigation and doesn't yet call the backend endpoint.
- **In-app authentication** — the backend fully supports register/login, but the Flutter app has no login, registration, or session UI yet; it opens directly into the main app.
- **Cloud sync (Firestore, client-side)** — `firestore_service.dart` on the Flutter side is currently a stub with the real Firestore calls commented out pending Firebase client setup.
- **Testing (Flutter)** — a widget test suite exists, but part of it currently expects UI text that doesn't match the current Settings screen and needs to be reconciled with the code.

### Future Features

These are on the roadmap but have **no implementation yet** — no code, no content, no UI. Contributors interested in any of these should open an issue first (see [CONTRIBUTING.md](./CONTRIBUTING.md#issue-workflow)) to discuss scope before building, since these are also the areas most likely to need product/content decisions, not just code.

- **First Period Guidance** — a separate onboarding path and education content for girls aged 12–17 experiencing their first period. Needs its own tone, simplified UI, and content review (likely with input from a health educator) before implementation. Nothing exists in the codebase yet — no screen, no content, no data model changes.
- **Ayurvedic Correlation Layer** — educational content connecting lifestyle and cycle patterns to traditional Ayurvedic wellness concepts. Requires sourcing and reviewing culturally accurate, non-prescriptive content, plus a lightweight rules layer to surface it contextually. No content or code exists yet.
- **WhatsApp Bot Integration** — a Gemini-powered WhatsApp assistant (via Twilio/Meta Cloud API) offering cycle tracking and health Q&A without an app install, aimed at community/self-help-group users and shared/low-end devices. Depends on the backend `/assistant/chat` endpoint being production-ready first (see [Features In Progress](#features-in-progress)).
- **Website (feature parity)** — a second, browser-based client offering the same core features as the Flutter app (see [Platforms](#platforms)), built against the same backend endpoints. Distinct from the existing `landing-page/` marketing site, which has no product functionality. No code exists yet.
- End-to-end offline-first sync with conflict resolution and a visible sync-status indicator
- On-device encryption for locally stored health data
- Connectivity-aware sync (detecting online/offline state)
- Water, weight, and medication tracking
- Data export/import and shareable health reports
- A trained CVI/MHS model (current logic runs on a heuristic, not a trained model)
- Verified healthcare-provider directory / connect feature
- Regional, anonymized health-trend insights
- CI/CD pipelines and an automated release process
- Accessibility support (screen reader labels, semantic markup)

---

## Technology Stack

| Layer | Technology | Status | Why |
| --- | --- | --- | --- |
| Mobile app | **Flutter** | Implemented (UI) | Single codebase across Android/iOS |
| Website (planned product client) | Not yet chosen | Not implemented | Will consume the same backend as the Flutter app; not to be confused with the Next.js marketing site below |
| Marketing landing page | **Next.js** | Implemented | Public-facing site explaining the product; no app functionality |
| Backend | **FastAPI** | Implemented | Lightweight async Python API layer |
| Auth | **JWT + bcrypt** | Implemented (backend only) | Stateless, standard token auth |
| Cloud database | **Firebase / Firestore** | Implemented for user accounts only; not yet used for health data | Managed NoSQL store, pairs with Firebase Auth long-term |
| Local storage | **Hive** | Implemented | Fast, dependency-light on-device storage for offline access |
| AI assistant | **Google Gemini API** | Implemented (called directly from Flutter) | Strong multilingual generation for Indian languages |
| State management | **Provider** | Implemented | Simple, sufficient reactivity for theme/locale |
| Notifications | **flutter_local_notifications** | Implemented | Local reminder scheduling without a push backend |
| Localization | **Flutter intl / ARB files** | Implemented | Native Flutter i18n tooling |
| Charts | Custom `CustomPainter` | Implemented (basic) | `fl_chart` is a listed dependency but not yet used |
| SMS | **Twilio** | Implemented on backend; not connected to the app UI yet | Reaches users without reliable data connectivity |
| WhatsApp messaging | **Twilio / Meta Cloud API (planned)** | Not implemented | Needed for the planned WhatsApp bot |
| ML scoring | **XGBoost / Logistic Regression (planned), heuristic fallback (current)** | Partially implemented | Efficient, interpretable scoring approach once trained |
| Routing | Manual `IndexedStack` / `Navigator` | Implemented | `go_router` is a listed dependency but not yet used |
| Encryption | — | Not implemented | `encrypt` / `flutter_secure_storage` are listed dependencies but unused |
| Connectivity detection | — | Not implemented | `connectivity_plus` is a listed dependency but unused |

---

## Architecture

Rhythma currently consists of two independently runnable pieces that are **not yet fully connected**:

```
┌──────────────────────────────────────────────┐
│                 Flutter App                   │
│                                                │
│  Home · Cycle · Assistant · Insights · Profile│
│                                                │
│  ┌──────────────────────────────────────┐     │
│  │  Hive (local, on-device)              │     │
│  │  → profile, settings, contacts        │     │
│  │  → cycle log storage exists,          │     │
│  │    but no screen writes to it yet     │     │
│  └──────────────────────────────────────┘     │
│                                                │
│  Gemini API ◄── called directly for AI chat   │
└──────────────────────────────────────────────┘

┌──────────────────────────────────────────────┐          ┌ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ┐
│               FastAPI Backend                 │◄─────────  Website (planned, no code   
│                                                │          │  yet) — same feature set as   
│  /auth      → real JWT auth, Firestore users  │           the Flutter app, same backend │
│  /assistant → real Gemini call (unused by app)│          └ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ┘
│  /cycle     → stub, returns empty/static data │
│  /insights  → stub, returns static data       │
│  /sms       → real Twilio integration         │
│  /health    → basic health check              │
└──────────────────────────────────────────────┘
```

The Flutter app and FastAPI backend do not currently share data — the app works entirely off local Hive storage and a direct Gemini connection, while the backend's auth, cycle, insights, and assistant endpoints are functional in isolation but are not yet called by the client.

There is no WhatsApp, first-period, Ayurvedic-content, or website layer in this architecture yet — they would each attach to the backend (`/assistant` for WhatsApp; new endpoints/content sources for first-period and Ayurvedic content; the full existing `/auth`, `/cycle`, `/insights`, `/assistant` set for the planned website). The dashed box above marks the one piece of this diagram that is a plan, not running code — see [Platforms](#platforms).

---

## Folder Structure

```
Rhythma/
├── backend/                       FastAPI backend
│   ├── api/
│   │   ├── assistant.py           Gemini chat endpoint (not yet used by the app)
│   │   ├── cycle.py                Cycle log endpoints (stubbed persistence)
│   │   ├── health.py               Health check
│   │   ├── insights.py             Score endpoint (stubbed)
│   │   └── sms.py                  Twilio SMS endpoint (real, rate-limited)
│   ├── core/
│   │   ├── auth.py                 JWT + password hashing
│   │   └── auth_router.py          Register/login routes
│   ├── models/
│   │   ├── cvi_model.py            Cycle Variability Index scoring (heuristic fallback)
│   │   ├── mhs_model.py            Menstrual Health Score scoring
│   │   └── user.py                 Pydantic user schemas
│   ├── services/
│   │   └── firestore_service.py    Firestore user CRUD
│   ├── tests/
│   │   └── test_auth.py            Backend test suite
│   ├── utils/logger.py
│   ├── main.py                     App entrypoint, router registration
│   └── .env.example
│
├── rhythma_flutter/                Flutter application
│   ├── lib/
│   │   ├── main.dart
│   │   ├── config/theme.dart
│   │   ├── components/             bottom_nav, charts, shared widgets
│   │   ├── providers/              theme_provider, locale_provider
│   │   ├── services/               local_storage_service, gemini_service,
│   │   │                           firestore_service (stub), notification_service
│   │   ├── screens/
│   │   │   ├── home/, cycle/, assistant/, insights/, profile/
│   │   │   ├── settings/           settings, language, theme
│   │   │   └── sms/                built but not yet linked into navigation
│   │   └── l10n/                   en, hi, mr, ta, te translations
│   ├── test/widget_test.dart
│   ├── env.example
│   └── pubspec.yaml
│   *(Note: `android/` and `ios/` platform folders are not committed; run
│   `flutter create .` before building for a device.)*
│
├── landing-page/                   Standalone Next.js marketing site (Vercel) —
│                                    NOT the planned product website; see "Platforms"
│                                    (no product website folder exists yet)
├── docs/architecture.md            System design notes (describes target architecture)
├── design-concepts/                UI demo videos
├── screenshots/
├── requirements.txt                Backend Python dependencies
├── CONTRIBUTING.md
├── LICENSE
└── README.md
```

---

## Installation

### Prerequisites

- Flutter SDK 3.x
- Python 3.10+
- Git
- A Firebase project (for backend user storage)
- A Gemini API key ([get one here](https://ai.google.dev))
- A Twilio account (optional — only needed for SMS)

```
git clone https://github.com/ishita2740/Rhythma.git
cd Rhythma
```

### Running Flutter

```
cd rhythma_flutter

# Platform folders are not committed — generate them first
flutter create .

flutter pub get

cp env.example .env
# Add GEMINI_API_KEY to .env to enable real AI responses
# (without it, the assistant falls back to a canned demo response)

flutter run
```

### Running Backend

```
cd backend

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r ../requirements.txt

cp .env.example .env
# Fill in JWT_SECRET, Firebase credentials, and (optionally) GEMINI_API_KEY / Twilio credentials

uvicorn main:app --reload
```

The API will be available at `http://127.0.0.1:8000`, with interactive docs at `http://127.0.0.1:8000/docs`.

To run backend tests:

```
cd backend
pytest
```

---

## Configuration

### Environment Variables

**Backend (`backend/.env`)**

| Variable | Required | Purpose |
| --- | --- | --- |
| `JWT_SECRET` | Yes | Signs and verifies auth tokens. App will not start without it. |
| `FIREBASE_SERVICE_ACCOUNT_JSON` or `FIREBASE_SERVICE_ACCOUNT_PATH` | Yes (one of the two) | Firebase Admin SDK credentials for Firestore access |
| `GEMINI_API_KEY` | Optional | Enables the backend's `/assistant/chat` endpoint |
| `TWILIO_ACCOUNT_SID` / `TWILIO_AUTH_TOKEN` / `TWILIO_PHONE_NUMBER` | Optional | Enables the `/sms/send-summary` endpoint |

**Flutter (`rhythma_flutter/.env`)**

| Variable | Required | Purpose |
| --- | --- | --- |
| `GEMINI_API_KEY` | Optional | Enables real AI responses in the Assistant tab; without it, a demo fallback response is shown |

### Firebase Setup

The backend currently uses Firebase **only for user accounts** (via the Admin SDK). To set it up:

1. Create a Firebase project at [console.firebase.google.com](https://console.firebase.google.com).
2. Generate a service account key: **Project Settings → Service Accounts → Generate new private key**.
3. Either paste the resulting JSON into `FIREBASE_SERVICE_ACCOUNT_JSON`, or save the file and point `FIREBASE_SERVICE_ACCOUNT_PATH` at it.
4. Ensure Firestore is enabled in the project (Native mode).

> **Note:** The Flutter app does not currently initialize Firebase or connect to Firestore on the client side — `firebase_core`, `cloud_firestore`, and `firebase_auth` are listed as dependencies for planned client-side sync but are not yet wired up. No `google-services.json` / `GoogleService-Info.plist` setup is required today.

---

## Project Status

| Area | Status |
| --- | --- |
| Flutter UI (screens, theming, localization) | ✅ Largely complete |
| Local storage (profile, settings, contacts) | ✅ Complete |
| Local notifications | ✅ Complete |
| Backend authentication (JWT/bcrypt) | ✅ Complete |
| Backend Firestore (user accounts) | ✅ Complete |
| AI Assistant (client → Gemini directly) | ✅ Functional |
| AI Assistant (backend endpoint) | ⚠️ Built, unused |
| Cycle tracking (persistence) | ❌ UI only, not wired |
| Cycle/insights backend endpoints | ⚠️ Stubbed, no persistence |
| CVI / MHS scoring | ⚠️ Logic exists, no trained model, not called from the app |
| SMS (Twilio) | ⚠️ Backend done; app UI built but unlinked |
| Cloud sync (Flutter ↔ Firestore) | ❌ Stubbed only |
| Encryption at rest | ❌ Not implemented |
| Connectivity detection | ❌ Not implemented |
| In-app authentication | ❌ Not implemented |
| First Period Guidance | ❌ Not implemented — no design, content, or code yet |
| Ayurvedic Correlation Layer | ❌ Not implemented — no content or code yet |
| WhatsApp Bot Integration | ❌ Not implemented — depends on backend assistant endpoint going live first |
| Website (feature parity with the app) | ❌ Not implemented — no framework chosen, no code; not to be confused with the existing marketing `landing-page/` |
| Testing | ⚠️ Basic backend suite passing; Flutter suite needs reconciliation with current UI |
| CI/CD | ❌ Not set up |
| Deployment | ⚠️ Landing page only (Vercel) |

**In short:** the Flutter UI and the FastAPI backend are each independently further along than the app is as an integrated whole. The immediate priority is wiring the two together and making cycle tracking actually persist data. First Period Guidance, the Ayurvedic layer, and the WhatsApp bot are all clean-slate features with no existing code — good candidates for contributors who want to own something end-to-end, but each needs a scoping discussion first (see [CONTRIBUTING.md](./CONTRIBUTING.md)).

---

## Roadmap

### Phase 1 — Make it functional end-to-end

- Generate missing Flutter platform folders (`android/`, `ios/`)
- Wire the Cycle screen to Hive persistence
- Reconcile the Flutter test suite with the current Settings UI
- Link the built `SmsScreen` into app navigation

### Phase 2 — Connect frontend and backend

- Build in-app login/registration against the existing backend auth
- Persist cycle logs through the backend `/cycle` endpoints
- Decide on a single Gemini integration path (client-direct vs. backend-proxied) and remove the other
- Connect the Insights screen to real CVI/MHS scores

### Phase 3 — Offline-first & privacy

- Implement Hive encryption at rest
- Add connectivity detection and complete the stubbed Firestore sync logic
- Initialize Firebase on the client and add a sync-status indicator

### Phase 4 — Real ML scoring

- Collect/curate training data and ship trained CVI/MHS model artifacts
- Replace the current heuristic fallback with model-backed predictions

### Phase 5 — Expanded health content

- **First Period Guidance**: design and build a dedicated onboarding/education flow for ages 12–17
- **Ayurvedic Correlation Layer**: source and review educational content, then build the rules layer to surface it contextually
- Both require content/product decisions before implementation — see [Future Features](#future-features)

### Phase 6 — Platform expansion

- **Website with feature parity**: a new, separate front end (framework not yet decided) covering cycle tracking, AI Assistant, Insights, and Profile against the same backend the Flutter app uses — not an extension of the existing `landing-page/` marketing site. See [Platforms](#platforms).
- **WhatsApp-based assistant access**, built on top of the existing (but currently unused) `/assistant/chat` backend endpoint
- CI/CD, automated releases, and healthcare-provider partnerships

---

## Contributing

Contributions are welcome. Please read [CONTRIBUTING.md](https://github.com/ishita2740/Rhythma/blob/main/CONTRIBUTING.md) before opening a pull request. Since large parts of the app are still being wired together (see [Project Status](#project-status)), issues that clarify or fix the frontend/backend integration gaps above are especially useful right now. First Period Guidance, the Ayurvedic Correlation Layer, WhatsApp Bot Integration, and the planned website are open, clean-slate feature areas — see [CONTRIBUTING.md](./CONTRIBUTING.md#feature-areas-open-for-contribution) for how to propose an approach.

---

## License

This project is licensed under the MIT License. See [LICENSE](https://github.com/ishita2740/Rhythma/blob/main/LICENSE) for details.

---

## Acknowledgements

- Built by [Ishita Rathi](https://github.com/ishita2740)
- AI assistance powered by [Google Gemini](https://ai.google.dev)
- Backend framework by [FastAPI](https://fastapi.tiangolo.com)
- Mobile framework by [Flutter](https://flutter.dev)
- Read the origin story: [*Building Rhythma: An AI health companion for the women India's apps forgot*](https://medium.com/@rathiishita1005729/building-rhythma-an-ai-health-companion-for-the-women-indias-forgot-e249ac1cdc9a)

---

## Disclaimer

Rhythma is intended for **educational and general wellness purposes only**. It is not a certified medical device and does not provide medical diagnoses, prescriptions, or treatment recommendations. The Cycle Variability Index (CVI) and Menstrual Health Score (MHS) are experimental, non-clinical metrics currently under development. Any future Ayurvedic content will be educational and non-prescriptive, not a substitute for medical advice. Always consult a qualified healthcare professional for medical advice.

---

*Built with 💜 for the women India's apps forgot.*
