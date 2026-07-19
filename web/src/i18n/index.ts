import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

import en from './locales/en.json';
import hi from './locales/hi.json';
import mr from './locales/mr.json';
import ta from './locales/ta.json';
import te from './locales/te.json';

// Matches the Flutter app's 5 supported locales exactly: English, Hindi,
// Marathi, Tamil, Telugu. hi/mr/ta/te are currently English-text
// placeholders (infrastructure only, per this issue's scope) — real
// translations are a follow-up, not part of this scaffold.
i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources: {
      en: { translation: en },
      hi: { translation: hi },
      mr: { translation: mr },
      ta: { translation: ta },
      te: { translation: te },
    },
    fallbackLng: 'en',
    interpolation: { escapeValue: false },
  });

export default i18n;
