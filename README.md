# Rhythma 🌸
### *Her Rhythm. Her Health. Her Power.*

> A multilingual, offline-capable AI-powered women's health companion designed for Indian women.

[![Flutter](https://img.shields.io/badge/Flutter-3.x-blue?logo=flutter)](https://flutter.dev)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green?logo=fastapi)](https://fastapi.tiangolo.com)
[![Gemini API](https://img.shields.io/badge/Gemini-API-orange?logo=google)](https://ai.google.dev)
[![License: MIT](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Active%20Development-brightgreen)]()

---

## 🎯 The Problem

1 in 5 Indian women have PCOD — yet **70% of cases go undetected for years**. Women in tier-2 and tier-3 cities face a uniquely difficult combination of challenges:

- Popular apps (Flo, Clue) assume 28-day cycles, English fluency, and stable internet
- Limited access to gynecologists in smaller cities
- Deep social stigma that prevents open conversations about menstrual health
- No AI-powered early detection tool built specifically for Indian languages and contexts

**Rhythma was built from the ground up for Indian women — not adapted from a solution built for another market.**

---

## ✨ What Rhythma Does

Users can track menstrual cycles, symptoms, mood, sleep, and lifestyle habits. Using this data, Rhythma identifies long-term patterns and surfaces personalised health insights — helping women understand their health earlier, privately, and in their own language.

| Metric | Value |
|--------|-------|
| Target users | Women in tier-2 / tier-3 India |
| Languages supported | Hindi, Marathi, Tamil + more planned |
| Health scores | CVI™ + MHS™ (proprietary scoring) |
| Connectivity | Offline-first, syncs when online |

---

## 🚀 Key Features

|                    Feature                        | Description |
|---------|-------------|
| 🌸 **Smart Cycle Tracking** | Handles irregular cycles. No fixed 28-day assumption. Tracks flow, mood, and daily symptoms. |
| 🤖 **Gemini-Powered AI Assistant** | Multilingual health education and wellness guidance in Hindi, Marathi, Tamil, English, and more. |
| 📊 **Cycle Variability Index™ (CVI)** | Proprietary 0–100 score quantifying hormonal instability over rolling 6–12 months. |
| ❤️ **Menstrual Health Score™ (MHS)** | Holistic composite score: CVI + lifestyle + sleep + stress + symptoms. |
| 🏥 **Hormonal Risk Indicator** | 3-tier alert system (Low / Medium / High) based on cycle gaps and symptom clusters. |
| 📱 **Offline-First Architecture** | Hive local storage → Firestore cloud sync when connectivity is available. |
| 🔒 **Privacy-First Design** | AES-256 on-device encryption. No data leaves the phone without explicit user consent. |
| 🌍 **Indian Regional Languages** | Designed for linguistic diversity across India. |
| 📩 **SMS Health Summaries** | Weekly summaries via Twilio SMS for users in low-data areas. |
| 🌿 **Ayurvedic Correlation Layer** | Educational wellness insights inspired by Ayurvedic principles. |

---

## 🛠️ Technology Stack

| Technology | Role | Why |
|------------|------|-----|
| **Flutter** | Cross-platform mobile app (Android + iOS) | Single codebase for diverse Indian devices |
| **Gemini API** | Multilingual AI health assistant | Native multilingual support across Indian languages without separate models |
| **Google Firestore** | Cloud sync + offline support | Pairs with Hive for offline-first architecture |
| **FastAPI** | Backend APIs, auth, SMS dispatch | Lightweight async Python backend |
| **Hive** | Local offline storage | Fast, lightweight; keeps sensitive data on-device |
| **Twilio SMS** | Weekly health summary delivery | Reaches users without reliable data access |
| **XGBoost** | Cycle Variability Index (CVI) engine | Efficient inference on mid-range Android devices |
| **Logistic Regression** | Menstrual Health Score (MHS) | Interpretable scoring layer |
| **AES-256 Encryption** | Data security | All locally stored health data encrypted at rest |

> **ML models run entirely on-device.** No sensitive health data leaves the phone unless the user explicitly enables cloud sync.

---

## 📂 Repository Structure

```
Rhythma/
│
├── rhythma_flutter/          # Flutter mobile application (Android + iOS)
│   ├── lib/
│   │   ├── main.dart
│   │   ├── config/
│   │   │   └── theme.dart
│   │   ├── components/
│   │   │   ├── bottom_nav.dart
│   │   │   ├── charts.dart
│   │   │   └── shared.dart
│   │   └── screens/
│   │       ├── home/
│   │       ├── cycle/
│   │       ├── assistant/
│   │       ├── insights/
│   │       └── sms/
│   └── pubspec.yaml
│
├── backend/                  # FastAPI backend (planned / in progress)
│   ├── api/                  # Route handlers
│   ├── models/               # ML models (CVI, MHS)
│   ├── services/             # Gemini, Firestore, Twilio integrations
│   └── utils/                # Helpers, encryption, validators
│
├── data/
│   └── sample_datasets/      # Anonymized sample data for model training
│
├── docs/
│   └── architecture.md       # System design documentation
│
├── design-concepts/          # UI reference videos (UI_Demo_1, UI_Demo_2)
├── screenshots/              # App screenshots and logo
│
├── README.md
├── LICENSE
├── CONTRIBUTING.md
├── requirements.txt
└── .gitignore
```

---

## 🏗️ Current Status

| Component | Status |
|-----------|--------|
| Flutter UI screens | ✅ Complete |
| Design System & Theme Tokens | ✅ Complete |
| Charts & Visual Components | ✅ Complete |
| Navigation & User Flows | ✅ Complete |
| Local Demo Data Integration | ✅ Complete |
| Backend APIs (FastAPI) | 🚧 Not Started |
| Gemini API Integration | 🚧 Not Started |
| Firestore Cloud Sync | 🚧 Not Started |
| Hive Local Storage Integration | 🚧 Not Started |
| Cycle Variability Index (CVI) Engine | 🚧 Not Started |
| Menstrual Health Score (MHS) Engine | 🚧 Not Started |
| SMS Notifications (Twilio) | 🚧 Not Started |
| Authentication & User Accounts | 🚧 Not Started |
| Web Application | 🚧 Planned |
| WhatsApp Bot Integration | 🚧 Planned |

##### **Current Version:** Rhythma currently includes the complete Flutter frontend, UI screens, design system, and user experience flows. Backend services, AI capabilities, cloud synchronization, authentication, and health-scoring models are under development.
---

## ⚡ Getting Started

### Prerequisites

- Flutter SDK 3.x
- Python 3.10+
- Git
- Firebase / Firestore account
- Gemini API key ([get one here](https://ai.google.dev))
- Twilio account (optional, for SMS)

### Flutter (Frontend)

```bash
# Clone the repo
git clone https://github.com/ishita2740/Rhythma.git
cd Rhythma/rhythma_flutter

# Install packages
flutter pub get

# Run the app
flutter run
```

### Backend (FastAPI) — Coming Soon

```bash
cd backend

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate        # Linux / macOS
# venv\Scripts\activate         # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Fill in: GEMINI_API_KEY, FIREBASE_PROJECT_ID, TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN

# Start server
uvicorn main:app --reload
```

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
- XGBoost + LR model serving (CVI + MHS)

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

## ⚠️ Disclaimer

Rhythma AI is intended for **educational and preventive health awareness purposes only**. It is not a medical device and does not provide diagnoses, prescriptions, or medical treatment recommendations. Users should always consult qualified healthcare professionals for medical advice. Experimental health-awareness metrics currently under development and intended for educational insights only.

---

## 📖 Read the Story

[Building Rhythma: An AI health companion for the women India's apps forgot](https://medium.com/@rathiishita1005729/building-rhythma-an-ai-health-companion-for-the-women-indias-forgot-e249ac1cdc9a) — Medium

---

## 🤝 Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) before submitting a pull request.

---

## 📄 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

*Built with 💜 by [Ishita Rathi](https://github.com/ishita2740) for the women India's apps forgot.*
#### *AI For Every Phase of Her Health.*
