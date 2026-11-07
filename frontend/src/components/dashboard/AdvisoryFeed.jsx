import React from "react";
import { AlertTriangle, CloudRain, Droplets } from "lucide-react";
import { useLanguage } from "../../context/LanguageContext";

export default function AdvisoryFeed() {
  const { t } = useLanguage();

  return (
    <div className="glass-panel p-[22px] px-6 h-full">
      <div className="flex justify-between items-center mb-4">
        <h2 className="font-display text-[16px] font-semibold">{t("feed_title", "Recent Alerts & Advisories")}</h2>
        <span className="panel-label">3 Active</span>
      </div>

      <div className="flex flex-col">
        <FeedItem 
          icon={<AlertTriangle size={17} />}
          iconColor="text-amber-500"
          iconBg="bg-[rgba(245,158,11,0.10)]"
          title={t("code_BREAK_SPELL_WARNING_title", "High Dry-Spell Risk")}
          desc={t("code_BREAK_SPELL_WARNING_action", "Delay rain-dependent sowing if practical due to imminent dry spell.")}
          tag="MEERUT · AGRIC ADVISORY"
        />
        
        <FeedItem 
          icon={<CloudRain size={17} />}
          iconColor="text-rose-500"
          iconBg="bg-[rgba(242,99,125,0.18)]"
          title={t("code_HEAVY_RAIN_WARNING_title", "Heavy Rainfall Alert")}
          desc={t("code_HEAVY_RAIN_WARNING_action", "Check and clear field drainage systems to prevent waterlogging.")}
          tag="MEERUT · RISK MODEL"
        />
        
        <FeedItem 
          icon={<Droplets size={17} />}
          iconColor="text-teal-500"
          iconBg="bg-[rgba(52,214,196,0.18)]"
          title={t("code_ROUTINE_MONITORING_title", "Routine Weather Monitoring")}
          desc={t("code_ROUTINE_MONITORING_action", "Continue standard field practices and routine monitoring.")}
          tag="MEERUT · WEATHER"
          noBorder
        />
      </div>
    </div>
  );
}

function FeedItem({ icon, iconColor, iconBg, title, desc, tag, noBorder }) {
  return (
    <div className={`flex gap-3.5 py-3.5 ${!noBorder ? 'border-b border-glass-borderSoft' : ''}`}>
      <div className={`w-9 h-9 rounded-[11px] flex items-center justify-center shrink-0 ${iconBg} ${iconColor}`}>
        {icon}
      </div>
      <div>
        <h3 className="font-display text-[13.5px] font-semibold mb-[3px] text-text-hi">{title}</h3>
        <p className="text-[12.5px] text-text-mid leading-relaxed mb-1.5">{desc}</p>
        <span className="font-mono text-[9.5px] text-text-lo uppercase tracking-[.04em]">{tag}</span>
      </div>
    </div>
  );
}
