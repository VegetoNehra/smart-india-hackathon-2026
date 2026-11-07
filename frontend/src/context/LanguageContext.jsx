import React, { createContext, useContext, useState, useEffect } from "react";
import { translations } from "../i18n/translations";

const LanguageContext = createContext();

export function LanguageProvider({ children }) {
  const [language, setLanguageState] = useState(() => {
    return localStorage.getItem("monsoon_lang") || "en";
  });

  const setLanguage = (lang) => {
    if (lang === "en" || lang === "hi") {
      setLanguageState(lang);
      localStorage.setItem("monsoon_lang", lang);
    }
  };

  const toggleLanguage = () => {
    setLanguage(language === "en" ? "hi" : "en");
  };

  const t = (key, defaultText) => {
    const dict = translations[language] || translations["en"];
    if (dict && dict[key] !== undefined) {
      return dict[key];
    }
    const fallbackDict = translations["en"];
    if (fallbackDict && fallbackDict[key] !== undefined) {
      return fallbackDict[key];
    }
    return defaultText || key;
  };

  return (
    <LanguageContext.Provider value={{ language, setLanguage, toggleLanguage, t }}>
      {children}
    </LanguageContext.Provider>
  );
}

export function useLanguage() {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error("useLanguage must be used within a LanguageProvider");
  }
  return context;
}
