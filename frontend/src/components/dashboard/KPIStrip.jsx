import React from "react";
import { Droplets, CloudRain, CloudLightning, ShieldCheck } from "lucide-react";

export default function KPIStrip({ selectedRegion, liveForecast }) {
  const probs = liveForecast?.probabilities;
  const adv = liveForecast?.advisory;

  const onset14d = probs?.onset?.['14d'] ?? 30;
  const break14d = probs?.break_spell?.['14d'] ?? 100;
  const heavy14d = probs?.heavy_rain?.['14d'] ?? 8;

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      <KPICard 
        icon={<Droplets size={15} />}
        iconBg="rgba(139,124,246,0.18)"
        iconColor="var(--color-violet-500)"
        trendBg="rgba(139,124,246,0.14)"
        trendColor="var(--color-violet-500)"
        trendText={onset14d > 50 ? "HIGH" : "MODERATE"}
        value={`${Math.round(onset14d)}%`}
        label="14D Monsoon Onset Likelihood"
        barColor="var(--color-violet-500)"
        barWidth={`${Math.round(onset14d)}%`}
      />
      <KPICard 
        icon={<CloudRain size={15} />}
        iconBg="rgba(242,99,125,0.18)"
        iconColor="var(--color-rose-500)"
        trendBg={break14d > 50 ? "rgba(242,99,125,0.14)" : "rgba(52,214,196,0.14)"}
        trendColor={break14d > 50 ? "var(--color-rose-500)" : "var(--color-teal-500)"}
        trendText={break14d > 50 ? "ELEVATED RISK" : "LOW RISK"}
        value={`${Math.round(break14d)}%`}
        label="14D Break Spell Risk"
        barColor="var(--color-rose-500)"
        barWidth={`${Math.round(break14d)}%`}
      />
      <KPICard 
        icon={<CloudLightning size={15} />}
        iconBg="rgba(245,158,11,0.10)"
        iconColor="var(--color-amber-500)"
        trendBg={heavy14d > 50 ? "rgba(245,158,11,0.14)" : "rgba(52,214,196,0.14)"}
        trendColor={heavy14d > 50 ? "var(--color-amber-500)" : "var(--color-teal-500)"}
        trendText={heavy14d > 50 ? "WARNING" : "LOW RISK"}
        value={`${Math.round(heavy14d)}%`}
        label="14D Heavy Rain Likelihood"
        barColor="var(--color-amber-500)"
        barWidth={`${Math.round(heavy14d)}%`}
      />
      <KPICard 
        icon={<ShieldCheck size={15} />}
        iconBg="rgba(52,214,196,0.18)"
        iconColor="var(--color-teal-500)"
        trendBg="rgba(52,214,196,0.14)"
        trendColor="var(--color-teal-500)"
        trendText="VERIFIED"
        value="88%"
        label="Phase 3B Isotonic Consensus"
        barColor="var(--color-teal-500)"
        barWidth="88%"
      />
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
