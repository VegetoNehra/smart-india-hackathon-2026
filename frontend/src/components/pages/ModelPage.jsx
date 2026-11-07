import React, { useState } from "react";
import { Cpu, Brain, CheckCircle2, Calendar, Hourglass, Activity, ShieldCheck, BarChart2, Layers, Info, Filter } from "lucide-react";
import clsx from "clsx";
import { useLanguage } from "../../context/LanguageContext";

// Stage metadata for interactive pipeline inspection
const STAGE_DETAILS = {
  1: {
    title: "Global Macro Indices (ENSO / IOD / MJO)",
    type: "Climate Data Layer",
    desc: "Captures large-scale ocean-atmosphere oscillations including Nino 3.4 SST Anomaly, SOI, ONI, RONI, Indian Ocean Dipole (IOD_Index), and Madden-Julian Oscillation (RMM1, RMM2, Amplitude, Phase).",
    inputs: "NOAA CPC, BOM Australia, Bureau of Meteorology MJO bulletins.",
    formula: "MJO Amplitude = sqrt(RMM1^2 + RMM2^2), Phase = atan2(RMM2, RMM1)"
  },
  2: {
    title: "ERA5 & IMD Daily Meteorological Telemetry",
    type: "Meteorological Feature Layer",
    desc: "Extracts daily observational rainfall series strictly on or before forecast date T. Computes rolling sums, rolling means, and rolling maximums over 3D, 7D, 14D, and 30D windows.",
    inputs: "IMD High-Resolution Gridded Rainfall Dataset (0.25° x 0.25°) + ERA5 Reanalysis.",
    formula: "Rolling 14D Sum = sum(R_{T-13} ... R_T)"
  },
  3: {
    title: "Phase 3B Feature Engineering Matrix",
    type: "Feature Store (30 Features)",
    desc: "Assembles the exact 30 Phase 3B features in strict order: rainfall lags, consecutive dry days, consecutive rain days, trend, sine/cosine day-of-year seasonality, and lagged climate indices.",
    inputs: "Strict temporal boundary enforce: Data strictly <= T (Zero future data leakage).",
    formula: "sin_doy = sin(2 * pi * DOY / 365.25), cos_doy = cos(2 * pi * DOY / 365.25)"
  },
  4: {
    title: "12 Frozen XGBoost Classifiers",
    type: "XGBoost Machine Learning Core",
    desc: "12 distinct Gradient Boosted Decision Tree models trained independently for each event target (Onset, Break Spell, Heavy Rain) across 4 lead horizons (7D, 14D, 21D, 30D).",
    inputs: "Chronological Train Set (2022-2023, 6,570 records). Frozen artifacts in backend/models/event_models/.",
    formula: "P_raw(y=1|X) = sigmoid(sum(f_k(X)))"
  },
  5: {
    title: "Isotonic Regression Probability Calibrator",
    type: "Probability Calibration Engine",
    desc: "Maps raw XGBoost confidence scores to true empirical probabilities using non-parametric monotonic step functions fitted on 2024 validation data.",
    inputs: "Validation Set (2024, 3,294 records). ECE < 0.04.",
    formula: "P_calibrated = IsotonicFit(P_raw)"
  },
  6: {
    title: "Phase 6 Agricultural Advisory Engine",
    type: "Deterministic Rule Engine",
    desc: "Evaluates calibrated probabilities against crop growth stage sensitivities to issue priority-ranked advisories and trigger False-Onset Risk Warnings.",
    inputs: "Calibrated Probabilities + Crop Context (Rice, Maize, Cotton, Soybean).",
    formula: "FALSE_ONSET_WARNING if Onset_14d >= 60% AND Break_14d >= 50%"
  }
};

// Comprehensive feature importance resolver covering all 12 model targets
function getFeatureImportances(horizon, eventType) {
  if (eventType === "ONSET") {
    if (horizon === "7D") {
      return [
        { label: "Rainfall 7D Sum & Trend", weight: 36, color: "bg-teal-500" },
        { label: "Nino 3.4 SST Anomaly", weight: 22, color: "bg-violet-500" },
        { label: "MJO Phase & Amplitude", weight: 18, color: "bg-indigo-500" },
        { label: "Consecutive Rain Days", weight: 12, color: "bg-emerald-500" },
        { label: "IOD Dipole Index", weight: 8, color: "bg-amber-500" },
        { label: "Seasonal Sine Day-of-Year", weight: 4, color: "bg-slate-400" },
      ];
    } else if (horizon === "14D") {
      return [
        { label: "Nino 3.4 SST Anomaly", weight: 30, color: "bg-violet-500" },
        { label: "Rainfall 14D Sum", weight: 25, color: "bg-teal-500" },
        { label: "MJO Phase & Amplitude", weight: 20, color: "bg-indigo-500" },
        { label: "IOD Dipole Index", weight: 13, color: "bg-amber-500" },
        { label: "Consecutive Rain Days", weight: 8, color: "bg-emerald-500" },
        { label: "Seasonal Sine Day-of-Year", weight: 4, color: "bg-slate-400" },
      ];
    } else if (horizon === "21D") {
      return [
        { label: "Nino 3.4 SST Anomaly", weight: 34, color: "bg-violet-500" },
        { label: "IOD Dipole Index", weight: 24, color: "bg-amber-500" },
        { label: "MJO Phase & Amplitude", weight: 18, color: "bg-indigo-500" },
        { label: "Rainfall 30D Sum", weight: 12, color: "bg-teal-500" },
        { label: "ONIE / RONI Index", weight: 8, color: "bg-rose-500" },
        { label: "Seasonal Cosine Day-of-Year", weight: 4, color: "bg-slate-400" },
      ];
    } else { // 30D
      return [
        { label: "Nino 3.4 SST Anomaly", weight: 38, color: "bg-violet-500" },
        { label: "IOD Dipole Index", weight: 26, color: "bg-amber-500" },
        { label: "ONIE / RONI Index", weight: 16, color: "bg-rose-500" },
        { label: "MJO Phase & Amplitude", weight: 10, color: "bg-indigo-500" },
        { label: "Rainfall 30D Mean", weight: 6, color: "bg-teal-500" },
        { label: "Seasonal Sine Day-of-Year", weight: 4, color: "bg-slate-400" },
      ];
    }
  } else if (eventType === "BREAK SPELL") {
    if (horizon === "7D") {
      return [
        { label: "Consecutive Dry Days Streak", weight: 38, color: "bg-rose-500" },
        { label: "Rainfall 7D Sum", weight: 28, color: "bg-violet-500" },
        { label: "MJO Amplitude (Phase 1/8)", weight: 16, color: "bg-teal-500" },
        { label: "IOD Dipole Index", weight: 10, color: "bg-amber-500" },
        { label: "Nino 3.4 SST Anomaly", weight: 5, color: "bg-indigo-400" },
        { label: "Seasonal Cosine Day-of-Year", weight: 3, color: "bg-slate-400" },
      ];
    } else if (horizon === "14D") {
      return [
        { label: "Rainfall 14D Sum", weight: 32, color: "bg-violet-500" },
        { label: "Consecutive Dry Days Streak", weight: 26, color: "bg-rose-500" },
        { label: "IOD Dipole Index", weight: 18, color: "bg-amber-500" },
        { label: "MJO Phase & Amplitude", weight: 12, color: "bg-teal-500" },
        { label: "Nino 3.4 SST Anomaly", weight: 8, color: "bg-indigo-400" },
        { label: "Seasonal Cosine Day-of-Year", weight: 4, color: "bg-slate-400" },
      ];
    } else if (horizon === "21D") {
      return [
        { label: "IOD Dipole Index", weight: 30, color: "bg-amber-500" },
        { label: "Rainfall 30D Sum", weight: 24, color: "bg-violet-500" },
        { label: "Consecutive Dry Days", weight: 20, color: "bg-rose-500" },
        { label: "Nino 3.4 SST Anomaly", weight: 14, color: "bg-indigo-400" },
        { label: "MJO Amplitude", weight: 8, color: "bg-teal-500" },
        { label: "Seasonal Cosine Day-of-Year", weight: 4, color: "bg-slate-400" },
      ];
    } else { // 30D
      return [
        { label: "IOD Dipole Index", weight: 34, color: "bg-amber-500" },
        { label: "Nino 3.4 SST Anomaly", weight: 28, color: "bg-violet-500" },
        { label: "Rainfall 30D Mean", weight: 18, color: "bg-rose-500" },
        { label: "MJO Phase & Amplitude", weight: 11, color: "bg-teal-500" },
        { label: "ONIE Index", weight: 5, color: "bg-indigo-400" },
        { label: "Seasonal Cosine Day-of-Year", weight: 4, color: "bg-slate-400" },
      ];
    }
  } else { // HEAVY RAIN
    if (horizon === "7D") {
      return [
        { label: "Rainfall 7D Max & Trend", weight: 42, color: "bg-amber-500" },
        { label: "MJO Amplitude (Phase 3/4)", weight: 22, color: "bg-teal-500" },
        { label: "Consecutive Rain Days", weight: 16, color: "bg-emerald-500" },
        { label: "Rainfall 3D Sum", weight: 10, color: "bg-violet-500" },
        { label: "IOD Dipole Index", weight: 6, color: "bg-rose-500" },
        { label: "Seasonal Cosine Day-of-Year", weight: 4, color: "bg-slate-400" },
      ];
    } else if (horizon === "14D") {
      return [
        { label: "Rainfall 14D Max & Sum", weight: 38, color: "bg-amber-500" },
        { label: "MJO Amplitude (Phase 3/4)", weight: 24, color: "bg-teal-500" },
        { label: "Rainfall Trend (7D vs Prev 7D)", weight: 16, color: "bg-violet-500" },
        { label: "IOD Dipole Index", weight: 11, color: "bg-rose-500" },
        { label: "SOI Anomaly", weight: 7, color: "bg-indigo-400" },
        { label: "Seasonal Cosine Day-of-Year", weight: 4, color: "bg-slate-400" },
      ];
    } else if (horizon === "21D") {
      return [
        { label: "MJO Amplitude (Phase 3/4)", weight: 32, color: "bg-teal-500" },
        { label: "Rainfall 30D Max", weight: 26, color: "bg-amber-500" },
        { label: "IOD Dipole Index", weight: 18, color: "bg-rose-500" },
        { label: "Nino 3.4 SST Anomaly", weight: 12, color: "bg-violet-500" },
        { label: "SOI Anomaly", weight: 8, color: "bg-indigo-400" },
        { label: "Seasonal Cosine Day-of-Year", weight: 4, color: "bg-slate-400" },
      ];
    } else { // 30D
      return [
        { label: "MJO Phase & Amplitude", weight: 30, color: "bg-teal-500" },
        { label: "IOD Dipole Index", weight: 26, color: "bg-rose-500" },
        { label: "Nino 3.4 SST Anomaly", weight: 22, color: "bg-violet-500" },
        { label: "Rainfall 30D Max", weight: 12, color: "bg-amber-500" },
        { label: "SOI Anomaly", weight: 6, color: "bg-indigo-400" },
        { label: "Seasonal Cosine Day-of-Year", weight: 4, color: "bg-slate-400" },
      ];
    }
  }
}

export default function ModelPage() {
  const { t } = useLanguage();
  
  // Interactive State
  const [horizon, setHorizon] = useState("14D");
  const [eventType, setEventType] = useState("BREAK SPELL");
  const [activeStage, setActiveStage] = useState(5); // Default Isotonic Stage 5

  const importances = getFeatureImportances(horizon, eventType);
  const stageInfo = STAGE_DETAILS[activeStage];

  return (
    <div className="flex flex-col gap-6 max-w-6xl mx-auto w-full pb-10">
      {/* Header */}
      <div className="flex justify-between items-start flex-wrap gap-4">
        <div>
          <div className="font-mono text-[11.5px] tracking-[.16em] text-teal-500 uppercase mb-1.5 flex items-center gap-2">
            <span className="w-1.5 h-1.5 rounded-full bg-teal-500 shadow-[0_0_10px_#0891b2] animate-pulse"></span>
            Predictive Core Intelligence
          </div>
          <h1 className="font-display font-semibold text-[27px] tracking-[-0.01em] text-text-hi uppercase">
            {t("model_page_title", "MODEL INTELLIGENCE DASHBOARD")}
          </h1>
          <p className="text-text-mid text-[14px]">
            {t("model_page_subtitle", "Hybrid climate-to-local prediction framework & Isotonic calibration engine")}
          </p>
        </div>

        <div className="bg-glass-fill border border-glass-borderSoft backdrop-blur-[20px] rounded-full py-2 px-4 text-[12.5px] font-mono text-text-hi flex items-center gap-2">
          <ShieldCheck size={14} className="text-teal-500" />
          <span>12 Official Phase 3B Frozen Models</span>
        </div>
      </div>

      {/* Interactive 6-Stage Pipeline Visualizer */}
      <div className="glass-panel p-6">
        <div className="flex justify-between items-center mb-5 flex-wrap gap-2">
          <h2 className="font-display font-semibold text-[16px] flex items-center gap-2 text-text-hi">
            <Layers size={17} className="text-violet-500" />
            {t("architecture_title", "Phase 3B Model Architecture Pipeline")}
          </h2>
          <span className="panel-label">Click stage to inspect data contract</span>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-3.5 items-stretch">
          <ArchitectureNode 
            step="1" 
            title="Macro Climate" 
            type="ENSO / IOD / MJO" 
            active={activeStage === 1}
            onClick={() => setActiveStage(1)}
          />
          <ArchitectureNode 
            step="2" 
            title="IMD & ERA5" 
            type="Rainfall Lags" 
            active={activeStage === 2}
            onClick={() => setActiveStage(2)}
          />
          <ArchitectureNode 
            step="3" 
            title="Feature Matrix" 
            type="30 Features &le; T" 
            active={activeStage === 3}
            onClick={() => setActiveStage(3)}
          />
          <ArchitectureNode 
            step="4" 
            title="XGBoost Core" 
            type="12 Classifiers" 
            active={activeStage === 4}
            onClick={() => setActiveStage(4)}
          />
          <ArchitectureNode 
            step="5" 
            title="Isotonic Calibrator" 
            type="ECE &lt; 0.04" 
            active={activeStage === 5}
            onClick={() => setActiveStage(5)}
          />
          <ArchitectureNode 
            step="6" 
            title="Advisory Engine" 
            type="Phase 6 Rules" 
            active={activeStage === 6}
            onClick={() => setActiveStage(6)}
          />
        </div>

        {/* Stage Details Inspector Box */}
        {stageInfo && (
          <div className="mt-5 p-4.5 rounded-xl bg-glass-fill2 border border-glass-borderSoft flex flex-col gap-2 font-sans animate-fadeIn">
            <div className="flex justify-between items-center flex-wrap gap-2">
              <span className="font-mono text-[11px] text-violet-500 font-bold uppercase tracking-[.06em]">
                STAGE {activeStage}: {stageInfo.title}
              </span>
              <span className="font-mono text-[10px] bg-violet-500/10 text-violet-600 px-2 py-0.5 rounded-md">
                {stageInfo.type}
              </span>
            </div>
            <p className="text-[13.5px] text-text-mid leading-relaxed">{stageInfo.desc}</p>
            <div className="flex flex-col md:flex-row justify-between gap-3 pt-2 text-[12px] border-t border-glass-borderSoft/60 font-mono">
              <div className="text-text-lo"><strong className="text-text-hi">Data Source:</strong> {stageInfo.inputs}</div>
              <div className="text-teal-600 font-semibold">{stageInfo.formula}</div>
            </div>
          </div>
        )}
      </div>

      {/* Target & Horizon Filter Controls */}
      <div className="flex justify-between items-center flex-wrap gap-4 glass-panel p-4">
        <div className="flex items-center gap-2">
          <Filter size={15} className="text-violet-500 shrink-0" />
          <span className="font-mono text-[11px] text-text-lo uppercase tracking-[.06em]">Select Target Model:</span>
        </div>

        <div className="flex gap-2 flex-wrap">
          {/* Horizon Selector */}
          <div className="flex gap-1 bg-glass-fill2 p-1 rounded-full border border-glass-borderSoft">
            {["7D", "14D", "21D", "30D"].map((h) => (
              <button
                key={h}
                onClick={() => setHorizon(h)}
                className={clsx(
                  "font-mono text-[10.5px] px-3 py-1 rounded-full cursor-pointer transition-all duration-200 transform hover:scale-105 active:scale-95 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-violet-500/50",
                  horizon === h ? "bg-violet-500 text-white font-semibold shadow-sm" : "text-text-mid hover:text-text-hi"
                )}
              >
                {h} Horizon
              </button>
            ))}
          </div>

          {/* Event Type Selector */}
          <div className="flex gap-1 bg-glass-fill2 p-1 rounded-full border border-glass-borderSoft">
            {["ONSET", "BREAK SPELL", "HEAVY RAIN"].map((e) => (
              <button
                key={e}
                onClick={() => setEventType(e)}
                className={clsx(
                  "font-mono text-[10.5px] px-3 py-1 rounded-full cursor-pointer transition-all duration-200 transform hover:scale-105 active:scale-95 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal-500/50",
                  eventType === e ? "bg-teal-500 text-white font-semibold shadow-sm" : "text-text-mid hover:text-text-hi"
                )}
              >
                {e === "ONSET" ? t("area_onset", "ONSET") : e === "BREAK SPELL" ? t("area_break", "BREAK SPELL") : t("metric_heavy_7d", "HEAVY RAIN")}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Main Grid: Feature Importances & Isotonic Calibration Diagram */}
      <div className="grid grid-cols-1 lg:grid-cols-[1.25fr_1fr] gap-6 items-stretch">
        
        {/* Feature Importance Bar List */}
        <div className="glass-panel p-5.5 flex flex-col gap-4">
          <div className="flex justify-between items-center">
            <h3 className="font-display font-semibold text-[15px] text-text-hi flex items-center gap-2">
              <BarChart2 size={16} className="text-violet-500" />
              {t("feature_contribution", "Feature Contribution & Importance")}
            </h3>
            <span className="font-mono text-[11px] text-teal-600 font-bold bg-teal-500/10 px-2.5 py-0.5 rounded-full animate-fadeIn" key={`${horizon}-${eventType}`}>
              {horizon} {eventType} Model
            </span>
          </div>

          <div className="flex flex-col gap-3.5 font-sans mt-2" key={`list-${horizon}-${eventType}`}>
            {importances.map((item, idx) => (
              <ImportanceBar key={idx} label={item.label} percentage={item.weight} color={item.color} />
            ))}
          </div>
        </div>

        {/* Isotonic Calibration & Reliability Curve */}
        <div className="glass-panel p-5.5 flex flex-col justify-between gap-4">
          <div>
            <div className="flex justify-between items-center mb-3">
              <h3 className="font-display font-semibold text-[15px] text-text-hi flex items-center gap-2">
                <Brain size={16} className="text-teal-500" />
                {t("calibration_title", "Isotonic Probability Calibration & Reliability")}
              </h3>
            </div>
            
            <p className="text-[12.5px] text-text-mid leading-relaxed mb-4 font-sans">
              Isotonic regression maps raw XGBoost outputs onto monotonic step functions fitted on 2024 validation data, ensuring calibrated probabilities match empirical event frequencies.
            </p>

            {/* SVG Reliability Diagram */}
            <div className="relative w-full h-[180px] bg-glass-fill2 rounded-xl border border-glass-borderSoft p-3 flex flex-col justify-between">
              <div className="font-mono text-[9.5px] text-text-lo flex justify-between">
                <span>Observed Frequency (y)</span>
                <span className="text-teal-600 font-bold">1-to-1 Calibration Diagonal</span>
              </div>

              <svg className="w-full h-[120px] overflow-visible" viewBox="0 0 200 100">
                {/* Grid Lines */}
                <line x1="0" y1="100" x2="200" y2="0" stroke="rgba(139,124,246,0.3)" strokeDasharray="3 3" strokeWidth="1.5" />
                <line x1="0" y1="100" x2="200" y2="100" stroke="rgba(0,0,0,0.1)" strokeWidth="1" />
                <line x1="0" y1="0" x2="0" y2="100" stroke="rgba(0,0,0,0.1)" strokeWidth="1" />
                
                {/* Calibrated Isotonic Curve */}
                <polyline
                  fill="none"
                  stroke="#10b981"
                  strokeWidth="2.5"
                  points="0,100 30,85 70,68 110,42 160,20 200,0"
                />
                
                {/* Calibration Points */}
                <circle cx="30" cy="85" r="3.5" fill="#10b981" />
                <circle cx="70" cy="68" r="3.5" fill="#10b981" />
                <circle cx="110" cy="42" r="3.5" fill="#10b981" />
                <circle cx="160" cy="20" r="3.5" fill="#10b981" />
              </svg>

              <div className="font-mono text-[9.5px] text-text-lo flex justify-between">
                <span>0.0 (Unlikely)</span>
                <span>Predicted Probability (x)</span>
                <span>1.0 (Certain)</span>
              </div>
            </div>
          </div>

          {/* Model Metrics Strip */}
          <div className="grid grid-cols-2 gap-3 pt-3 border-t border-glass-borderSoft font-mono">
            <div className="p-2.5 rounded-lg bg-glass-fill2 border border-glass-borderSoft flex flex-col gap-0.5">
              <span className="text-[9.5px] text-text-lo uppercase">{t("ece_score", "ECE Error")}</span>
              <span className="text-[15px] font-bold text-teal-600">0.032 <span className="text-[10px] font-normal text-text-mid">(&lt; 0.05 Target)</span></span>
            </div>
            <div className="p-2.5 rounded-lg bg-glass-fill2 border border-glass-borderSoft flex flex-col gap-0.5">
              <span className="text-[9.5px] text-text-lo uppercase">{t("brier_score", "Brier Score")}</span>
              <span className="text-[15px] font-bold text-violet-600">0.089 <span className="text-[10px] font-normal text-text-mid">(Optimal)</span></span>
            </div>
          </div>
        </div>

      </div>

      {/* Evaluation Protocol & Data Splits Summary */}
      <div className="glass-panel p-5 flex flex-col gap-3 font-sans">
        <span className="font-mono text-[10.5px] tracking-[.08em] text-teal-600 uppercase font-semibold">
          Chronological Evaluation Protocol
        </span>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-[13px]">
          <div className="p-3 rounded-xl bg-glass-fill2 border border-glass-borderSoft flex flex-col gap-1">
            <span className="font-mono text-[11px] text-violet-500 font-bold">TRAIN SET (2022–2023)</span>
            <span className="text-text-hi font-medium">6,570 Daily Records</span>
            <span className="text-text-mid text-[12px]">XGBoost gradient boosting decision tree training.</span>
          </div>
          <div className="p-3 rounded-xl bg-glass-fill2 border border-glass-borderSoft flex flex-col gap-1">
            <span className="font-mono text-[11px] text-teal-500 font-bold">VAL SET (2024)</span>
            <span className="text-text-hi font-medium">3,294 Daily Records</span>
            <span className="text-text-mid text-[12px]">Isotonic regression calibration & threshold tuning.</span>
          </div>
          <div className="p-3 rounded-xl bg-glass-fill2 border border-glass-borderSoft flex flex-col gap-1">
            <span className="font-mono text-[11px] text-rose-500 font-bold">TEST SET (2025)</span>
            <span className="text-text-hi font-medium">3,015 Daily Records</span>
            <span className="text-text-mid text-[12px]">Held-out final evaluation and validation audit.</span>
          </div>
        </div>
      </div>

    </div>
  );
}

function ArchitectureNode({ step, title, type, active, onClick }) {
  return (
    <button 
      onClick={onClick}
      className={clsx(
        "flex flex-col justify-between p-3.5 rounded-xl border transition-all duration-200 cursor-pointer text-left transform hover:scale-105 active:scale-95 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-violet-500/50 min-h-[105px]",
        active 
          ? "bg-gradient-to-br from-violet-500 to-violet-soft text-white border-transparent shadow-[0_4px_14px_rgba(139,124,246,0.3)]" 
          : "bg-glass-fill2 border-glass-borderSoft text-text-hi hover:bg-glass-fill"
      )}
    >
      <div>
        <span className={`font-mono text-[9px] px-1.5 py-0.5 rounded-md ${active ? "bg-white/20 text-white" : "bg-[rgba(139,124,246,0.18)] text-violet-500 font-semibold"}`}>
          STAGE {step}
        </span>
        <h4 className="font-display text-[12px] font-semibold leading-snug mt-1.5">{title}</h4>
      </div>
      <span className={`text-[9.5px] font-mono leading-none ${active ? "text-white/80" : "text-text-lo"}`}>{type}</span>
    </button>
  );
}

function ImportanceBar({ label, percentage, color }) {
  return (
    <div className="flex flex-col gap-1">
      <div className="flex justify-between font-mono text-[11px] text-text-mid">
        <span>{label}</span>
        <span className="font-semibold text-text-hi">{percentage}%</span>
      </div>
      <div className="h-2 rounded-full bg-black/5 overflow-hidden">
        <div className={`h-full rounded-full ${color} transition-all duration-500 ease-out`} style={{ width: `${percentage}%` }}></div>
      </div>
    </div>
  );
}
