import React, { useState } from "react";
import { Check, Settings, ShieldCheck, MapPin, Bell, Globe, LayoutGrid } from "lucide-react";
import clsx from "clsx";
import SearchableSelect from "../common/SearchableSelect";

export default function SettingsPage({
  states = [],
  districts = [],
  selectedStateId,
  selectedDistrictId,
  onStateChange,
  onDistrictChange
}) {
  const [lang, setLang] = useState("en");
  const [density, setDensity] = useState("compact");
  const [techInfo, setTechInfo] = useState(true);
  
  const [alerts, setAlerts] = useState({
    rainfall: true,
    dryspell: true,
    onset: true,
    irrigation: false
  });

  const toggleAlert = (key) => {
    setAlerts(prev => ({ ...prev, [key]: !prev[key] }));
  };

  return (
    <div className="flex flex-col gap-6 max-w-4xl mx-auto w-full">
      {/* Header */}
      <div>
        <div className="font-mono text-[11.5px] tracking-[.16em] text-teal-500 uppercase mb-1.5 flex items-center gap-2">
          <Settings size={13} className="animate-spin" />
          Application Preferences
        </div>
        <h1 className="font-display font-semibold text-[27px] tracking-[-0.01em] text-text-hi uppercase">
          SETTINGS
        </h1>
        <p className="text-text-mid text-[14px]">Customize your Monsoon Intelligence experience</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        
        {/* Left Side: Location & Crop Settings */}
        <div className="flex flex-col gap-6">
          {/* Default Location Card */}
          <div className="glass-panel p-5.5 flex flex-col gap-4">
            <h3 className="font-display font-semibold text-[15px] flex items-center gap-2 text-text-hi">
              <MapPin size={16} className="text-violet-500" /> Default Location
            </h3>
            
            <div className="grid grid-cols-2 gap-4">
              <div className="flex flex-col gap-1.5 font-sans">
                <label className="text-[10px] font-mono tracking-[.06em] uppercase text-text-lo">State</label>
                <SearchableSelect 
                  options={states}
                  value={selectedStateId}
                  onChange={onStateChange}
                  placeholder="Select State"
                />
              </div>

              <div className="flex flex-col gap-1.5 font-sans">
                <label className="text-[10px] font-mono tracking-[.06em] uppercase text-text-lo">District</label>
                <SearchableSelect 
                  options={districts}
                  value={selectedDistrictId}
                  onChange={onDistrictChange}
                  placeholder="Select District"
                />
              </div>

              <SelectBox label="Block" defaultValue="Block A" options={["Block A"]} />
              <SelectBox label="Panchayat" defaultValue="Panchayat X" options={["Panchayat X"]} />
            </div>
          </div>

          {/* Crop Preferences Card */}
          <div className="glass-panel p-5.5 flex flex-col gap-4">
            <h3 className="font-display font-semibold text-[15px] flex items-center gap-2 text-text-hi">
              <ShieldCheck size={16} className="text-teal-500" /> Crop Preferences
            </h3>
            <SelectBox 
              label="Primary Crop" 
              defaultValue="Rice" 
              options={["Rice", "Wheat", "Maize", "Cotton", "Sugarcane", "Pulses"]} 
            />
          </div>
        </div>

        {/* Right Side: Alert & Display Settings */}
        <div className="flex flex-col gap-6">
          {/* Alert Preferences */}
          <div className="glass-panel p-5.5 flex flex-col gap-4">
            <h3 className="font-display font-semibold text-[15px] flex items-center gap-2 text-text-hi">
              <Bell size={16} className="text-rose-500" /> Alert Notifications
            </h3>
            
            <div className="flex flex-col gap-3 font-sans">
              <ToggleRow label="Heavy Rainfall Alerts" active={alerts.rainfall} onClick={() => toggleAlert("rainfall")} />
              <ToggleRow label="Dry Spell Alerts" active={alerts.dryspell} onClick={() => toggleAlert("dryspell")} />
              <ToggleRow label="Monsoon Onset Alerts" active={alerts.onset} onClick={() => toggleAlert("onset")} />
              <ToggleRow label="Irrigation Recommendations" active={alerts.irrigation} onClick={() => toggleAlert("irrigation")} />
            </div>
          </div>

          {/* Display & Language Settings */}
          <div className="glass-panel p-5.5 flex flex-col gap-4">
            <h3 className="font-display font-semibold text-[15px] flex items-center gap-2 text-text-hi">
              <LayoutGrid size={16} className="text-amber-500" /> Preferences & Display
            </h3>
            
            {/* Language */}
            <div className="flex justify-between items-center py-1">
              <span className="text-[13.5px] text-text-mid font-sans">Application Language</span>
              <div className="flex gap-1">
                {["en", "hi"].map((l) => (
                  <button
                    key={l}
                    onClick={() => setLang(l)}
                    className={clsx(
                      "font-mono text-[10px] px-3 py-1 rounded-full cursor-pointer transition-all duration-200 transform hover:scale-105 active:scale-95 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-violet-500/50 border",
                      lang === l 
                        ? "bg-text-hi text-white border-transparent" 
                        : "bg-glass-fill2 border-glass-borderSoft text-text-mid hover:text-text-hi"
                    )}
                  >
                    {l === "en" ? "English" : "हिन्दी"}
                  </button>
                ))}
              </div>
            </div>

            {/* Density */}
            <div className="flex justify-between items-center py-1">
              <span className="text-[13.5px] text-text-mid font-sans">Dashboard Density</span>
              <div className="flex gap-1">
                {["comfortable", "compact"].map((d) => (
                  <button
                    key={d}
                    onClick={() => setDensity(d)}
                    className={clsx(
                      "font-mono text-[10px] px-3 py-1 rounded-full cursor-pointer transition-all duration-200 transform hover:scale-105 active:scale-95 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-violet-500/50 border",
                      density === d 
                        ? "bg-text-hi text-white border-transparent" 
                        : "bg-glass-fill2 border-glass-borderSoft text-text-mid hover:text-text-hi"
                    )}
                  >
                    {d.toUpperCase()}
                  </button>
                ))}
              </div>
            </div>

            {/* Show Tech Info */}
            <ToggleRow label="Show Technical Climate Info" active={techInfo} onClick={() => setTechInfo(!techInfo)} />

          </div>
        </div>

      </div>
    </div>
  );
}

function SelectBox({ label, defaultValue, options }) {
  return (
    <div className="flex flex-col gap-1.5 font-sans">
      <label className="text-[10px] font-mono tracking-[.06em] uppercase text-text-lo">{label}</label>
      <select 
        defaultValue={defaultValue} 
        className="w-full bg-glass-fill2 border border-glass-borderSoft px-3 py-2 text-[13.5px] text-text-hi rounded-xl outline-none transition-all duration-200 hover:bg-glass-fill focus:ring-2 focus:ring-violet-500/50 focus:border-transparent cursor-pointer"
      >
        {options.map((opt) => (
          <option key={opt} value={opt}>{opt}</option>
        ))}
      </select>
    </div>
  );
}

function ToggleRow({ label, active, onClick }) {
  return (
    <div className="flex justify-between items-center py-1">
      <span className="text-[13.5px] text-text-mid">{label}</span>
      <button 
        onClick={onClick}
        className={clsx(
          "w-10 h-6.5 rounded-full p-1 cursor-pointer transition-all duration-200 transform hover:scale-105 active:scale-95 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-500/50 relative",
          active ? "bg-teal-500" : "bg-black/10"
        )}
      >
        <div className={clsx(
          "w-[18px] h-[18px] rounded-full bg-white transition-all shadow-md",
          active ? "translate-x-3.5" : "translate-x-0"
        )}></div>
      </button>
    </div>
  );
}
