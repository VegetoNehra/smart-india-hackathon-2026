import React, { useState, useEffect } from "react";
import { MapPin, Languages } from "lucide-react";
import SearchableSelect from "../common/SearchableSelect";
import { useLanguage } from "../../context/LanguageContext";

export default function Topbar({
  states = [],
  districts = [],
  selectedStateId,
  selectedDistrictId,
  onStateChange,
  onDistrictChange
}) {
  const [time, setTime] = useState(new Date());
  const { language, toggleLanguage, t } = useLanguage();

  useEffect(() => {
    const timer = setInterval(() => setTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  const formatTime = (date) => {
    const datePart = date.toLocaleDateString(language === "hi" ? "hi-IN" : "en-IN", {
      weekday: "short",
      day: "2-digit",
      month: "short",
      year: "numeric"
    });
    const timePart = date.toLocaleTimeString("en-IN", {
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
      hour12: false
    });
    return `${datePart} · IST ${timePart}`;
  };

  return (
    <div className="flex items-center justify-between gap-5 flex-wrap">
      <div>
        <div className="font-mono text-[11.5px] tracking-[.16em] text-teal-500 uppercase mb-1.5 flex items-center gap-2">
          <span className="w-1.5 h-1.5 rounded-full bg-teal-500 shadow-[0_0_10px_#0891b2] animate-pulse"></span>
          {t("app_title", "Monsoon Intelligence")} · {t("live_model", "Live Model")}
        </div>
        <h1 className="font-display font-semibold text-[27px] tracking-[-0.01em] text-text-hi">
          {t("national_overview", "National Advisory Overview")}
        </h1>
      </div>
      
      <div className="flex items-center gap-3.5 flex-wrap">
        {/* Language Toggle Switcher */}
        <button
          onClick={toggleLanguage}
          className="bg-glass-fill border border-glass-borderSoft hover:border-violet-500/40 backdrop-blur-[20px] rounded-full py-2 px-3 text-[12.5px] text-text-hi font-medium flex items-center gap-1.5 cursor-pointer transition-all duration-200 hover:scale-105 active:scale-95"
          title="Switch Language / भाषा बदलें"
        >
          <Languages size={14} className="text-violet-500 shrink-0" />
          <span className="font-mono text-[11.5px] font-bold">
            {language === "en" ? "EN | हिंदी" : "हिंदी | EN"}
          </span>
        </button>

        {/* State selection searchable dropdown */}
        <div className="flex items-center gap-2">
          <MapPin size={14} className="text-violet-500 shrink-0" />
          <SearchableSelect 
            options={states}
            value={selectedStateId}
            onChange={onStateChange}
            placeholder={t("select_state", "Select State")}
          />
        </div>

        {/* District selection searchable dropdown */}
        <SearchableSelect 
          options={districts}
          value={selectedDistrictId}
          onChange={onDistrictChange}
          placeholder={t("select_district", "Select District")}
        />

        <div className="bg-glass-fill border border-glass-borderSoft backdrop-blur-[20px] rounded-full py-2 px-4 text-[13px] text-text-mid font-sans flex items-center h-full">
          {formatTime(time)}
        </div>
      </div>
    </div>
  );
}
