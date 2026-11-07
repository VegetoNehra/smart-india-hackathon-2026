import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

# Define Output File
OUTPUT_PDF = r"c:\Users\LENOVO\OneDrive\SMART INDIA HACKATHON\Monsoon_Event_Forecasting_System_Comprehensive_Report.pdf"
ASSET_DIR = r"c:\Users\LENOVO\OneDrive\SMART INDIA HACKATHON\report_assets"

# -------------------------------------------------------------
# Numbered Canvas for Page X of Y & Running Header
# -------------------------------------------------------------
class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        if self._pageNumber == 1:
            # Suppress header and footer on cover page
            return

        self.saveState()
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor("#475569"))

        # Running Header
        self.drawString(54, 11 * 72 - 36, "MONSOON EVENT FORECASTING & AGRICULTURAL ADVISORY SYSTEM")
        self.drawRightString(8.5 * 72 - 54, 11 * 72 - 36, "SIH 2026 TECHNICAL & NON-TECHNICAL REPORT")
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(54, 11 * 72 - 42, 8.5 * 72 - 54, 11 * 72 - 42)

        # Running Footer
        self.setFont("Helvetica", 8)
        self.drawString(54, 36, "CONFIDENTIAL & PROPRIETARY — SMART INDIA HACKATHON 2026")
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(8.5 * 72 - 54, 36, page_text)
        self.line(54, 46, 8.5 * 72 - 54, 46)

        self.restoreState()


def build_pdf():
    doc = SimpleDocTemplate(
        OUTPUT_PDF,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    # Custom Color Palette
    c_primary = colors.HexColor("#0F172A")    # Dark Slate Navy
    c_secondary = colors.HexColor("#1E293B")  # Slate Gray
    c_accent = colors.HexColor("#0284C7")     # Ocean Cyan
    c_success = colors.HexColor("#059669")    # Emerald Green
    c_warning = colors.HexColor("#D97706")    # Amber
    c_dark = colors.HexColor("#334155")       # Body Text

    # Custom Typography Styles
    style_cover_title = ParagraphStyle(
        'CoverTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=30,
        textColor=c_primary,
        alignment=0,
        spaceAfter=12
    )

    style_cover_subtitle = ParagraphStyle(
        'CoverSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=16,
        textColor=c_accent,
        alignment=0,
        spaceAfter=24
    )

    style_h1 = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=16,
        leading=20,
        textColor=c_primary,
        spaceBefore=16,
        spaceAfter=10,
        keepWithNext=True
    )

    style_h2 = ParagraphStyle(
        'Heading2_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=c_accent,
        spaceBefore=12,
        spaceAfter=6,
        keepWithNext=True
    )

    style_body = ParagraphStyle(
        'Body_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=c_dark,
        spaceAfter=8
    )

    style_bullet = ParagraphStyle(
        'Bullet_Custom',
        parent=style_body,
        leftIndent=15,
        bulletIndent=5,
        spaceAfter=4
    )

    style_callout = ParagraphStyle(
        'CalloutText',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#1E293B")
    )

    style_table_header = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=colors.white,
        alignment=1
    )

    style_table_cell = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=10.5,
        textColor=c_dark,
        alignment=0
    )

    style_table_cell_center = ParagraphStyle(
        'TableCellCenter',
        parent=style_table_cell,
        alignment=1
    )

    story = []

    # =============================================================
    # COVER PAGE
    # =============================================================
    story.append(Spacer(1, 20))
    story.append(Paragraph("SMART INDIA HACKATHON 2026 — TECHNICAL SPECIFICATION", ParagraphStyle('SubHeaderBadge', fontName='Helvetica-Bold', fontSize=10, leading=12, textColor=c_accent, spaceAfter=8)))
    story.append(Paragraph("Monsoon Event Forecasting & Agricultural Advisory System", style_cover_title))
    story.append(Paragraph("An End-to-End Sub-Seasonal Probabilistic Forecasting Platform & Phase 6 Agronomic Decision Support Engine", style_cover_subtitle))
    story.append(HRFlowable(width="100%", thickness=2, color=c_accent, spaceAfter=20))

    # Cover Meta Box
    meta_data = [
        [Paragraph("<b>Project Platform:</b>", style_body), Paragraph("Smart India Hackathon 2026 (SIH 2026)", style_body)],
        [Paragraph("<b>Backend Engine:</b>", style_body), Paragraph("FastAPI / Python 3.12 / Async Uvicorn", style_body)],
        [Paragraph("<b>ML Framework:</b>", style_body), Paragraph("12 Frozen XGBoost Models + Isotonic Calibrators", style_body)],
        [Paragraph("<b>Decision Support:</b>", style_body), Paragraph("Phase 6 Agronomic Priority Hierarchy Engine", style_body)],
        [Paragraph("<b>Frontend UI:</b>", style_body), Paragraph("React Dashboard / Tailwind v4 Glassmorphism UI", style_body)],
        [Paragraph("<b>Target Domain:</b>", style_body), Paragraph("Sub-Seasonal Risk Management (Onset, Break, Heavy Rain)", style_body)],
        [Paragraph("<b>Location Honesty:</b>", style_body), Paragraph("28 Indian States & Top Monitoring Districts Disclosed", style_body)],
    ]
    t_meta = Table(meta_data, colWidths=[140, 340])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#E2E8F0")),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#F1F5F9")),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 25))

    # Executive Overview Callout Box on Cover Page
    exec_summary_text = (
        "<b>Executive Summary:</b> Agriculture in India supports over 50% of the national workforce and is heavily reliant on the "
        "Southwest Monsoon. However, sub-seasonal weather variability—such as delayed monsoon onset, sudden false-onset rain spells, "
        "extended dry break spells, and torrential heavy rain events—creates catastrophic risk for rainfed farming systems. "
        "This project delivers an operational, end-to-end forecasting and decision-support platform that generates calibrated 7-, 14-, 21-, "
        "and 30-day probabilistic risk profiles across India. By combining 30 meteorological features, global ocean-atmosphere indices "
        "(ENSO, IOD, MJO), Isotonic Regression calibration, and a 5-tier agronomic rule engine, the platform translates raw probabilities "
        "into clear, stage-specific agricultural advisories for key crops (Rice, Maize, Cotton, Soybean)."
    )
    t_exec = Table([[Paragraph(exec_summary_text, style_callout)]], colWidths=[480])
    t_exec.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#E0F2FE")),
        ('BOX', (0, 0), (-1, -1), 1.5, colors.HexColor("#0284C7")),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
    ]))
    story.append(t_exec)

    story.append(PageBreak())

    # =============================================================
    # CHAPTER 1: NON-TECHNICAL OVERVIEW & PROJECT STRATEGY
    # =============================================================
    story.append(Paragraph("1. Non-Technical Overview & Project Strategy", style_h1))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceAfter=10))

    story.append(Paragraph("1.1 The Agricultural Problem Statement in India", style_h2))
    story.append(Paragraph(
        "Over 60% of cultivated land in India relies entirely on rainfall. Smallholder farmers operate under narrow profit margins "
        "and cannot afford crop failure resulting from mis-timed sowing or unmitigated weather stress. Three specific monsoon risks drive the majority of losses:",
        style_body
    ))
    story.append(Paragraph("• <b>False Onset of Monsoon:</b> Initial isolated rain triggers early sowing, followed immediately by a 2-3 week dry spell. Seeds desiccate in dry soil, causing 100% crop failure and requiring costly re-sowing.", style_bullet))
    story.append(Paragraph("• <b>Mid-Season Break Spells:</b> Prolonged dry intervals during vegetative or flowering stages lead to irreversible moisture stress, reducing final yields by 30-50%.", style_bullet))
    story.append(Paragraph("• <b>Heavy Rainfall & Extreme Events:</b> Intense precipitation causes waterlogging, soil nutrient leaching, and root asphyxiation during early seedling stages, or physical lodging during harvest.", style_bullet))

    story.append(Paragraph("1.2 The System Solution & Core Value Proposition", style_h2))
    story.append(Paragraph(
        "The Monsoon Event Forecasting & Advisory System bridges the critical gap between raw meteorological ensemble data and practical on-farm decision making. "
        "Rather than presenting raw, uncalibrated weather outputs, the platform provides:",
        style_body
    ))
    story.append(Paragraph("1. <b>Multi-Horizon Probabilistic Guidance:</b> Quantifies probability curves for Onset, Break Spells, and Heavy Rain at 7, 14, 21, and 30-day lead times.", style_bullet))
    story.append(Paragraph("2. <b>False-Onset Warning Protection:</b> Explicitly cross-analyzes Onset and Break Spell probabilities to detect high false-onset risk, advising farmers to delay rain-dependent sowing.", style_bullet))
    story.append(Paragraph("3. <b>Crop- and Stage-Specific Advisories:</b> Synthesizes probabilistic risk into 1 primary recommendation and up to 2 supporting actions tailored to Rice, Maize, Cotton, and Soybean across 6 growth stages.", style_bullet))
    story.append(Paragraph("4. <b>100% Location Honesty & Transparency:</b> Fully discloses whether a location uses a direct validated regional model or a regional baseline model, avoiding deceptive accuracy claims.", style_bullet))

    story.append(Paragraph("1.3 Stakeholders & Use Cases", style_h2))
    story.append(Paragraph(
        "The platform serves a wide agricultural ecosystem:",
        style_body
    ))
    story.append(Paragraph("• <b>Smallholder Farmers:</b> Receive actionable, localized guidance via web dashboard, SMS, or extension alerts to optimize sowing dates, irrigation, and fertilizer timing.", style_bullet))
    story.append(Paragraph("• <b>Agricultural Extension Officers (Krishi Vigyan Kendra - KVK):</b> Utilize the decision-support engine to issue validated district-level advisories and coordinate emergency irrigation resources.", style_bullet))
    story.append(Paragraph("• <b>Agronomists & Policy Makers:</b> Monitor regional drought/flood vulnerability trajectories to deploy contingency seed stocks and disaster relief reserves.", style_bullet))

    story.append(Spacer(1, 10))

    # KPI Summary Cards Table
    kpi_data = [
        [
            Paragraph("<b>12</b><br/><font size=7.5 color='#475569'>Frozen ML Models</font>", style_table_cell_center),
            Paragraph("<b>30</b><br/><font size=7.5 color='#475569'>Climate Variables</font>", style_table_cell_center),
            Paragraph("<b>4 Lead Horizons</b><br/><font size=7.5 color='#475569'>7D, 14D, 21D, 30D</font>", style_table_cell_center),
            Paragraph("<b>28 States</b><br/><font size=7.5 color='#475569'>Full India Coverage</font>", style_table_cell_center)
        ]
    ]
    t_kpi = Table(kpi_data, colWidths=[120, 120, 120, 120])
    t_kpi.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#CBD5E1")),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(t_kpi)

    story.append(PageBreak())

    # =============================================================
    # CHAPTER 2: SYSTEM ARCHITECTURE & TECHNICAL INFRASTRUCTURE
    # =============================================================
    story.append(Paragraph("2. System Architecture & Technical Infrastructure", style_h1))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceAfter=10))

    story.append(Paragraph("2.1 End-to-End Technical Stack", style_h2))
    story.append(Paragraph(
        "The application follows a decoupled, asynchronous micro-architecture engineered for high reliability, fast inference latency (<100ms), and easy scalability:",
        style_body
    ))

    # Architecture Image
    arch_img_path = os.path.join(ASSET_DIR, "chart_architecture.png")
    if os.path.exists(arch_img_path):
        story.append(Image(arch_img_path, width=460, height=230))
        story.append(Spacer(1, 10))

    story.append(Paragraph("2.2 Component Breakdown", style_h2))
    story.append(Paragraph("• <b>FastAPI Backend Application (`backend/main.py`):</b> Serves non-blocking REST API endpoints using Uvicorn. Exposes `/api/v1/forecast/predict` for live inference and `/health` for system status monitoring.", style_bullet))
    story.append(Paragraph("• <b>Production Inference Pipeline (`backend/inference_pipeline.py`):</b> Loads official Phase 3B frozen model artifacts and Isotonic calibrators. Pre-processes feature vectors strictly $\\le T$ to prevent temporal data leakage.", style_bullet))
    story.append(Paragraph("• <b>Phase 6 Agricultural Advisory Engine (`backend/advisory/`):</b> A deterministic rule engine that evaluates calibrated event probabilities against crop-specific vulnerability thresholds and soil moisture conditions.", style_bullet))
    story.append(Paragraph("• <b>React + Vite Dashboard (`frontend/src/`):</b> Modern glassmorphism UI built with React, Vite, and Tailwind CSS v4. Features interactive probability curves, risk badges, priority cards, and regional model baseline disclosures.", style_bullet))

    story.append(Paragraph("2.3 Location Resolution & 100% Location Honesty Protocol", style_h2))
    story.append(Paragraph(
        "A cornerstone design principle of this platform is <b>100% Location Honesty</b>. Weather models trained on specific geographical regions cannot automatically guarantee equal accuracy in unmonitored sub-regions. "
        "The system implements an explicit resolution engine (`resolve_state_name`):",
        style_body
    ))
    story.append(Paragraph("• <b>9 Direct Validated Dataset States:</b> <i>Assam, Gujarat, Karnataka, Kerala, Maharashtra, Punjab, Rajasthan, Uttar Pradesh, West Bengal</i> have direct daily historical training grids.", style_bullet))
    story.append(Paragraph("• <b>Key District Mapping:</b> 50+ major agricultural districts (e.g., <i>Meerut, Lucknow, Wayanad, Mumbai, Jaipur, Patna, Visakhapatnam</i>) are mapped directly to their parent validated states.", style_bullet))
    story.append(Paragraph("• <b>Regional Fallback Disclosures:</b> Non-covered states return regional model baselines with explicit metadata (`is_direct_match=False` and `location_resolution_note`). The frontend renders an indicator badge (`ℹ️ Regional Baseline`) so users are fully informed.", style_bullet))

    story.append(PageBreak())

    # =============================================================
    # CHAPTER 3: DATA ENGINEERING & FEATURE PIPELINE
    # =============================================================
    story.append(Paragraph("3. Data Engineering & Feature Pipeline", style_h1))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceAfter=10))

    story.append(Paragraph("3.1 Input Datasets & Climate Teleconnections", style_h2))
    story.append(Paragraph(
        "Sub-seasonal forecasting requires integrating localized short-term precipitation dynamics with large-scale ocean-atmosphere teleconnections. "
        "The dataset incorporates high-resolution observational grid data alongside global climate indices spanning 2022 to 2025:",
        style_body
    ))
    story.append(Paragraph("• <b>IMD High-Resolution Grid Rainfall ($0.25^\\circ \\times 0.25^\\circ$):</b> Daily gridded rainfall binary data across Indian landmass.", style_bullet))
    story.append(Paragraph("• <b>El Niño-Southern Oscillation (ENSO):</b> Incorporates Nino 3.4 SST Anomaly, Southern Oscillation Index (SOI), Oceanic Niño Index (ONI), and Relative ONI (RONI).", style_bullet))
    story.append(Paragraph("• <b>Indian Ocean Dipole (IOD):</b> Tracks the IOD Index to capture sea-surface temperature anomalies in the Indian Ocean.", style_bullet))
    story.append(Paragraph("• <b>Madden-Julian Oscillation (MJO):</b> Includes RMM1, RMM2, Amplitude, and Phase to capture intraseasonal tropical atmospheric variability.", style_bullet))

    story.append(Paragraph("3.2 The 30 Official Feature Catalog", style_h2))

    # Feature Catalog Table
    feat_headers = [Paragraph("Category", style_table_header), Paragraph("Feature Names", style_table_header), Paragraph("Agronomic & Physical Rationale", style_table_header)]
    feat_rows = [
        [
            Paragraph("<b>Rainfall Lags & Sums</b>", style_table_cell),
            Paragraph("`rainfall_today`, `3d_sum`, `7d_sum`, `14d_sum`, `30d_sum`", style_table_cell),
            Paragraph("Captures short-to-medium antecedent soil moisture accumulation.", style_table_cell)
        ],
        [
            Paragraph("<b>Rainfall Means & Maxes</b>", style_table_cell),
            Paragraph("`3d_mean`, `7d_mean`, `14d_mean`, `30d_mean`, `7d_max`, `14d_max`, `30d_max`", style_table_cell),
            Paragraph("Measures average rain intensity and extreme single-day rainfall spikes.", style_table_cell)
        ],
        [
            Paragraph("<b>Streaks & Trends</b>", style_table_cell),
            Paragraph("`consecutive_dry_days`, `consecutive_rain_days`, `7d_vs_prev_7d`, `14d_vs_prev_14d`, `rainfall_trend`", style_table_cell),
            Paragraph("Identifies onset momentum, spell breaks, and rapid drying trends.", style_table_cell)
        ],
        [
            Paragraph("<b>Seasonality</b>", style_table_cell),
            Paragraph("`month`, `doy` (Day of Year), `sin_day_of_year`, `cos_day_of_year`", style_table_cell),
            Paragraph("Encodes annual solar cycle and seasonal climatological baseline.", style_table_cell)
        ],
        [
            Paragraph("<b>ENSO / IOD Indices</b>", style_table_cell),
            Paragraph("`Nino 3.4 SST Anomaly`, `SOI`, `ONI`, `RONI`, `IOD_Index`", style_table_cell),
            Paragraph("Models large-scale Pacific and Indian Ocean warming/cooling phases.", style_table_cell)
        ],
        [
            Paragraph("<b>MJO Indices</b>", style_table_cell),
            Paragraph("`RMM1`, `RMM2`, `amplitude`, `phase`", style_table_cell),
            Paragraph("Captures eastward propagating convective cloud clusters driving break/active spells.", style_table_cell)
        ]
    ]

    t_feat = Table([feat_headers] + feat_rows, colWidths=[110, 170, 200])
    t_feat.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_primary),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t_feat)
    story.append(Spacer(1, 12))

    story.append(Paragraph("3.3 Feature Importance Analysis", style_h2))
    story.append(Paragraph(
        "Empirical feature importance extraction across all 12 models confirms that cyclical day-of-year features (`cos_day_of_year`, `doy`), "
        "medium-term rainfall sums (`rainfall_14d_sum`), and intraseasonal teleconnections (`IOD_Index`, MJO Phase) dominate model predictions:",
        style_body
    ))

    feat_img_path = os.path.join(ASSET_DIR, "chart_feature_importance.png")
    if os.path.exists(feat_img_path):
        story.append(Image(feat_img_path, width=440, height=220))
        story.append(Spacer(1, 10))

    story.append(PageBreak())

    # =============================================================
    # CHAPTER 4: MACHINE LEARNING MODELING & ISOTONIC CALIBRATION
    # =============================================================
    story.append(Paragraph("4. Machine Learning Modeling & Calibration", style_h1))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceAfter=10))

    story.append(Paragraph("4.1 Modeling Architecture & Training Protocol", style_h2))
    story.append(Paragraph(
        "The system trains <b>12 individual XGBoost binary classifiers</b> covering 3 target event types across 4 lead horizons (7D, 14D, 21D, 30D). "
        "Strict chronological data partitioning was enforced to replicate operational deployment:",
        style_body
    ))
    story.append(Paragraph("• <b>TRAIN SET:</b> `2022-01-01` to `2023-12-31` (6,570 records) — Model parameter optimization.", style_bullet))
    story.append(Paragraph("• <b>VALIDATION SET:</b> `2024-01-01` to `2024-12-31` (3,294 records) — Optimal probability threshold selection & Isotonic Regression fitting.", style_bullet))
    story.append(Paragraph("• <b>HELD-OUT TEST SET:</b> `2025-01-01` to `2025-12-01` (3,015 records) — Out-of-sample final evaluation.", style_bullet))

    story.append(Paragraph("4.2 Class Imbalance & Isotonic Probability Calibration", style_h2))
    story.append(Paragraph(
        "Extreme event targets (such as Onset 7D or Heavy Rain 7D) exhibit severe class imbalance (positive prevalence <2%). "
        "While rebalancing via `scale_pos_weight` (up to 51.14x) forces the trees to learn rare positive events, it heavily distorts raw output probabilities, causing extreme overconfidence. "
        "To restore true empirical reliability, <b>Isotonic Regression calibrators</b> were fitted on the held-out validation set. "
        "Post-hoc calibration dramatically reduced Brier Score errors across all models:",
        style_body
    ))

    calib_img_path = os.path.join(ASSET_DIR, "chart_brier_calibration.png")
    if os.path.exists(calib_img_path):
        story.append(Image(calib_img_path, width=440, height=220))
        story.append(Spacer(1, 10))

    story.append(Paragraph("4.3 Comprehensive Held-Out Test Evaluation Benchmarks", style_h2))
    story.append(Paragraph("Table 4.1 details final out-of-sample evaluation metrics across all 12 frozen production models on the 2025 held-out dataset:", style_body))

    # Complete 12 Model Metrics Table
    m_headers = [
        Paragraph("Target Model", style_table_header),
        Paragraph("Pos Weight", style_table_header),
        Paragraph("Optimal Thresh", style_table_header),
        Paragraph("Raw ROC-AUC", style_table_header),
        Paragraph("Calib ROC-AUC", style_table_header),
        Paragraph("Raw Brier", style_table_header),
        Paragraph("Calib Brier", style_table_header),
        Paragraph("F1-Score", style_table_header)
    ]

    m_rows = [
        [Paragraph("<b>Onset 7D</b>", style_table_cell), Paragraph("51.14", style_table_cell_center), Paragraph("0.08", style_table_cell_center), Paragraph("0.954", style_table_cell_center), Paragraph("0.935", style_table_cell_center), Paragraph("0.0405", style_table_cell_center), Paragraph("<b>0.0180</b>", style_table_cell_center), Paragraph("0.224", style_table_cell_center)],
        [Paragraph("<b>Onset 14D</b>", style_table_cell), Paragraph("25.07", style_table_cell_center), Paragraph("0.22", style_table_cell_center), Paragraph("0.955", style_table_cell_center), Paragraph("0.957", style_table_cell_center), Paragraph("0.0632", style_table_cell_center), Paragraph("<b>0.0302</b>", style_table_cell_center), Paragraph("0.461", style_table_cell_center)],
        [Paragraph("<b>Onset 21D</b>", style_table_cell), Paragraph("16.38", style_table_cell_center), Paragraph("0.26", style_table_cell_center), Paragraph("0.960", style_table_cell_center), Paragraph("0.958", style_table_cell_center), Paragraph("0.0708", style_table_cell_center), Paragraph("<b>0.0381</b>", style_table_cell_center), Paragraph("0.546", style_table_cell_center)],
        [Paragraph("<b>Onset 30D</b>", style_table_cell), Paragraph("11.17", style_table_cell_center), Paragraph("0.33", style_table_cell_center), Paragraph("0.970", style_table_cell_center), Paragraph("0.969", style_table_cell_center), Paragraph("0.0669", style_table_cell_center), Paragraph("<b>0.0431</b>", style_table_cell_center), Paragraph("0.485", style_table_cell_center)],
        [Paragraph("<b>Break 7D</b>", style_table_cell), Paragraph("3.58", style_table_cell_center), Paragraph("0.34", style_table_cell_center), Paragraph("0.936", style_table_cell_center), Paragraph("0.931", style_table_cell_center), Paragraph("0.0965", style_table_cell_center), Paragraph("<b>0.0863</b>", style_table_cell_center), Paragraph("0.741", style_table_cell_center)],
        [Paragraph("<b>Break 14D</b>", style_table_cell), Paragraph("2.57", style_table_cell_center), Paragraph("0.29", style_table_cell_center), Paragraph("0.942", style_table_cell_center), Paragraph("0.939", style_table_cell_center), Paragraph("0.0798", style_table_cell_center), Paragraph("<b>0.0743</b>", style_table_cell_center), Paragraph("0.857", style_table_cell_center)],
        [Paragraph("<b>Break 21D</b>", style_table_cell), Paragraph("2.08", style_table_cell_center), Paragraph("0.44", style_table_cell_center), Paragraph("0.954", style_table_cell_center), Paragraph("0.950", style_table_cell_center), Paragraph("0.0644", style_table_cell_center), Paragraph("<b>0.0609</b>", style_table_cell_center), Paragraph("0.900", style_table_cell_center)],
        [Paragraph("<b>Break 30D</b>", style_table_cell), Paragraph("1.77", style_table_cell_center), Paragraph("0.46", style_table_cell_center), Paragraph("0.962", style_table_cell_center), Paragraph("0.964", style_table_cell_center), Paragraph("0.0500", style_table_cell_center), Paragraph("<b>0.0484</b>", style_table_cell_center), Paragraph("<b>0.930</b>", style_table_cell_center)],
        [Paragraph("<b>Heavy Rain 7D</b>", style_table_cell), Paragraph("46.96", style_table_cell_center), Paragraph("0.04", style_table_cell_center), Paragraph("0.710", style_table_cell_center), Paragraph("0.706", style_table_cell_center), Paragraph("0.0822", style_table_cell_center), Paragraph("<b>0.0336</b>", style_table_cell_center), Paragraph("0.108", style_table_cell_center)],
        [Paragraph("<b>Heavy Rain 14D</b>", style_table_cell), Paragraph("26.15", style_table_cell_center), Paragraph("0.11", style_table_cell_center), Paragraph("0.712", style_table_cell_center), Paragraph("0.704", style_table_cell_center), Paragraph("0.1063", style_table_cell_center), Paragraph("<b>0.0602</b>", style_table_cell_center), Paragraph("0.176", style_table_cell_center)],
        [Paragraph("<b>Heavy Rain 21D</b>", style_table_cell), Paragraph("18.32", style_table_cell_center), Paragraph("0.15", style_table_cell_center), Paragraph("0.701", style_table_cell_center), Paragraph("0.697", style_table_cell_center), Paragraph("0.1302", style_table_cell_center), Paragraph("<b>0.0854</b>", style_table_cell_center), Paragraph("0.212", style_table_cell_center)],
        [Paragraph("<b>Heavy Rain 30D</b>", style_table_cell), Paragraph("13.28", style_table_cell_center), Paragraph("0.14", style_table_cell_center), Paragraph("0.709", style_table_cell_center), Paragraph("0.702", style_table_cell_center), Paragraph("0.1345", style_table_cell_center), Paragraph("<b>0.0886</b>", style_table_cell_center), Paragraph("0.231", style_table_cell_center)],
    ]

    t_metrics = Table([m_headers] + m_rows, colWidths=[75, 55, 55, 55, 60, 55, 60, 50])
    t_metrics.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_primary),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t_metrics)
    story.append(Spacer(1, 10))

    # ROC AUC Chart
    roc_img_path = os.path.join(ASSET_DIR, "chart_roc_auc.png")
    if os.path.exists(roc_img_path):
        story.append(Image(roc_img_path, width=440, height=220))

    story.append(PageBreak())

    # =============================================================
    # CHAPTER 5: PHASE 6 AGRICULTURAL ADVISORY ENGINE
    # =============================================================
    story.append(Paragraph("5. Phase 6 Agricultural Advisory Engine", style_h1))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceAfter=10))

    story.append(Paragraph("5.1 Deterministic Priority Hierarchy", style_h2))
    story.append(Paragraph(
        "To eliminate conflicting operational advice, the Phase 6 Advisory Engine enforces a strict 5-tier priority hierarchy. "
        "The engine evaluates calibrated probabilities starting from Priority 1 and outputs exactly 1 primary recommendation and up to 2 supporting actions:",
        style_body
    ))

    rule_img_path = os.path.join(ASSET_DIR, "chart_rule_hierarchy.png")
    if os.path.exists(rule_img_path):
        story.append(Image(rule_img_path, width=450, height=225))
        story.append(Spacer(1, 10))

    story.append(Paragraph("5.2 Priority Rules & Trigger Conditions", style_h2))
    story.append(Paragraph("• <b>Priority 1 — False-Onset Risk Warning (`FALSE_ONSET_WARNING`):</b> Triggers when $\\text{Onset}_{14d} \\ge 60\\%$ AND $\\text{Break}_{14d} \\ge 50\\%$. Advises farmers to delay rain-dependent sowing to prevent seed desiccation from imminent post-rain dry spells.", style_bullet))
    story.append(Paragraph("• <b>Priority 2 — Heavy Rain Threat (`HEAVY_RAIN_WARNING`):</b> Triggers when $\\text{HeavyRain}_{max} \\ge 60\\%$. Directs drainage clearing and harvest protection. Integrates soil moisture: if VWC $\\ge 70\\%$, halts field irrigation completely.", style_bullet))
    story.append(Paragraph("• <b>Priority 3 — Break Spell Warning (`BREAK_SPELL_WARNING`):</b> Triggers when $\\text{Break}_{max} \\ge 60\\%$. Recommends supplemental irrigation preparation and organic mulching to conserve root-zone moisture.", style_bullet))
    story.append(Paragraph("• <b>Priority 4 — Favorable Monsoon Onset (`ONSET_ALERT`):</b> Triggers when $\\text{Onset}_{max} \\ge 60\\%$. Recommends seed bed preparation and land clearing for upcoming sowing.", style_bullet))
    story.append(Paragraph("• <b>Priority 5 — Normal Seasonal Operations (`NORMAL_CONDITIONS`):</b> Triggers when all probabilities remain $<60\\%$. Directs routine crop management and daily monitoring.", style_bullet))

    story.append(Paragraph("5.3 Crop Profile Catalog & Dynamic Growth Stage Sensitivity", style_h2))
    story.append(Paragraph(
        "The advisory engine incorporates specific agronomic sensitivity profiles across 50+ supported crops spanning 7 major agricultural categories "
        "(<i>Cereals, Pulses, Oilseeds, Fiber, Horticulture, Sugarcane, Coarse Grains</i>) and 6 distinct growth stages "
        "(<i>Sowing, Germination / Establishment, Vegetative, Flowering, Grain/Fruit Development, Harvest</i>):",
        style_body
    ))

    # Chart 6 Image
    coverage_img_path = os.path.join(ASSET_DIR, "chart_crop_stage_coverage.png")
    if os.path.exists(coverage_img_path):
        story.append(Image(coverage_img_path, width=460, height=210))
        story.append(Spacer(1, 10))

    # Crop Profiles Table
    crop_headers = [Paragraph("Crop Category", style_table_header), Paragraph("Water Demand", style_table_header), Paragraph("Critical Growth Stage Sensitivity", style_table_header), Paragraph("Agronomic Action Highlights", style_table_header)]
    crop_rows = [
        [Paragraph("<b>Rice / Paddy</b>", style_table_cell), Paragraph("Very High", style_table_cell_center), Paragraph("Sowing, Panicle / Flowering", style_table_cell), Paragraph("Maintain 3-5 cm standing water layer during flowering; execute AWD if dry.", style_table_cell)],
        [Paragraph("<b>Wheat & Barley</b>", style_table_cell), Paragraph("Moderate", style_table_cell_center), Paragraph("Pre-Sowing (Palewa), Booting/Flowering", style_table_cell), Paragraph("Ensure pre-sowing irrigation; light frequent irrigation during grain filling.", style_table_cell)],
        [Paragraph("<b>Cotton & Fiber</b>", style_table_cell), Paragraph("Moderate", style_table_cell_center), Paragraph("Sowing, Flowering / Boll Formation", style_table_cell), Paragraph("Micro-irrigation during boll formation; clear furrows for >48h rain.", style_table_cell)],
        [Paragraph("<b>Pulses (Gram, Tur)</b>", style_table_cell), Paragraph("Low-Mod", style_table_cell_center), Paragraph("Germination, Flowering", style_table_cell), Paragraph("Prevent flower drop under dry spell; clear drainage to avoid wilt/rot.", style_table_cell)],
        [Paragraph("<b>Oilseeds (Soybean)</b>", style_table_cell), Paragraph("Moderate", style_table_cell_center), Paragraph("Sowing, Pegging / Pod Setting", style_table_cell), Paragraph("Rhizobium seed treatment; protective irrigation during pod setting.", style_table_cell)],
        [Paragraph("<b>Horticulture</b>", style_table_cell), Paragraph("High", style_table_cell_center), Paragraph("Planting, Tuber / Fruit Dev", style_table_cell), Paragraph("Raised bed planting; immediate drainage to prevent seed tuber rot.", style_table_cell)],
    ]

    t_crop = Table([crop_headers] + crop_rows, colWidths=[90, 65, 145, 180])
    t_crop.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_primary),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(t_crop)

    story.append(PageBreak())

    # =============================================================
    # CHAPTER 6: API REFERENCE & REQUEST/RESPONSE SPECIFICATIONS
    # =============================================================
    story.append(Paragraph("6. REST API Reference & Data Schemas", style_h1))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceAfter=10))

    story.append(Paragraph("6.1 Production Prediction Endpoint (`POST /api/v1/forecast/predict`)", style_h2))
    story.append(Paragraph("Executes end-to-end model inference, location resolution, and Phase 6 advisory generation.", style_body))

    # Request Schema Table
    req_headers = [Paragraph("Field Name", style_table_header), Paragraph("Type", style_table_header), Paragraph("Required", style_table_header), Paragraph("Description & Sample Values", style_table_header)]
    req_rows = [
        [Paragraph("`state`", style_table_cell), Paragraph("string", style_table_cell_center), Paragraph("Yes", style_table_cell_center), Paragraph("Target Indian state or district (e.g. `\"Uttar Pradesh\"`, `\"Meerut\"`)", style_table_cell)],
        [Paragraph("`prediction_date`", style_table_cell), Paragraph("string", style_table_cell_center), Paragraph("Yes", style_table_cell_center), Paragraph("Forecast date formatted as `\"YYYY-MM-DD\"` (e.g. `\"2024-06-15\"`)", style_table_cell)],
        [Paragraph("`crop_name`", style_table_cell), Paragraph("string", style_table_cell_center), Paragraph("Optional", style_table_cell_center), Paragraph("Crop type (`\"Rice\"`, `\"Maize\"`, `\"Cotton\"`, `\"Soybean\"`) (Default: `\"Rice\"`)", style_table_cell)],
        [Paragraph("`growth_stage`", style_table_cell), Paragraph("string", style_table_cell_center), Paragraph("Optional", style_table_cell_center), Paragraph("Growth stage (`\"Sowing\"`, `\"Vegetative\"`, `\"Flowering\"`, etc.) (Default: `\"Sowing\"`)", style_table_cell)],
        [Paragraph("`soil_moisture_pct`", style_table_cell), Paragraph("float", style_table_cell_center), Paragraph("Optional", style_table_cell_center), Paragraph("Volumetric soil moisture percentage (0-100%) (e.g. `25.0`)", style_table_cell)],
    ]
    t_req = Table([req_headers] + req_rows, colWidths=[110, 60, 60, 250])
    t_req.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), c_primary),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(t_req)
    story.append(Spacer(1, 12))

    story.append(Paragraph("6.2 Sample API Response Payload Structure", style_h2))
    
    json_sample = (
        "{\n"
        "  \"status\": \"SUCCESS\",\n"
        "  \"metadata\": {\n"
        "    \"requested_location\": \"Uttar Pradesh\",\n"
        "    \"resolved_state\": \"Uttar Pradesh\",\n"
        "    \"is_direct_match\": true,\n"
        "    \"location_resolution_note\": \"Direct validated Phase 3B model for Uttar Pradesh.\",\n"
        "    \"model_version\": \"Phase_3B_Official_Production\",\n"
        "    \"advisory_engine_version\": \"Phase_6_Rule_Engine\"\n"
        "  },\n"
        "  \"probabilities\": {\n"
        "    \"onset\": { \"7d\": 6.6, \"14d\": 30.0, \"21d\": 41.2, \"30d\": 86.2 },\n"
        "    \"break_spell\": { \"7d\": 95.5, \"14d\": 100.0, \"21d\": 81.9, \"30d\": 100.0 },\n"
        "    \"heavy_rain\": { \"7d\": 0.0, \"14d\": 3.4, \"21d\": 0.7, \"30d\": 5.5 }\n"
        "  },\n"
        "  \"advisory\": {\n"
        "    \"risk_level\": \"VERY_HIGH\",\n"
        "    \"event_type\": \"BREAK_SPELL\",\n"
        "    \"horizon_days\": 7,\n"
        "    \"probability\": 95.5,\n"
        "    \"false_onset_risk\": false,\n"
        "    \"title\": \"🟠 High Dry-Spell Risk\",\n"
        "    \"primary_action\": \"Delay rain-dependent Rice sowing if practical due to imminent dry spell.\",\n"
        "    \"supporting_actions\": [\n"
        "      \"Prepare supplemental irrigation facilities\",\n"
        "      \"Keep nursery beds covered and hydrated\"\n"
        "    ],\n"
        "    \"advisory_code\": \"BREAK_SPELL_WARNING\"\n"
        "  }\n"
        "}"
    )

    t_json = Table([[Paragraph(f"<font fontName='Courier' size=7.5 color='#0F172A'><pre>{json_sample}</pre></font>", style_body)]], colWidths=[480])
    t_json.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F1F5F9")),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#CBD5E1")),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(t_json)

    story.append(PageBreak())

    # =============================================================
    # CHAPTER 7: QUICKSTART, DEPLOYMENT & ROADMAP
    # =============================================================
    story.append(Paragraph("7. Quickstart, Deployment & Future Roadmap", style_h1))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceAfter=10))

    story.append(Paragraph("7.1 Local Execution & Environment Setup", style_h2))
    story.append(Paragraph("Follow these steps to launch the complete system locally:", style_body))

    cmd_text = (
        "<b># Step 1: Set up & launch FastAPI Backend</b><br/>"
        "cd backend<br/>"
        "python -m venv venv<br/>"
        ".\\venv\\Scripts\\Activate.ps1 &nbsp;&nbsp;<i># Windows PowerShell</i><br/>"
        "pip install -r requirements.txt<br/>"
        "python test_inference_pipeline.py &nbsp;&nbsp;<i># Run unit tests</i><br/>"
        "python -m uvicorn main:app --reload --port 8000<br/><br/>"
        "<b># Step 2: Set up & launch React Frontend</b><br/>"
        "cd ../frontend<br/>"
        "npm install<br/>"
        "npm run dev &nbsp;&nbsp;<i># Frontend running at http://localhost:5173</i>"
    )
    t_cmd = Table([[Paragraph(f"<font fontName='Courier' size=8 color='#0F172A'>{cmd_text}</font>", style_body)]], colWidths=[480])
    t_cmd.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#CBD5E1")),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(t_cmd)
    story.append(Spacer(1, 14))

    story.append(Paragraph("7.2 Operational & Future Roadmap", style_h2))
    story.append(Paragraph("• <b>Hyper-Local Block Level Grid Interpolation:</b> Upgrade spatial mapping to interpolate IMD grid points down to block level (Panchayat level) using Inverse Distance Weighting (IDW).", style_bullet))
    story.append(Paragraph("• <b>Satellite Soil Moisture Assimilation:</b> Integrate real-time SMAP / Sentinel-1 Synthetic Aperture Radar (SAR) soil moisture retrievals directly into backend inference vectors.", style_bullet))
    story.append(Paragraph("• <b>Multi-Channel Voice & Broadcast Delivery:</b> Connect automated WhatsApp Bot and IVR voice notification channels (in Hindi, Marathi, Bengali, Tamil, etc.) to reach smallholders without smartphones.", style_bullet))
    story.append(Spacer(1, 14))

    # Agronomic Disclaimer Box
    disclaimer_text = (
        "<b>⚠️ Operational Agronomic Disclaimer:</b> The rules in this MVP agricultural advisory engine represent "
        "deterministic engineering heuristics based on validated meteorological models and agronomic literature. "
        "They provide decision-support guidance and must be validated by local Krishi Vigyan Kendra (KVK) extension officers "
        "and agricultural authorities before committing large-scale financial resources or executing field deployment."
    )
    t_disc = Table([[Paragraph(disclaimer_text, style_callout)]], colWidths=[480])
    t_disc.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#FEF3C7")),
        ('BOX', (0, 0), (-1, -1), 1.5, colors.HexColor("#D97706")),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(t_disc)

    # Build PDF Document
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Comprehensive PDF Report successfully built at: {OUTPUT_PDF}")


if __name__ == "__main__":
    build_pdf()
