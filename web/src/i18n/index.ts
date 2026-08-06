import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

import en from './locales/en.json';
import gu from './locales/gu.json';
import hi from './locales/hi.json';
import kn from './locales/kn.json';
import ml from './locales/ml.json';
import mr from './locales/mr.json';
import ta from './locales/ta.json';
import te from './locales/te.json';
import bn from './locales/bn.json';

// Matches the Flutter app's supported locales: English, Hindi, Kannada,
// Malayalam, Marathi, Tamil, Telugu, and Bengali. Kannada and Malayalam translations
// are included, while hi/mr/ta/te/bn currently use placeholder translations and
// can be localized in future updates.
i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources: {
      en: { translation: en },
      gu: { translation: gu },
      hi: { translation: hi },
      kn: { translation: kn },
      ml: { translation: ml },
      mr: { translation: mr },
      ta: { translation: ta },
      te: { translation: te },
      bn: { translation: bn },
    },
    fallbackLng: 'en',
    interpolation: { escapeValue: false },
  });

export default i18n;