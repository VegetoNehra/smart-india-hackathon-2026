import React from "react";
import { Globe, MessageCircle, Smartphone } from "lucide-react";
import { useLanguage } from "../../context/LanguageContext";

export default function DeliveryChannels() {
  const { t } = useLanguage();

  return (
    <div className="glass-panel p-[22px] px-6 h-full flex flex-col gap-4">
      <h2 className="font-display text-[16px] font-semibold mb-1">{t("channel_title", "Distribution Channels")}</h2>
      
      <ChannelRow 
        icon={<Globe size={15} />}
        iconBg="bg-[rgba(139,124,246,0.18)]"
        iconColor="text-violet-500"
        name="Web Portal"
        desc="District dashboards"
        count="12.4k"
      />
      
      <ChannelRow 
        icon={<MessageCircle size={15} />}
        iconBg="bg-[rgba(52,214,196,0.18)]"
        iconColor="text-teal-500"
        name={t("channel_whatsapp", "WhatsApp Bot")}
        desc="Farmer group broadcast"
        count="48.9k"
      />
      
      <ChannelRow 
        icon={<Smartphone size={15} />}
        iconBg="bg-[rgba(245,158,11,0.10)]"
        iconColor="text-amber-500"
        name={t("channel_sms", "SMS Gateway")}
        desc="Low-connectivity regions"
        count="61.2k"
      />
      
      <div className="panel-label mt-1">Last dispatch · 09:00 IST today</div>
    </div>
  );
}

function ChannelRow({ icon, iconBg, iconColor, name, desc, count }) {
  return (
    <div className="flex items-center justify-between p-3 px-3.5 rounded-[14px] bg-glass-fill2 border border-glass-borderSoft hover:-translate-y-0.5 transition-transform cursor-pointer">
      <div className="flex items-center gap-3">
        <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${iconBg} ${iconColor}`}>
          {icon}
        </div>
        <div>
          <div className="font-display text-[13px] font-semibold text-text-hi">{name}</div>
          <div className="text-[11px] text-text-lo">{desc}</div>
        </div>
      </div>
      <div className="font-mono text-[13px] text-text-hi font-medium">{count}</div>
    </div>
  );
}
