import React from "react";
import { TriangleAlert, Sprout, Wind, Droplet, ShieldAlert, CheckCircle2 } from "lucide-react";

export default function AdvisoryCard({ liveForecast }) {
  const adv = liveForecast?.advisory;
  const meta = liveForecast?.metadata;

  const title = adv?.title || "Delay sowing by 3–4 days";
  const primaryAction = adv?.primary_action || "A possible dry spell may follow expected rainfall. Delay rain-dependent sowing until sustained moisture settles.";
  const supportingActions = adv?.supporting_actions || [
    "Prepare supplemental irrigation facilities",
    "Keep nursery beds covered and hydrated"
  ];
  const cropName = adv?.crop_name || "Rice";
  const stage = adv?.growth_stage || "Sowing";
  const riskLevel = adv?.risk_level || "HIGH";
  const isFalseOnset = adv?.false_onset_risk || false;
  const isDirectMatch = meta?.is_direct_match ?? true;
  const resolvedState = meta?.resolved_state ?? "Uttar Pradesh";

  return (
    <div className="glass-panel p-[24px] relative overflow-hidden bg-gradient-to-br from-[rgba(245,158,11,0.05)] to-transparent">
      {/* Decorative background element */}
      <div className="absolute -top-10 -right-10 w-40 h-40 bg-amber-500/10 blur-[40px] rounded-full pointer-events-none"></div>

      <div className="font-mono text-[10.5px] tracking-[.14em] uppercase text-amber-600 font-semibold mb-4 flex items-center justify-between">
        <div className="flex items-center gap-2">
          {isFalseOnset ? <ShieldAlert size={14} className="text-rose-500" /> : <TriangleAlert size={14} />}
          <span>Phase 6 Agricultural Advisory</span>
        </div>
        <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
          riskLevel === 'HIGH' || riskLevel === 'VERY_HIGH' ? 'bg-rose-500/20 text-rose-600' : 'bg-amber-500/20 text-amber-600'
        }`}>
          {riskLevel} RISK
        </span>
      </div>
      
      <h2 className="font-display text-[20px] font-bold text-text-hi mb-3 leading-tight uppercase">
        {title}
      </h2>
      
      <p className="text-[14px] text-text-mid leading-relaxed mb-4 max-w-xl">
        {primaryAction}
      </p>

      {supportingActions.length > 0 && (
        <div className="mb-6 space-y-1.5">
          {supportingActions.map((action, idx) => (
            <div key={idx} className="flex items-center gap-2 text-[13px] text-text-mid font-sans">
              <CheckCircle2 size={13} className="text-teal-500 shrink-0" />
              <span>{action}</span>
            </div>
          ))}
        </div>
      )}
      
      <div className="flex flex-wrap gap-6 border-t border-glass-borderSoft pt-5">
        <div className="flex items-center gap-2 text-[13px] text-text-hi font-medium">
          <div className="w-7 h-7 rounded-lg bg-[rgba(52,214,196,0.18)] text-teal-500 flex items-center justify-center">
            <Sprout size={14} />
          </div>
          {cropName} ({stage})
        </div>
        <div className="flex items-center gap-2 text-[13px] text-text-hi font-medium">
          <div className="w-7 h-7 rounded-lg bg-[rgba(139,124,246,0.18)] text-violet-500 flex items-center justify-center">
            <Droplet size={14} />
          </div>
          Soil Moist: 25%
        </div>
        <div className="flex items-center gap-2 text-[13px] text-text-hi font-medium">
          <div className="w-7 h-7 rounded-lg bg-[rgba(245,158,11,0.15)] text-amber-600 flex items-center justify-center">
            <Wind size={14} />
          </div>
          {isDirectMatch ? "Direct Phase 3B Model" : `Regional Baseline (${resolvedState})`}
        </div>
      </div>
    </div>
  );
}
