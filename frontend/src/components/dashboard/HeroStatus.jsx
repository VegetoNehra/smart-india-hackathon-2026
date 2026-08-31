import React from "react";
import { Info } from "lucide-react";

export default function HeroStatus({ selectedRegion, liveForecast }) {
  const probs = liveForecast?.probabilities;
  const adv = liveForecast?.advisory;
  const meta = liveForecast?.metadata;

  const onset7d = probs?.onset?.['7d'] ?? 12;
  const break7d = probs?.break_spell?.['7d'] ?? 85;
  const heavy7d = probs?.heavy_rain?.['7d'] ?? 4;
  const isFalseOnset = adv?.false_onset_risk ?? false;
  const isDirectMatch = meta?.is_direct_match ?? true;
  const resolvedState = meta?.resolved_state ?? "Uttar Pradesh";

  // Derive watch status badge
  let statusText = "NORMAL";
  let statusColor = "text-teal-500 bg-[rgba(52,214,196,0.14)] border-[rgba(52,214,196,0.3)]";

  if (isFalseOnset) {
    statusText = "FALSE-ONSET ALERT";
    statusColor = "text-rose-600 bg-rose-500/20 border-rose-500/30";
  } else if (heavy7d > 60 || break7d > 60) {
    statusText = "HIGH ALERT";
    statusColor = "text-rose-500 bg-rose-500/10 border-rose-500/20";
  } else if (heavy7d > 40 || break7d > 40) {
    statusText = "ELEVATED WATCH";
    statusColor = "text-amber-500 bg-amber-500/10 border-amber-500/20";
  }

  return (
    <div className="glass-panel p-[26px] flex flex-col justify-between h-full">
      <div className="flex justify-between items-start">
        <div>
          <span className="panel-label">7D Monsoon Onset Probability</span>
          <div className="font-display text-[19px] font-semibold mt-1 text-text-hi">
            {selectedRegion?.name || "Uttar Pradesh"}
            <span className="text-text-mid font-normal text-[13px] block mt-0.5 font-sans flex items-center gap-1.5">
              {selectedRegion?.level === "District" ? "District Monitor" : "State Monitor"}
              {!isDirectMatch && (
                <span className="inline-flex items-center gap-1 text-[11px] font-mono text-amber-600 bg-amber-500/10 px-2 py-0.5 rounded border border-amber-500/20" title={`Using regional baseline model (${resolvedState})`}>
                  <Info size={11} /> Regional Baseline ({resolvedState})
                </span>
              )}
            </span>
          </div>
        </div>
        <div className={`font-mono text-[10.5px] py-1 px-2.5 rounded-full border tracking-[.06em] ${statusColor}`}>
          {statusText}
        </div>
      </div>
      
      <div>
        <div className="font-display text-[64px] font-bold leading-none my-4 tracking-[-0.02em] text-transparent bg-clip-text bg-gradient-to-br from-white to-[#b9b2f7]">
          {Math.round(onset7d)}<sup className="text-[28px] opacity-70">%</sup>
        </div>
        <div className="text-text-mid text-[13.5px]">
          Phase 3B Calibrated Model Consensus (Date: 2024-06-15)
        </div>
      </div>
      
      <div className="flex gap-[22px] mt-5 pt-4 border-t border-glass-borderSoft">
        <Metric label="Break Spell (7D)" value={`${Math.round(break7d)}%`} trend={break7d > 50 ? "up" : "neutral"} />
        <Metric label="Heavy Rain (7D)" value={`${Math.round(heavy7d)}%`} trend={heavy7d > 50 ? "up" : "neutral"} />
        <Metric label="Soil Moist." value="25%" trend="down" />
        <Metric label="Confidence" value="88%" trend="neutral" />
      </div>
    </div>
  );
}

function Metric({ label, value, trend }) {
  return (
    <div className="flex flex-col gap-1">
      <span className="font-mono text-[10px] text-text-lo tracking-[.08em] uppercase">{label}</span>
      <span className={`font-display text-[16px] font-semibold ${
        trend === "up" ? "text-rose-500" : trend === "down" ? "text-teal-500" : "text-text-hi"
      }`}>
        {value}
      </span>
    </div>
  );
}
