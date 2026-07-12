[![Rhythma logo](https://github.com/ishita2740/Rhythma/raw/main/landing-page/public/logo1.png)](/ishita2740/Rhythma/blob/main/landing-page/public/logo1.png)

# Rhythma 🌸

*Her Rhythm. Her Health. Her Power.*

An AI-powered, offline-first, multilingual women's health companion — built for the women India's apps forgot.

[![Flutter](https://img.shields.io/badge/Flutter-3.x-blue?logo=flutter)](https://flutter.dev) [![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green?logo=fastapi)](https://fastapi.tiangolo.com) [![Gemini API](https://img.shields.io/badge/Gemini-API-orange?logo=google)](https://ai.google.dev) [![License: MIT](https://img.shields.io/badge/License-MIT-purple.svg)](https://github.com/ishita2740/Rhythma/blob/main/LICENSE) [![Status](https://img.shields.io/badge/Status-Active%20Development-yellow)](#project-status)

---

## 🎯 The Problem

**1 in 5 Indian women** experience PCOD/PCOS symptoms, and national studies show a **19.6% PCOS prevalence** using Rotterdam criteria — yet most cases go unnoticed for years. Women in Tier-2, Tier-3, and semi-urban India face a compounding set of barriers:
 
- Popular period-tracking apps (Flo, Clue) assume 28-day cycles, English fluency, and stable internet
- Gynecologist access remains limited outside major cities
- Deep social stigma discourages open conversations about reproductive health
- Only **26%** of Indian women have regular mobile internet access
- No AI tool built natively for Indian languages, realities, and connectivity constraints
> *"Women's healthcare is not inaccessible because solutions don't exist. It is inaccessible because current solutions are not designed around Indian realities."*
 
**Rhythma is built from the ground up for Indian women — not adapted from a solution built for another market.**

---

## ✨ What Rhythma Does
 
Rhythma helps women **understand, track, and act** on their health privately, in their own language. Users log cycles, symptoms, mood, sleep, and lifestyle habits; Rhythma turns that data into personalized, on-device health insights instead of just raw charts.
Rhythma aims to be an offline-first, multilingual women's health companion for tier-2 and tier-3 Indian cities — supporting cycle tracking, an AI health assistant, and personalized wellness scoring in regional languages.

---

## Platforms

Rhythma consists of **two front ends sharing one backend**, not two separate products:

1. **Flutter mobile app** (`rhythma_flutter/`) — the primary experience today. Most of the UI described in this README lives here.
2. **Website** (`web/`) — a browser-based client aiming for **the same features as the app** (cycle tracking, AI Assistant, Insights, Profile), talking to the same FastAPI backend, for women who don't have or don't want to install a mobile app. **Scaffolding has started**: a React + Vite + TypeScript app with working registration, login, protected routing, and i18n (same 5 locales as Flutter) against the real backend `/auth` endpoints — but it only has a placeholder home page so far. Cycle tracking, AI Assistant, and Insights pages don't exist on the web yet.

This is separate from `landing-page/`, a Next.js **marketing** site that explains the product but runs none of its functionality. Don't confuse the two when navigating the codebase.

---

## Who Rhythma Is For

Rhythma is designed to grow into support for multiple groups of Indian women, each with different needs. Not all of these are served by the app yet — this is the target scope, not a claim about current functionality.

| Group | Age / context | What they need |
| --- | --- | --- |
| **Teen girls (first period journey)** | 12–17 | Simple, non-clinical first-period guidance and menstrual education — **planned, not yet built** (see [First Period Guidance](#future-features)) |
| **College students & working women** | 18–35 | Irregular-cycle tracking, PCOD/PCOS awareness, hormonal health support — **primary users of the current app** |
| **Women with irregular cycles** | 18–35+ | Long-term pattern detection (CVI), not single-cycle guesswork | 
| **Community / self-help groups** | Extended ecosystem (NGOs, rural users, shared devices)  across Tier-2, Tier-3 & semi-urban India | Offline access, SMS support, and eventually WhatsApp-based access without needing to install an app — **partially planned** |

| **Feature** | **Details** |
| --- | --- |
| **Languages** | Hindi, Marathi, Tamil, English — more planned |
| **Health scores** | CVI™ (Cycle Variability Index) + MHS™ (Menstrual Health Score) — proprietary |
| **Connectivity** | Offline-first; core features work with zero internet, sync when available |
| **Privacy** | 100% on-device processing and storage by default |

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

## 🆚 How Rhythma Compares
 
| Feature | Flo | SheBloom | HerMantra | **Rhythma** |
|---|:---:|:---:|:---:|:---:|
| PCOS/PCOD Support | ✅ | ✅ | ✅ | ✅ |
| AI Early Risk Detection | ✅ | ➖ | ➖ | ✅ |
| Offline Functionality | ❌ | ✅ | ➖ | ✅ |
| SMS-Based Health Support | ❌ | ❌ | ❌ | ✅ |
| Privacy-First Data Ownership | ✅ | ✅ | ➖ | ✅ |
| Indian Language Support | ❌ | ✅ | ✅ | ✅ |
| CVI™ Score (Proprietary) | ❌ | ❌ | ❌ | ✅ |
| MHS™ Score (Proprietary) | ❌ | ❌ | ❌ | ✅ |
| Educational Ayurvedic Layer | ❌ | ➖ | ✅ | ✅ |

 
*Feature comparison based on publicly available information from official websites, app stores, and product documentation. Availability may change over time.*
 
**Key insight:** Existing platforms solve specific problems. Rhythma combines multiple underserved needs into one India-first ecosystem.

---

## 🚀 Key Features

| Feature | Description |
| --- | --- |
| 🔐 **Account Login / Registration** | JWT-based sign up and sign in, gating access to the app. | 
| 🌸 **Smart Cycle Tracking** | Handles irregular cycles. No fixed 28-day assumption. Tracks flow, mood, and daily symptoms. |
| 🤖 **Gemini-Powered AI Assistant** | Multilingual health education and wellness guidance in Hindi, Marathi, Tamil, English, and more. |
| 📊 **Cycle Variability Index™ (CVI)** | Proprietary 0–100 score quantifying hormonal instability over rolling 6–12 months. |
| ❤️ **Menstrual Health Score™ (MHS)** | Holistic composite score: CVI + lifestyle + sleep + stress + symptoms. | 
| 🏥 **Hormonal Risk Indicator** | 3-tier alert system (Low / Medium / High) based on cycle gaps and symptom clusters. (Awareness tool, not a diagnosis.) | 
| 📱 **Offline-First Architecture** | Hive local storage → Firestore cloud sync when connectivity is available. | 
| 🔒 **Privacy-First Design** | On-device encryption. No data leaves the phone without explicit user consent. | 
| 🌍 **Indian Regional Languages** | Full UI localization across Indian languages. | 
| 📩 **SMS Health Summaries** | Weekly summaries via Twilio SMS for users in low-data areas. | 
| 🩸 **First Period Guidance** | A dedicated, age-appropriate onboarding and education flow for first-time users (ages 12–17) — separate tone, content, and simplicity level from the adult cycle-tracking experience. |
| 🌿 **Ayurvedic Correlation Layer** | Educational wellness insights that connect lifestyle and cycle patterns with traditional Ayurvedic wellness concepts, for cultural relevance (educational only, not medical advice). | 
| 💬 **WhatsApp Bot Integration** | Gemini-powered WhatsApp assistant (via Twilio/Meta Cloud API) for cycle tracking and health Q&A without requiring an app install — aimed at community/self-help-group users on shared or low-end devices. | 
| 🌐 **Website (feature parity)** | A browser-based client offering the same cycle tracking, AI Assistant, Insights, and Profile features as the Flutter app, on the same backend. | 

> **ML models run entirely on-device.** No sensitive health data leaves the phone unless the user explicitly enables cloud sync.

---

## 🛠️ Detailed Technology Stack
 
### Mobile — `rhythma_flutter/`
| Package | Version | Purpose | Status in code |
|---|---|---|---|
| flutter (SDK) | — | Core framework | — |
| dio | ^5.4.3 | HTTP client | Used in `api_client.dart`, `auth_service.dart` |
| http | ^1.2.2 | Secondary HTTP client | Present |
| flutter_secure_storage | ^9.2.2 | Secure token storage | Used in `secure_storage.dart` |
| provider | ^6.1.2 | State management | Used across `providers/` |
| google_fonts | ^6.2.1 | Typography | Used in theme |
| go_router | ^13.2.0 | Navigation | Used |
| hive / hive_flutter | ^2.2.3 / ^1.1.0 | Local offline storage | Used extensively in `local_storage_service.dart` |
| firebase_core / cloud_firestore / firebase_auth | ^3.3.0 / ^5.2.1 / ^5.1.3 | Cloud sync | **In pubspec.yaml but never initialized — no `Firebase.initializeApp()` call anywhere in the codebase** |
| encrypt | ^5.0.3 | Local encryption | Present |
| fl_chart | ^0.68.0 | Charts | Used in `components/charts.dart` |
| flutter_localizations / intl | — / ^0.20.2 | i18n | Used, 5 languages generated |
| permission_handler | ^12.0.3 | Runtime permissions | Used by notification service |
| connectivity_plus | ^6.0.3 | Network state | **In pubspec.yaml but not imported anywhere in `lib/`** |
| shared_preferences | ^2.3.2 | Lightweight key-value storage | Present |
| url_launcher | ^6.3.0 | Open external links | Present |
| flutter_local_notifications / timezone | ^22.0.1 / ^0.11.1 | Local notifications | Used, but only wired to one manual Settings toggle |
| email_validator | ^3.0.0 | Form validation | Present |
| flutter_lints | ^4.0.0 (dev) | Linting | Used in CI |
 
### Backend — `backend/` (`requirements.txt`)
| Package | Version | Purpose |
|---|---|---|
| fastapi | 0.111.0 | Web framework |
| uvicorn[standard] | 0.30.1 | ASGI server |
| pydantic / pydantic-settings | 2.7.4 / 2.3.3 | Validation |
| firebase-admin | 6.5.0 | Server-side Firestore access |
| google-generativeai | 0.7.2 | Gemini API (model: `gemini-2.5-flash`, hardcoded in `assistant.py`) |
| xgboost | 2.0.3 | CVI model (declared, no trained artifact committed) |
| scikit-learn | 1.5.0 | MHS model (declared) |
| numpy / pandas / joblib | 1.26.4 / 2.2.2 / 1.4.2 | Data handling / model I/O |
| twilio | 9.2.3 | SMS delivery — real integration in `sms.py` |
| python-jose[cryptography] | 3.3.0 | JWT |
| passlib[bcrypt] / bcrypt | 1.7.4 / 4.1.3 | Password hashing |
| httpx | 0.27.0 | Async HTTP client |
| python-dotenv | 1.0.1 | Env config |
| loguru | 0.7.2 | Logging |
| pytest / pytest-asyncio | 8.2.2 / 0.23.7 | Testing (1 test file, auth only) |
 
### Web App — `web/` (React, separate from landing page)
React 19.2, Vite 8, TypeScript 6, react-router-dom 7, i18next + react-i18next + browser language detector, axios. No UI component library, no chart library yet.
 
### Landing Page — `landing-page/` (Next.js, separate app)
Next.js 16, React 19, Tailwind CSS 4, shadcn/ui, class-variance-authority, lucide-react, @vercel/analytics. Deployed at `rhythma-navy.vercel.app`.
 
### CI/CD — `.github/workflows/`
GitHub Actions already configured for **backend** (`pytest`, path-filtered) and **Flutter** (`flutter analyze` + `flutter test`, path-filtered). No workflow yet for `web/` or `landing-page/`.
 
---

 ## Current Status — Done / Partial / Not Implemented
 
Legend: ✅ **Done** (real, working, no mocks) · 🟡 **Partial / Needs Attention** (real code exists but incomplete, hardcoded piece, or disconnected) · ❌ **Not Implemented** (stub, placeholder, or absent)
 
### Backend
 
| Item | Status | Evidence |
|---|---|---|
| Auth: register / login / JWT / rate limiting | ✅ Done | `auth_router.py` — bcrypt hashing, rate-limited, generic error messages to prevent enumeration |
| Auth: password reset / email verification / refresh tokens | ❌ Not Implemented | No corresponding routes exist; access token expires in 30 min with no refresh flow |
| `POST /cycle/log`, `GET /cycle/{id}/history` | ✅ Done | Real Firestore persistence via `CycleService` |
| `POST /cycle/quick-log` (single-field upsert, discussed in issue #50) | ❌ Not Implemented | Not present in `api/cycle.py` — only the full-log endpoint exists server-side |
| `GET /dashboard` (CVI, MHS, cycle day, next period) | ✅ Done | Real feature extraction from Firestore logs, real model calls, `hasEnoughDataForInsights` flag |
| `GET /{user_id}/scores` (Insights endpoint) | ❌ Not Implemented | `api/insights.py` is 12 lines, returns `{"message": "Scores for user X"}` — literal placeholder |
| CVI model (`cvi_model.py`) | 🟡 Partial | Real feature engineering + XGBoost inference path exists, but **no trained `.joblib` file is committed** — every request currently falls back to a hardcoded heuristic (`std_dev * 8 + 30`) |
| MHS model (`mhs_model.py`) | 🟡 Partial | Real weighted composite of CVI/sleep/stress/symptoms, but **`lifestyle_score` is hardcoded to `70.0`** pending lifestyle tracking |
| AI Assistant (`POST /assistant/chat`) | 🟡 Partial | Real Gemini API call with a real system prompt; **no grounding in a sourced medical dataset**, no conversation persistence (history is client-passed only, lost on restart), no per-user rate limiting |
| SMS settings + send (`api/sms.py`) | 🟡 Partial | Real Twilio call, real rate limiting, real phone validation — but **the message body must be supplied by the caller**; there's no backend logic that generates the summary content from real MHS/CVI data |
| Server-side Firestore service (`firestore_service.py`) | ✅ Done | Real read/write for users and cycle logs |
| Health check endpoint | ✅ Done | `api/health.py` exists and is wired into `main.py` |
| CORS config | 🟡 Partial | Hardcoded localhost origins in `main.py` with an explicit `# TODO: Tighten this in production` |
| Backend test coverage | 🟡 Partial | Only `test_auth.py` exists; no tests for cycle, dashboard, sms, or assistant endpoints |
| API documentation (OpenAPI descriptions) | 🟡 Partial | FastAPI auto-generates `/docs`, but most routes lack descriptive docstrings/response models beyond basic type hints |
 
### Mobile (Flutter)
 
| Item | Status | Evidence |
|---|---|---|
| All core screens (Home, Cycle, Assistant, Insights, Profile, Settings, SMS, Onboarding, Auth) | ✅ Done | All present in `lib/screens/`, referenced from `main.dart`/navigation |
| Auth service (register/login calling real backend) | ✅ Done | `auth_service.dart` makes real `dio` calls to `/auth/*` |
| Local storage (Hive) | ✅ Done | `local_storage_service.dart`, 363 lines, the most substantial service file |
| Firestore client sync (issue #27) | ❌ Not Implemented | `firestore_service.dart` has Firebase imports **commented out**; both `syncCycleLogs()` and `pullCycleLogs()` are no-op stubs that just log a debug string |
| Connectivity detection (issue #30) | ❌ Not Implemented | `connectivity_plus` is a declared dependency but not imported/used anywhere in `lib/` |
| Sync status indicator (issue #20) | ❌ Not Implemented | Depends on #27/#30, neither of which exist yet |
| Local notifications | 🟡 Partial | Real `flutter_local_notifications` integration, initialized at app start, but only wired to a single manual "medicine alert" toggle in Settings — **not** connected to period predictions or logging reminders |
| Localization — English | ✅ Done | 180 keys |
| Localization — Telugu | 🟡 Partial | 178/180 keys (2 missing vs. English) |
| Localization — Hindi, Marathi, Tamil | 🟡 Partial | 162/180 keys each (18 missing vs. English in each) |
| Localization native-speaker review | ❌ Not Implemented | Matches open issues #38–#41 — no review has happened yet |
| CVI/MHS display on Insights screen | 🟡 Partial | Screen exists and renders; depends on backend `/dashboard`, which itself is 🟡 (heuristic CVI, hardcoded MHS lifestyle component) |
| Onboarding flow | ✅ Done (generic) / ❌ Not Implemented (age-gated) | `onboarding_screen.dart` exists and is tested (`onboarding_test.dart`), but the age-gated "First Period" simplified flow from issue #42 doesn't exist as a separate path |
| Ayurvedic correlation content (issue #43) | ❌ Not Implemented | No `assets/content/ayurveda/` or equivalent data file found anywhere in the repo |
| Widget/unit tests | 🟡 Partial | 4 test files exist (local storage migration, onboarding, generic widget test, calendar grid) — good start, far from full coverage |
| Encryption at rest | 🟡 Partial | `encrypt` package is a dependency; not verified in this pass whether Hive boxes are actually opened with encryption enabled (worth a dedicated audit — this was already flagged as its own backlog item) |
 
### Web (`web/` — React/Vite)
 
| Item | Status | Evidence |
|---|---|---|
| App scaffold, routing | ✅ Done | `App.tsx`, `react-router-dom` configured |
| Auth context + protected routes | ✅ Done | `AuthContext.tsx` (103 lines), `ProtectedRoute.tsx` |
| Login / Register pages | ✅ Done | Both call the real backend via `api/client.ts` |
| i18n setup | ✅ Done | 5 locale JSON files present, `i18next` configured |
| Home / Dashboard page | ❌ Not Implemented | `HomePage.tsx` is 17 lines — placeholder only |
| Cycle tracking page | ❌ Not Implemented | No corresponding page file exists |
| AI Assistant page | ❌ Not Implemented | No corresponding page file exists |
| Insights page | ❌ Not Implemented | No corresponding page file exists |
| Profile / Settings pages | ❌ Not Implemented | No corresponding page file exists |
| CI for `web/` | ❌ Not Implemented | No GitHub Actions workflow targets `web/` |
 
### Landing Page (`landing-page/` — Next.js)
 
| Item | Status | Evidence |
|---|---|---|
| Deployed, live | ✅ Done | Live at `rhythma-navy.vercel.app` |
| CTA / navigation interactions | ❌ Not Implemented | Matches open issue #73 — "Get Started," "Learn More," and feature-section links don't work |
| CI | ❌ Not Implemented | No workflow targets `landing-page/` |
 
### WhatsApp Bot
 
| Item | Status |
|---|---|
| Everything (webhook, message routing, session identity) | ❌ Not Implemented — no code for this exists anywhere in the repo |
 
### Cross-Cutting
 
| Item | Status |
|---|---|
| CI — Backend | ✅ Done (`backend.yml`) |
| CI — Flutter | ✅ Done (`flutter.yml`) |
| CI — Web / Landing Page | ❌ Not Implemented |
| Architecture documentation | 🟡 Partial — `docs/architecture.md` exists but is only 67 lines, high-level; no documented CVI/MHS methodology, no API reference doc, no data-flow diagrams |
| CVI/MHS methodology write-up | ❌ Not Implemented |
| Sourced medical/symptom reference dataset | ❌ Not Implemented — nothing resembling this exists in `backend/` or `rhythma_flutter/assets/` |
| PR template enforcing source citations for health content | ❌ Not Implemented |
| Issue templates / CODEOWNERS | ❌ Not Implemented |

---

## Folder Structure

```
Rhythma/
│
├── .github/
│   └── workflows/
│       ├── backend.yml            # CI: pytest on backend/, PR + push triggers, path-filtered
│       └── flutter.yml            # CI: flutter analyze + flutter test, PR + push triggers
│
├── backend/                        # FastAPI backend
│   ├── .env.example
│   ├── main.py                     # App entry, CORS, router registration
│   ├── api/
│   │   ├── assistant.py           # POST /assistant/chat, GET /assistant/languages (real Gemini call)
│   │   ├── cycle.py               # POST /cycle/log, GET /cycle/{user_id}/history
│   │   ├── dashboard.py           # GET /dashboard — real CVI/MHS aggregation
│   │   ├── health.py              # Health check endpoint
│   │   ├── insights.py            # GET /{user_id}/scores — STUB, returns placeholder text
│   │   └── sms.py                 # GET/POST /sms/settings, POST /sms/send-summary (real Twilio call)
│   ├── core/
│   │   ├── auth.py                # JWT creation/verification, bcrypt hashing
│   │   └── auth_router.py         # /auth/register, /auth/token, /auth/me — rate-limited
│   ├── models/
│   │   ├── cvi_model.py           # CVI scoring — heuristic fallback (no trained .joblib present)
│   │   ├── mhs_model.py           # MHS scoring — weighted composite, one component hardcoded
│   │   └── user.py                # Pydantic UserCreate / UserResponse
│   ├── services/
│   │   └── firestore_service.py   # UserService + CycleService — real Firestore reads/writes
│   ├── tests/
│   │   └── test_auth.py           # Mocks Firebase + Gemini, tests auth flow only
│   └── utils/
│       └── logger.py
│
├── rhythma_flutter/                 # Flutter mobile app (Android + iOS + web + desktop targets)
│   ├── .env.example
│   ├── analysis_options.yaml
│   ├── l10n.yaml
│   ├── android/ , ios/ , linux/ , macos/ , windows/, web/   # Platform scaffolding (Flutter default)
│   ├── assets/
│   │   ├── avatars/                # 4 avatar images
│   │   └── images/logo.png
│   ├── lib/
│   │   ├── main.dart               # App entry — calls NotificationService.init()
│   │   ├── config/
│   │   │   ├── app_config.dart
│   │   │   └── theme.dart
│   │   ├── components/
│   │   │   ├── bottom_nav.dart
│   │   │   ├── charts.dart
│   │   │   └── shared.dart
│   │   ├── l10n/                   # 5 languages: en (180 keys), hi/mr/ta (162 keys each), te (178 keys)
│   │   │   ├── app_en.arb / app_hi.arb / app_mr.arb / app_ta.arb / app_te.arb
│   │   │   └── app_localizations*.dart (generated)
│   │   ├── models/
│   │   │   └── user.dart
│   │   ├── providers/
│   │   │   ├── cycle_provider.dart
│   │   │   ├── locale_provider.dart
│   │   │   ├── profile_provider.dart
│   │   │   └── theme_provider.dart
│   │   ├── screens/
│   │   │   ├── assistant/assistant_screen.dart
│   │   │   ├── auth/login_screen.dart, register_screen.dart
│   │   │   ├── cycle/cycle_screen.dart
│   │   │   │   └── components/calendar_grid.dart, log_entry_sheet.dart
│   │   │   ├── home/home_screen.dart
│   │   │   ├── insights/insights_screen.dart
│   │   │   ├── onboarding/onboarding_screen.dart
│   │   │   ├── profile/profile_screen.dart
│   │   │   ├── settings/settings_screen.dart, language_screen.dart, theme_screen.dart
│   │   │   └── sms/sms_screen.dart
│   │   ├── services/
│   │   │   ├── api_client.dart            # Dio instance, base URL config
│   │   │   ├── assistant_service.dart      # Calls backend /assistant/chat
│   │   │   ├── auth_service.dart           # Calls backend /auth/* — real
│   │   │   ├── firestore_service.dart      # STUB — Firebase imports commented out, no-op sync
│   │   │   ├── local_storage_service.dart  # Hive-based local persistence — largest service (363 lines)
│   │   │   └── notification_service.dart   # flutter_local_notifications — wired ONLY to a manual
│   │   │                                     "medicine alert" toggle in Settings, not to period/log reminders
│   │   └── utils/
│   │       └── secure_storage.dart
│   ├── test/
│   │   ├── local_storage_migration_test.dart
│   │   ├── onboarding_test.dart
│   │   ├── widget_test.dart
│   │   └── widgets/calendar_grid_test.dart
│   └── pubspec.yaml
│
├── web/                             # React web app (separate from landing-page!)
│   ├── .env.example
│   ├── index.html
│   ├── package.json                 # React 19 + Vite 8 + TypeScript + react-router-dom + i18next
│   ├── src/
│   │   ├── App.tsx                  # 28 lines — router setup only
│   │   ├── api/client.ts            # axios instance
│   │   ├── auth/
│   │   │   ├── AuthContext.tsx      # 103 lines — real JWT auth context
│   │   │   └── ProtectedRoute.tsx
│   │   ├── i18n/
│   │   │   ├── index.ts
│   │   │   └── locales/en.json, hi.json, mr.json, ta.json, te.json
│   │   ├── pages/
│   │   │   ├── HomePage.tsx         # 17 lines — placeholder, no dashboard/cycle/insights yet
│   │   │   ├── LoginPage.tsx        # 67 lines — real, calls backend
│   │   │   └── RegisterPage.tsx     # 84 lines — real, calls backend
│   │   └── assets/hero.png, react.svg, vite.svg
│   └── vite.config.ts, tsconfig*.json
│
├── landing-page/                    # Next.js marketing site (separate app from web/ above)
│   ├── app/
│   │   ├── layout.tsx, page.tsx, globals.css
│   ├── components/ui/button.tsx     # shadcn/ui component(s)
│   ├── lib/utils.ts
│   ├── public/                       # favicons, logo, placeholder assets
│   ├── package.json                  # Next.js 16 + React 19 + Tailwind 4 + shadcn
│   └── next.config.mjs
│
├── design-concepts/
│   ├── UI_Demo_1.mp4
│   └── UI_Demo_2.mp4
│
├── docs/
│   ├── architecture.md              # 67 lines — high-level only, no CVI/MHS methodology doc
│   └── Rhythma_Blog.docx
│
├── screenshots/                     # 8 PNGs (dashboard, calendar, CVI, MHS, AI assistant, SMS, insights, logo)
│
├── .gitignore
├── CONTRIBUTING.md
├── LICENSE
├── README.md
└── requirements.txt
```

---

## Installation

### Prerequisites

- Flutter SDK 3.x
- Python 3.10+
- Node.js 18+ (only if you're working on `web/`)
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

### Running the Web App

```
cd web
cp .env.example .env.local
# VITE_API_BASE_URL defaults to http://localhost:8000/api/v1, adjust if needed

npm install
npm run dev
```

This gets you a working registration/login flow and a placeholder home page — there's no cycle tracking, AI Assistant, or Insights page here yet (see [Platforms](#platforms)).

> **Note:** Both the Flutter app and the web app now require a real account. Register through either front end's Register screen against a running backend before you'll see anything past the login screen.

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

**Web (`web/.env.local`)**

| Variable | Required | Purpose |
| --- | --- | --- |
| `VITE_API_BASE_URL` | No — defaults to `http://localhost:8000/api/v1` | Backend base URL the web app calls for `/auth`, etc. Vite only exposes `VITE_`-prefixed vars to client code. |

The backend's CORS config already whitelists the Vite dev server (`http://localhost:5173`) alongside `localhost:8000`/`localhost:3000`, so a default local setup works without touching `main.py`.

### Firebase Setup

The backend currently uses Firebase **only for user accounts** (via the Admin SDK). To set it up:

1. Create a Firebase project at [console.firebase.google.com](https://console.firebase.google.com).
2. Generate a service account key: **Project Settings → Service Accounts → Generate new private key**.
3. Either paste the resulting JSON into `FIREBASE_SERVICE_ACCOUNT_JSON`, or save the file and point `FIREBASE_SERVICE_ACCOUNT_PATH` at it.
4. Ensure Firestore is enabled in the project (Native mode).

> **Note:** The Flutter app does not currently initialize Firebase or connect to Firestore on the client side — `firebase_core`, `cloud_firestore`, and `firebase_auth` are listed as dependencies for planned client-side sync but are not yet wired up. No `google-services.json` / `GoogleService-Info.plist` setup is required today.

---

## 🗺️ Roadmap
 
### Phase 1 — Core Mobile App ✅
- Flutter UI for all screens (Home, Cycle, Assistant, Insights)
- Design system and component library
### Phase 2 — AI + Backend Integration 🔄
- FastAPI backend with Gemini API integration
- Real multilingual AI assistant (Hindi, Marathi, Tamil, English)
- Firestore cloud sync and local Hive storage
- Twilio SMS weekly summaries
- XGBoost + logistic regression model serving (CVI + MHS)
### Phase 3 — Web Application
- React / Next.js web app with feature parity
- Dashboard for longitudinal health insights
- Provider-facing view for healthcare professionals
### Phase 4 — WhatsApp Bot
- Gemini-powered WhatsApp assistant via Twilio / Meta API
- Cycle tracking and health Q&A without app installation
- Multilingual support for low-end device users
### Phase 5 — Scale + Impact
- Verified healthcare professional connect
- India regional health map (anonymized PCOD risk heatmap)
- NGO and public health partnerships
- Pilot studies in tier-2/3 cities
  
---

## Contributing
 
Contributions are welcome! Please read [CONTRIBUTING.md](./CONTRIBUTING.md) before submitting a pull request.

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

#### *AI For Every Phase of Her Health.*
