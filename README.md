# Monsoon Event Forecasting & Agricultural Advisory System

[![SIH 2026](https://img.shields.io/badge/Hackathon-Smart_India_Hackathon_2026-blue.svg)](https://sih.gov.in)
[![Python](https://img.shields.io/badge/Backend-FastAPI_%2F_Python_3.12-green.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/Frontend-React_%2F_Tailwind_v4-cyan.svg)](https://react.dev)
[![XGBoost](https://img.shields.io/badge/ML-XGBoost_%2F_Isotonic_Calibration-orange.svg)](https://xgboost.readthedocs.io)

An end-to-end, sub-seasonal probabilistic forecasting platform and deterministic decision-support engine designed to assist Indian farmers, agronomists, and agricultural extension officers in managing monsoon climate risks (*Monsoon Onset, Break Spells, Heavy Rain Events*).

---

## 🌟 Key Capabilities

1. **Sub-Seasonal Probabilistic Event Forecasting**:
   - Predicts calibrated probabilities for **Monsoon Onset**, **Break Spells**, and **Heavy Rain Events** across four lead horizons: **7 Days, 14 Days, 21 Days, and 30 Days**.
   - Built on 30 validated meteorological features including short-term rainfall lags, streaks, seasonality, and global ocean-atmosphere indices (**ENSO / Nino 3.4, IOD, MJO Phase & Amplitude**).
   - Calibrated using **Isotonic Regression** on held-out validation data.

2. **Phase 6 Agricultural Advisory Engine**:
   - Translates probabilistic outputs into deterministic, crop- and stage-specific advisories (*Rice, Maize, Cotton, Soybean* across 6 growth stages).
   - Enforces a 5-tier priority hierarchy to provide 1 primary recommendation and up to 2 supporting actions.

3. **Dedicated False-Onset Risk Warning**:
   - Detects false-onset risks ($\text{Onset}_{14d} \ge 60\%$ AND $\text{Break}_{14d} \ge 50\%$), generating explicit warnings (`FALSE_ONSET_WARNING`) to prevent premature rain-dependent sowing.

4. **100% Location Honesty & Multi-Region Support**:
   - Supports location resolution across all 28 Indian States and top monitoring districts (*e.g., Meerut, Lucknow, Wayanad, Mumbai, Jaipur, Patna, Visakhapatnam*).
   - Explicitly returns location resolution metadata (`is_direct_match` boolean and `location_resolution_note` string) and displays indicator badges (`ℹ️ Regional Baseline`) on the frontend when non-covered states rely on regional model baselines.

5. **Full-Stack Web Dashboard**:
   - **FastAPI REST API**: Asynchronous backend serving live model inference.
   - **React Dashboard**: Modern, glassmorphism UI displaying live probability curves, advisories, risk badges, and location indicators.

---

## 🏗 System Architecture

```text
                               ┌─────────────────────────────────────────┐
                               │       React Dashboard (Vite Frontend)   │
                               └────────────────────┬────────────────────┘
                                                    │
                                                    ▼
                               ┌─────────────────────────────────────────┐
                               │        FastAPI Asynchronous Router      │
                               │   (/api/v1/forecast/predict & /live)    │
                               └────────────────────┬────────────────────┘
                                                    │
                                                    ▼
                               ┌─────────────────────────────────────────┐
                               │   Production Inference Pipeline         │
                               │   (backend/inference_pipeline.py)       │
                               └──────────┬───────────────────┬──────────┘
                                          │                   │
                                          ▼                   ▼
                     ┌──────────────────────────┐   ┌──────────────────────────┐
                     │ 12 Frozen XGBoost Models │   │ Phase 6 Advisory Engine  │
                     │  + Isotonic Calibrators  │   │   (backend/advisory/)    │
                     └──────────────────────────┘   └──────────────────────────┘
```

---

## 📁 Repository Structure

```text
.
├── backend/
│   ├── main.py                          # FastAPI main application server
│   ├── inference_pipeline.py            # End-to-end production inference pipeline
│   ├── test_inference_pipeline.py       # Standalone unit test suite
│   ├── advisory/                        # Phase 6 Agricultural Advisory Engine
│   │   ├── engine.py                    # Core deterministic decision engine
│   │   ├── rules.py                     # Configurable risk thresholds & false-onset rules
│   │   ├── crops.py                     # Crop catalog & stage sensitivity matrix
│   │   └── schemas.py                   # Dataclass input/output schemas
│   ├── app/                             # FastAPI application routers & database models
│   ├── models/
│   │   └── event_models/                # Official frozen Phase 3B models & calibrators
│   └── data/                            # Historical forecasting datasets & climate indices
├── frontend/
│   ├── src/                             # React application source code
│   │   ├── App.jsx                      # Main React layout & state manager
│   │   └── components/dashboard/        # Dashboard widgets (HeroStatus, ForecastOutlook, AdvisoryCard, KPIStrip)
│   ├── package.json                     # Frontend dependencies
│   └── vite.config.js                   # Vite configuration with API proxy
└── README.md                            # Project documentation
```

---

## 🚀 Quickstart & Local Execution

### Prerequisites
- **Python 3.10+** (Virtual environment recommended)
- **Node.js 18+** & **npm**

### Step 1: Clone the Repository
```bash
git clone https://github.com/PR-REDHAWK/SMART-INDIA-HACKATHON-2026.git
cd SMART-INDIA-HACKATHON-2026
```

### Step 2: Set Up & Launch FastAPI Backend
```bash
cd backend

# Create & activate virtual environment (Windows PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install backend dependencies
pip install -r requirements.txt

# Run backend unit tests
python test_inference_pipeline.py

# Launch FastAPI server
python -m uvicorn main:app --reload --port 8000
```
> Backend API running at `http://127.0.0.1:8000` | OpenAPI Docs at `http://127.0.0.1:8000/docs`

### Step 3: Set Up & Launch React Frontend
Open a new terminal:
```bash
cd frontend

# Install frontend dependencies
npm install

# Launch Vite development server
npm run dev
```
> Frontend Dashboard running at `http://localhost:5173`

---

## 📡 API Endpoint Reference

### `POST /api/v1/forecast/predict`
Accepts prediction parameters and executes full production inference pipeline.

**Request Payload**:
```json
{
  "state": "Uttar Pradesh",
  "prediction_date": "2024-06-15",
  "crop_name": "Rice",
  "growth_stage": "Sowing",
  "soil_moisture_pct": 25.0
}
```

**Response Payload**:
```json
{
  "status": "SUCCESS",
  "metadata": {
    "requested_location": "Uttar Pradesh",
    "resolved_state": "Uttar Pradesh",
    "is_direct_match": true,
    "location_resolution_note": "Direct validated Phase 3B model for Uttar Pradesh.",
    "prediction_date": "2024-06-15",
    "model_version": "Phase_3B_Official_Production",
    "advisory_engine_version": "Phase_6_Rule_Engine"
  },
  "probabilities": {
    "onset": { "7d": 6.6, "14d": 30.0, "21d": 41.2, "30d": 86.2 },
    "break_spell": { "7d": 95.5, "14d": 100.0, "21d": 81.9, "30d": 100.0 },
    "heavy_rain": { "7d": 0.0, "14d": 3.4, "21d": 0.7, "30d": 5.5 }
  },
  "advisory": {
    "risk_level": "VERY_HIGH",
    "event_type": "BREAK_SPELL",
    "horizon_days": 7,
    "probability": 95.5,
    "probability_trend": "STABLE",
    "false_onset_risk": false,
    "crop_name": "Rice",
    "growth_stage": "Sowing",
    "title": "🟠 High Dry-Spell Risk",
    "message": "A prolonged dry spell (break spell) is likely (95%) over the next 7 days.",
    "primary_action": "Delay rain-dependent Rice sowing if practical due to imminent dry spell.",
    "supporting_actions": [
      "Prepare supplemental irrigation facilities",
      "Keep nursery beds covered and hydrated"
    ],
    "reasoning": "Break Spell probability (95%) exceeded threshold (60%) at horizon 7D.",
    "advisory_code": "BREAK_SPELL_WARNING"
  }
}
```

---

## 🧪 Model Evaluation & Validation Protocol

The forecasting models were evaluated under strict chronological splits:
- **TRAIN**: `2022-01-01` to `2023-12-31` (6,570 records)
- **VALIDATION**: `2024-01-01` to `2024-12-31` (3,294 records) — Threshold tuning & Isotonic calibration
- **TEST**: `2025-01-01` to `2025-12-01` (3,015 records) — **Held-out final evaluation**

---

## ⚠️ Agronomic Disclaimer

> **Notice**: The rules in this MVP advisory engine represent deterministic engineering rules. They provide decision-support recommendations based on calibrated forecast probabilities and must be validated by local agricultural extension officers (e.g. Krishi Vigyan Kendra) before field deployment.

---

## 📜 License & Citation

Developed for the **Smart India Hackathon (SIH 2026)**. Built with open-source software under the MIT License.
