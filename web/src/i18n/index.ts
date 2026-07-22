import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

import en from './locales/en.json';
import hi from './locales/hi.json';
import kn from './locales/kn.json';
import ml from './locales/ml.json';
import mr from './locales/mr.json';
import ta from './locales/ta.json';
import te from './locales/te.json';

// Matches the Flutter app's supported locales: English, Hindi, Kannada,
// Malayalam, Marathi, Tamil, and Telugu. Kannada and Malayalam translations
// are included, while hi/mr/ta/te currently use placeholder translations and
// can be localized in future updates.
i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources: {
      en: { translation: en },
      hi: { translation: hi },
      kn: { translation: kn },
      ml: { translation: ml },
      mr: { translation: mr },
      ta: { translation: ta },
      te: { translation: te },
    },
    fallbackLng: 'en',
    interpolation: { escapeValue: false },
  });

export default i18n;