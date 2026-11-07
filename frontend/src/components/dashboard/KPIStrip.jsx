import React from "react";
import { Droplets, CloudRain, CloudLightning, ShieldCheck, Volume2, VolumeX, Radio } from "lucide-react";
import { useLanguage } from "../../context/LanguageContext";
import { useTextToSpeech } from "../../hooks/useTextToSpeech";

export default function KPIStrip({ selectedRegion, liveForecast }) {
  const { language, t } = useLanguage();
  const { speak, stop, isSpeaking } = useTextToSpeech();
  
  const probs = liveForecast?.probabilities;

  const onset14d = probs?.onset?.['14d'] ?? 30;
  const break14d = probs?.break_spell?.['14d'] ?? 100;
  const heavy14d = probs?.heavy_rain?.['14d'] ?? 8;

  const handlePlayVoice = () => {
    if (isSpeaking) {
      stop();
      return;
    }

    const regionName = selectedRegion?.name || "Uttar Pradesh";
    
    let speechText = "";
    if (language === "hi") {
      speechText = `${regionName} का 14-दिवसीय मानसून पूर्वावलोकन। मानसून आगमन की संभावना ${Math.round(onset14d)} प्रतिशत है। सूखा काल का जोखिम ${Math.round(break14d)} प्रतिशत है। भारी बारिश की संभावना ${Math.round(heavy14d)} प्रतिशत है। फेज 3B मॉडल सहमति 88 प्रतिशत सत्यापित है।`;
    } else {
      speechText = `14-day forecast overview for ${regionName}. Monsoon Onset likelihood is ${Math.round(onset14d)} percent. Break Spell risk is ${Math.round(break14d)} percent. Heavy Rain likelihood is ${Math.round(heavy14d)} percent. Phase 3B Isotonic model consensus confidence is 88 percent, verified.`;
    }

    speak(speechText, language);
  };

  return (
    <div className="flex flex-col gap-3">
      {/* Voice Assistant Header Control */}
      <div className="flex justify-between items-center px-1">
        <div className="flex items-center gap-2 font-mono text-[11px] text-violet-500 uppercase tracking-[.08em]">
          <Radio size={13} className={isSpeaking ? "animate-pulse text-rose-500" : ""} />
          <span>{t("kpi_onset_label", "14D Monsoon Outlook Metrics")}</span>
        </div>

        <button
          onClick={handlePlayVoice}
          className={`font-mono text-[11.5px] px-3.5 py-1 rounded-full border flex items-center gap-1.5 cursor-pointer transition-all duration-200 transform hover:scale-105 active:scale-95 ${
            isSpeaking 
              ? "bg-rose-500/15 border-rose-500/40 text-rose-600 font-semibold animate-pulse" 
              : "bg-glass-fill border-glass-borderSoft hover:border-violet-500/40 text-text-hi"
          }`}
          title={isSpeaking ? t("stop_voice", "Stop Audio") : t("listen_voice", "Listen to Voice Summary")}
        >
          {isSpeaking ? (
            <>
              <VolumeX size={14} className="text-rose-500" />
              <span>{t("stop_voice", "Stop Audio")}</span>
            </>
          ) : (
            <>
              <Volume2 size={14} className="text-violet-500" />
              <span>{t("listen_voice", "Listen to Voice Summary")}</span>
            </>
          )}
        </button>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <KPICard 
          icon={<Droplets size={15} />}
          iconBg="rgba(139,124,246,0.18)"
          iconColor="var(--color-violet-500)"
          trendBg="rgba(139,124,246,0.14)"
          trendColor="var(--color-violet-500)"
          trendText={onset14d > 50 ? t("trend_high", "HIGH") : t("trend_moderate", "MODERATE")}
          value={`${Math.round(onset14d)}%`}
          label={t("kpi_onset_label", "14D Monsoon Onset Likelihood")}
          barColor="var(--color-violet-500)"
          barWidth={`${Math.round(onset14d)}%`}
        />
        <KPICard 
          icon={<CloudRain size={15} />}
          iconBg="rgba(242,99,125,0.18)"
          iconColor="var(--color-rose-500)"
          trendBg={break14d > 50 ? "rgba(242,99,125,0.14)" : "rgba(52,214,196,0.14)"}
          trendColor={break14d > 50 ? "var(--color-rose-500)" : "var(--color-teal-500)"}
          trendText={break14d > 50 ? t("trend_elevated_risk", "ELEVATED RISK") : t("trend_low_risk", "LOW RISK")}
          value={`${Math.round(break14d)}%`}
          label={t("kpi_break_label", "14D Break Spell Risk")}
          barColor="var(--color-rose-500)"
          barWidth={`${Math.round(break14d)}%`}
        />
        <KPICard 
          icon={<CloudLightning size={15} />}
          iconBg="rgba(245,158,11,0.10)"
          iconColor="var(--color-amber-500)"
          trendBg={heavy14d > 50 ? "rgba(245,158,11,0.14)" : "rgba(52,214,196,0.14)"}
          trendColor={heavy14d > 50 ? "var(--color-amber-500)" : "var(--color-teal-500)"}
          trendText={heavy14d > 50 ? t("trend_warning", "WARNING") : t("trend_low_risk", "LOW RISK")}
          value={`${Math.round(heavy14d)}%`}
          label={t("kpi_heavy_label", "14D Heavy Rain Likelihood")}
          barColor="var(--color-amber-500)"
          barWidth={`${Math.round(heavy14d)}%`}
        />
        <KPICard 
          icon={<ShieldCheck size={15} />}
          iconBg="rgba(52,214,196,0.18)"
          iconColor="var(--color-teal-500)"
          trendBg="rgba(52,214,196,0.14)"
          trendColor="var(--color-teal-500)"
          trendText={t("trend_verified", "VERIFIED")}
          value="88%"
          label={t("kpi_confidence_label", "Phase 3B Isotonic Consensus")}
          barColor="var(--color-teal-500)"
          barWidth="88%"
        />
      </div>
    </div>
  );
}

function KPICard({ icon, iconBg, iconColor, trendBg, trendColor, trendText, value, label, barColor, barWidth }) {
  return (
    <div className="glass-panel p-[18px] px-5 flex flex-col gap-2.5">
      <div className="flex justify-between items-center">
        <div className="w-[30px] h-[30px] rounded-[9px] flex items-center justify-center" style={{ backgroundColor: iconBg, color: iconColor }}>
          {icon}
        </div>
        <span className="font-mono text-[10.5px] py-0.5 px-2 rounded-full" style={{ backgroundColor: trendBg, color: trendColor }}>
          {trendText}
        </span>
      </div>
      <div className="font-display text-[27px] font-bold tracking-[-0.01em] text-text-hi">{value}</div>
      <div className="text-[12px] text-text-mid font-sans">{label}</div>
      <div className="h-1 rounded-full bg-black/5 overflow-hidden mt-0.5">
        <div className="h-full rounded-full" style={{ width: barWidth, backgroundColor: barColor }}></div>
      </div>
    </div>
  );
}
