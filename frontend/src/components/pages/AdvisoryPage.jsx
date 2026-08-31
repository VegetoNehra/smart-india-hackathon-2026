import React, { useState, useEffect } from "react";
import { AlertTriangle, Calendar, Sprout, Droplets, ShieldAlert, Sparkles } from "lucide-react";
import clsx from "clsx";

const texts = {
  en: {
    title: "AGRICULTURAL ADVISORY",
    subtitle: "Translate climate predictions into actionable farming decisions.",
    actionRequired: "ACTION REQUIRED",
    advisoryTitle: "DELAY SOWING BY 3–4 DAYS",
    advisoryReason: "A possible rainfall event may be followed by a prolonged dry spell. Sowing prematurely could risk germination failure.",
    location: "Meerut",
    crop: "Rice",
    breakProb: "71%",
    soilMoist: "31%",
    confidence: "HIGH",
    sowingTitle: "Delay sowing",
    sowingDesc: "Wait for rainfall persistence before planting.",
    irrigationTitle: "Monitor irrigation",
    irrigationDesc: "Current soil moisture is adequate, but conditions may change.",
    drainageTitle: "Prepare drainage",
    drainageDesc: "Heavy rainfall probability is increasing.",
    healthTitle: "Monitor crop stress",
    healthDesc: "Dry spell probability is elevated.",
    timelineToday: "Monitor conditions",
    timeline3Days: "Avoid premature sowing",
    timeline7Days: "Expected rainfall window",
    timeline14Days: "Possible dry spell"
  },
  hi: {
    title: "कृषि संबंधी सलाह",
    subtitle: "जलवायु पूर्वानुमानों को खेती के व्यावहारिक निर्णयों में बदलें।",
    actionRequired: "कार्रवाई आवश्यक",
    advisoryTitle: "बुवाई में 3-4 दिन की देरी करें",
    advisoryReason: "संभावित बारिश के बाद लंबे समय तक सूखा पड़ सकता है। समय से पहले बुवाई करने से अंकुरण विफल होने का खतरा हो सकता है।",
    location: "मेरठ",
    crop: "धान",
    breakProb: "७१%",
    soilMoist: "३१%",
    confidence: "उच्च",
    sowingTitle: "बुवाई में देरी करें",
    sowingDesc: "रोपण से पहले बारिश की निरंतरता की प्रतीक्षा करें।",
    irrigationTitle: "सिंचाई की निगरानी करें",
    irrigationDesc: "वर्तमान मिट्टी की नमी पर्याप्त है, लेकिन स्थिति बदल सकती है।",
    drainageTitle: "जल निकासी तैयार करें",
    drainageDesc: "भारी बारिश की संभावना बढ़ रही है।",
    healthTitle: "फसल के तनाव की निगरानी करें",
    healthDesc: "सूखे की संभावना बढ़ी हुई है।",
    timelineToday: "स्थितियों की निगरानी करें",
    timeline3Days: "समय से पहले बुवाई से बचें",
    timeline7Days: "अपेक्षित वर्षा की खिड़की",
    timeline14Days: "संभावित सूखा समय"
  }
};

export default function AdvisoryPage() {
  const [lang, setLang] = useState("en");
  const [liveAdvisories, setLiveAdvisories] = useState([]);
  
  const t = texts[lang];

  useEffect(() => {
    fetch('/api/v1/advisories')
      .then(res => res.json())
      .then(data => setLiveAdvisories(data))
      .catch(err => console.error(err));
  }, []);

  return (
    <div className="flex flex-col gap-6">
      {/* Header */}
      <div className="flex justify-between items-start flex-wrap gap-4">
        <div>
          <div className="font-mono text-[11.5px] tracking-[.16em] text-teal-500 uppercase mb-1.5 flex items-center gap-2">
            <span className="w-1.5 h-1.5 rounded-full bg-teal-500 shadow-[0_0_10px_#0891b2] animate-pulse"></span>
            Farmer Decision Support
          </div>
          <h1 className="font-display font-semibold text-[27px] tracking-[-0.01em] text-text-hi uppercase">
            {t.title}
          </h1>
          <p className="text-text-mid text-[14px]">
            {t.subtitle}
          </p>
        </div>

        {/* Language Toggles */}
        <div className="bg-glass-fill border border-glass-borderSoft p-1 rounded-full flex gap-1.5">
          <button 
            onClick={() => setLang("en")}
            className={clsx(
              "font-mono text-[10.5px] px-3.5 py-1 rounded-full cursor-pointer transition-all duration-200 transform hover:scale-105 active:scale-95 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-violet-500/50",
              lang === "en" ? "bg-text-hi text-white font-semibold" : "text-text-mid hover:text-text-hi"
            )}
          >
            English
          </button>
          <button 
            onClick={() => setLang("hi")}
            className={clsx(
              "font-mono text-[10.5px] px-3.5 py-1 rounded-full cursor-pointer transition-all duration-200 transform hover:scale-105 active:scale-95 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-violet-500/50",
              lang === "hi" ? "bg-text-hi text-white font-semibold" : "text-text-mid hover:text-text-hi"
            )}
          >
            हिन्दी
          </button>
        </div>
      </div>

      {/* Main Grid: Highlighted Card & Dynamic Recommendations */}
      <div className="grid grid-cols-1 lg:grid-cols-[1.6fr_1fr] gap-6 items-stretch">
        
        {/* Left Side: Highlighted Decision Card & Grid details */}
        <div className="flex flex-col gap-6">
          {/* Main Action Required Highlight */}
          <div className="glass-panel p-6 border-l-4 border-amber-500 bg-gradient-to-r from-amber-500/5 to-transparent relative overflow-hidden flex flex-col justify-between">
            <div className="absolute -top-12 -right-12 w-48 h-48 bg-amber-500/10 blur-[50px] rounded-full pointer-events-none"></div>
            
            <div>
              <div className="font-mono text-[10px] tracking-[.14em] text-amber-600 font-semibold mb-3 flex items-center gap-1.5 uppercase">
                <AlertTriangle size={14} />
                {t.actionRequired}
              </div>
              <h2 className="font-display font-bold text-[24px] text-text-hi tracking-wide mb-3 leading-tight">
                {t.advisoryTitle}
              </h2>
              <p className="text-[14.5px] text-text-mid leading-relaxed mb-6">
                {t.advisoryReason}
              </p>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-5 gap-4 pt-5 border-t border-glass-borderSoft">
              <AdvisorySpec label="Location" val={t.location} />
              <AdvisorySpec label="Crop" val={t.crop} />
              <AdvisorySpec label="Break Prob." val={t.breakProb} />
              <AdvisorySpec label="Soil Moisture" val={t.soilMoist} />
              <AdvisorySpec label="Confidence" val={t.confidence} highlight />
            </div>
          </div>

          {/* Live API Advisories */}
          {liveAdvisories.length > 0 && (
            <div className="flex flex-col gap-3 mt-2 mb-2">
              <span className="font-mono text-[10px] tracking-[.1em] text-violet-500 uppercase">Live Database Alerts</span>
              {liveAdvisories.map(adv => (
                <div key={adv.id} className="glass-panel p-4 border-l-4 border-rose-500 flex flex-col gap-2">
                  <div className="flex justify-between items-center">
                    <span className="font-mono text-[10px] bg-rose-500/10 text-rose-600 px-2 py-0.5 rounded-full uppercase">{adv.advisory_type} - {adv.crop}</span>
                    <span className="font-mono text-[9px] text-text-lo">{new Date(adv.created_at).toLocaleDateString()}</span>
                  </div>
                  <h4 className="font-display font-semibold text-text-hi text-[15px]">{adv.title}</h4>
                  <p className="text-[13px] text-text-mid leading-relaxed">{adv.message}</p>
                </div>
              ))}
            </div>
          )}

          {/* Sub advisory crop grids */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <SubAdvisoryCard icon={<Sprout size={16} />} title={t.sowingTitle} desc={t.sowingDesc} type="SOWING" />
            <SubAdvisoryCard icon={<Droplets size={16} />} title={t.irrigationTitle} desc={t.irrigationDesc} type="IRRIGATION" />
            <SubAdvisoryCard icon={<ShieldAlert size={16} />} title={t.drainageTitle} desc={t.drainageDesc} type="DRAINAGE" />
            <SubAdvisoryCard icon={<Sparkles size={16} />} title={t.healthTitle} desc={t.healthDesc} type="CROP HEALTH" />
          </div>
        </div>

        {/* Right Side: Timeline */}
        <div className="glass-panel p-5.5 flex flex-col justify-between min-h-[400px]">
          <div>
            <span className="panel-label">Advisory Decision Timeline</span>
            
            <div className="relative mt-8 ml-2 flex flex-col gap-8">
              {/* Vertical line connector */}
              <div className="absolute left-[9px] top-2 bottom-2 w-0.5 bg-gradient-to-b from-violet-500 via-teal-500 to-rose-400"></div>

              <TimelineStep step="TODAY" desc={t.timelineToday} color="bg-violet-500" />
              <TimelineStep step="NEXT 3 DAYS" desc={t.timeline3Days} color="bg-teal-500" />
              <TimelineStep step="NEXT 7 DAYS" desc={t.timeline7Days} color="bg-amber-500" />
              <TimelineStep step="NEXT 14 DAYS" desc={t.timeline14Days} color="bg-rose-500" />
            </div>
          </div>

          <div className="mt-8 pt-5 border-t border-glass-borderSoft text-center text-text-lo text-[11px] font-mono leading-relaxed">
            * advisories compiled by combining global ENSO models, regional weather, and crop stages.
          </div>
        </div>

      </div>
    </div>
  );
}

function AdvisorySpec({ label, val, highlight }) {
  return (
    <div className="flex flex-col gap-1">
      <span className="font-mono text-[9px] text-text-lo tracking-[.06em] uppercase">{label}</span>
      <span className={clsx(
        "font-display text-[14px] font-semibold text-text-hi",
        highlight && "text-teal-600 font-bold"
      )}>
        {val}
      </span>
    </div>
  );
}

function SubAdvisoryCard({ icon, title, desc, type }) {
  return (
    <div className="glass-panel p-5 flex flex-col gap-3">
      <div className="flex justify-between items-center">
        <div className="w-[32px] h-[32px] rounded-lg bg-[rgba(139,124,246,0.18)] text-violet-500 flex items-center justify-center">
          {icon}
        </div>
        <span className="font-mono text-[9px] tracking-[.08em] uppercase text-text-lo">{type}</span>
      </div>
      <div>
        <h4 className="font-display text-[14.5px] font-semibold text-text-hi mb-1">{title}</h4>
        <p className="text-[12.5px] text-text-mid leading-relaxed">{desc}</p>
      </div>
    </div>
  );
}

function TimelineStep({ step, desc, color }) {
  return (
    <div className="flex gap-4 relative z-10">
      <div className={`w-5 h-5 rounded-full ${color} border-4 border-white flex items-center justify-center shrink-0 shadow-[0_2px_8px_rgba(0,0,0,0.1)]`}></div>
      <div className="flex flex-col">
        <span className="font-mono text-[9.5px] text-text-lo uppercase tracking-[.08em] leading-none mb-1">{step}</span>
        <span className="font-display text-[13.5px] font-semibold text-text-hi">{desc}</span>
      </div>
    </div>
  );
}
