export const translations = {
  en: {
    // Topbar & Header
    app_title: "Monsoon Intelligence",
    live_model: "Live Model",
    national_overview: "National Advisory Overview",
    select_state: "Select State",
    select_district: "Select District",
    language: "Language",
    
    // Sidebar
    nav_dashboard: "Dashboard",
    nav_map: "Map",
    nav_datasources: "Data Sources",
    nav_model: "Model",
    nav_advisory: "Advisory",
    nav_settings: "Settings",

    // HeroStatus & Badges
    hero_onset_label: "7D Monsoon Onset Probability",
    state_monitor: "State Monitor",
    district_monitor: "District Monitor",
    regional_baseline: "Regional Baseline",
    direct_model: "Direct Validated Model",
    consensus_note: "Phase 3B Calibrated Model Consensus (Date: 2024-06-15)",
    
    // Status Badges
    status_normal: "NORMAL",
    status_watch: "ELEVATED WATCH",
    status_alert: "HIGH ALERT",
    status_false_onset: "FALSE-ONSET ALERT",

    // Metrics
    metric_break_7d: "Break Spell (7D)",
    metric_heavy_7d: "Heavy Rain (7D)",
    metric_soil_moist: "Soil Moist.",
    metric_confidence: "Confidence",

    // Voice Assistant
    voice_summary: "Voice Summary",
    listen_voice: "Listen to Voice Summary",
    listen_advisory: "Listen to Advisory",
    stop_voice: "Stop Audio",
    speaking_now: "Speaking Forecast...",
    speaking_advisory: "Speaking Advisory...",

    // KPI Strip
    kpi_onset_label: "14D Monsoon Onset Likelihood",
    kpi_break_label: "14D Break Spell Risk",
    kpi_heavy_label: "14D Heavy Rain Likelihood",
    kpi_confidence_label: "Phase 3B Isotonic Consensus",
    trend_high: "HIGH",
    trend_moderate: "MODERATE",
    trend_elevated_risk: "ELEVATED RISK",
    trend_low_risk: "LOW RISK",
    trend_warning: "WARNING",
    trend_verified: "VERIFIED",

    // ForecastOutlook
    outlook_title: "Monsoon Outlook",
    outlook_subtitle: "Phase 3B Calibrated Probabilities",
    area_onset: "Onset %",
    area_break: "Break Spell %",

    // Advisory Card Header & Tags
    advisory_phase6_title: "Phase 6 Agricultural Advisory",
    risk_high: "HIGH RISK",
    risk_very_high: "VERY HIGH RISK",
    risk_moderate: "MODERATE RISK",
    risk_low: "LOW RISK",
    select_crop_label: "Select Crop:",
    select_stage_label: "Growth Stage:",
    select_location_label: "Select Location:",
    active_region: "Active Region:",
    scenario_sim_label: "Simulate Climate Scenario:",

    // Advisory Codes & Fallbacks
    advisory_default_title: "Delay sowing by 3–4 days",
    advisory_default_action: "A possible dry spell may follow expected rainfall. Delay rain-dependent sowing until sustained moisture settles.",

    code_FALSE_ONSET_WARNING_title: "⚠️ False-Onset Risk Warning",
    code_FALSE_ONSET_WARNING_action: "Avoid relying solely on initial rainfall for sowing. Delay rain-dependent sowing until sustained moisture settles.",
    code_FALSE_ONSET_WARNING_msg: "Monsoon onset appears likely, but break-spell risk remains high over the next 14 days.",

    code_BREAK_SPELL_WARNING_title: "🟠 High Dry-Spell Risk",
    code_BREAK_SPELL_WARNING_action: "Delay rain-dependent sowing if practical due to imminent dry spell. Prepare supplemental irrigation alternatives.",
    code_BREAK_SPELL_WARNING_msg: "A prolonged dry spell (break spell) is likely over the next 7–14 days.",

    code_HEAVY_RAIN_WARNING_title: "⚡ High Heavy Rainfall Alert",
    code_HEAVY_RAIN_WARNING_action: "Check and clear field drainage systems to prevent waterlogging and crop damage.",
    code_HEAVY_RAIN_WARNING_msg: "Heavy rainfall event probability is high over the next 7-14 days.",

    code_ONSET_FAVORABLE_title: "🟢 Favorable Monsoon Onset Alert",
    code_ONSET_FAVORABLE_action: "Prepare land and seed stocks for sowing as soil moisture conditions settle.",
    code_ONSET_FAVORABLE_msg: "Monsoon onset probability is favorable with low break-spell conflict.",

    code_ROUTINE_MONITORING_title: "ℹ️ Routine Weather Monitoring",
    code_ROUTINE_MONITORING_action: "Continue standard field practices and routine monitoring.",
    code_ROUTINE_MONITORING_msg: "No immediate extreme weather risk detected over the next 7–14 days.",

    // Crop & Stage specific advisory actions
    adv_rice_sowing: "Delay rain-dependent Rice sowing until continuous monsoon onset is confirmed. Keep nursery beds covered.",
    adv_rice_vegetative: "Maintain 2-5 cm standing water in paddy fields. Monitor for stem borer and leaf folder pests.",
    adv_rice_flowering: "Ensure adequate water supply during flowering stage. Avoid field draining to prevent grain sterility.",

    adv_maize_sowing: "Sow Maize on raised beds to prevent seed rot from sudden heavy rainfall events. Maintain optimum moisture.",
    adv_maize_vegetative: "Apply top-dressing nitrogen fertilizer when soil moisture is adequate. Clear drainage furrows.",
    adv_maize_flowering: "Protect silks from extreme moisture stress. Ensure field remains free from standing water.",

    adv_cotton_sowing: "Delay Cotton sowing if dry spell risk is high. Sow when topsoil moisture reaches 15-20 cm depth.",
    adv_cotton_vegetative: "Perform intercultural weeding and earthing up. Monitor for sucking pests like aphids and jassids.",
    adv_cotton_flowering: "Avoid excess nitrogen application to prevent boll shedding. Maintain uniform soil moisture.",

    adv_soybean_sowing: "Treat Soybean seeds with Bradyrhizobium inoculant before sowing. Sow at 3-4 cm depth.",
    adv_soybean_vegetative: "Keep field weed-free during first 30-45 days. Inspect for tobacco caterpillar and girdle beetle.",
    adv_soybean_flowering: "Critical moisture requirement stage. Provide protective irrigation if dry spell exceeds 7 days.",

    // Crops & Stages
    crop_rice: "Rice",
    crop_wheat: "Wheat",
    crop_maize: "Maize",
    crop_cotton: "Cotton",
    crop_sugarcane: "Sugarcane",
    crop_pulses: "Pulses",
    crop_soybean: "Soybean",
    crop_mustard: "Mustard",
    crop_gram: "Gram (Chickpea)",
    crop_tur: "Tur (Pigeon Pea)",
    crop_bajra: "Bajra (Pearl Millet)",
    crop_jowar: "Jowar (Sorghum)",
    crop_groundnut: "Groundnut",
    crop_potato: "Potato",
    crop_onion: "Onion",
    crop_barley: "Barley",
    stage_sowing: "Sowing",
    stage_germination___establishment: "Germination / Establishment",
    stage_establishment: "Germination / Establishment",
    stage_vegetative: "Vegetative",
    stage_flowering: "Flowering",
    stage_grain_fruit_development: "Grain/Fruit Development",
    stage_harvest: "Harvest",

    // Advisory Feed & Delivery Channels
    feed_title: "Recent Alerts & Advisories",
    channel_title: "Distribution Channels",
    channel_sms: "SMS Gateway",
    channel_whatsapp: "WhatsApp Bot",
    channel_voice: "IVR Voice Broadcast",
    channel_status_active: "Active",

    // Pages
    map_page_title: "Geographic Risk & Spatial Map Overview",
    map_page_desc: "Interactive spatial risk map showing district-level monsoon probabilities.",
    data_page_title: "Climate Data Sources & Meteorological Inputs",
    model_page_title: "Phase 3B Machine Learning Model Architecture",
    advisory_page_title: "Phase 6 Agricultural Advisory System Rules",
    
    // Model Intelligence Page
    model_page_subtitle: "Hybrid climate-to-local prediction framework & Isotonic calibration engine",
    architecture_title: "Phase 3B Model Architecture Pipeline",
    calibration_title: "Isotonic Probability Calibration & Reliability",
    ece_score: "Expected Calibration Error (ECE)",
    brier_score: "Brier Reliability Score",
    feature_contribution: "Feature Contribution & Importance",
    stage_inspect_title: "Pipeline Stage Inspection",

    // Settings Page
    settings_title: "SETTINGS",
    settings_subtitle: "Customize your Monsoon Intelligence experience",
    default_location: "Default Location",
    crop_preferences: "Crop Preferences",
    primary_crop: "Primary Crop",
    alert_notifications: "Alert Notifications",
    heavy_rain_alerts: "Heavy Rainfall Alerts",
    dry_spell_alerts: "Dry Spell Alerts",
    onset_alerts: "Monsoon Onset Alerts",
    irrigation_recs: "Irrigation Recommendations",
    preferences_display: "Preferences & Display",
    app_language: "Application Language",
    dashboard_density: "Dashboard Density",
    tech_info: "Show Technical Climate Info",
    save_settings: "Save Preferences",
    settings_saved: "Settings Saved Successfully!"
  },
  hi: {
    // Topbar & Header
    app_title: "मानसून इंटेलिजेंस",
    live_model: "लाइव मॉडल",
    national_overview: "राष्ट्रीय कृषि सलाह अवलोकन",
    select_state: "राज्य चुनें",
    select_district: "जिला चुनें",
    language: "भाषा",

    // Sidebar
    nav_dashboard: "डैशबोर्ड",
    nav_map: "मानचित्र",
    nav_datasources: "डेटा स्रोत",
    nav_model: "मॉडल",
    nav_advisory: "कृषि सलाह",
    nav_settings: "सेटिंग्स",

    // HeroStatus & Badges
    hero_onset_label: "7-दिवसीय मानसून आगमन संभावना",
    state_monitor: "राज्य निगरानी",
    district_monitor: "जिला निगरानी",
    regional_baseline: "क्षेत्रीय बेसलाइन मॉडल",
    direct_model: "प्रत्यक्ष सत्यापित मॉडल",
    consensus_note: "फेज 3B मॉडल सर्वसम्मति (दिनांक: 2024-06-15)",

    // Status Badges
    status_normal: "सामान्य",
    status_watch: "निगरानी",
    status_alert: "उच्च चेतावनी",
    status_false_onset: "झूठे-आगमन की चेतावनी",

    // Metrics
    metric_break_7d: "सूखा काल (7 दिन)",
    metric_heavy_7d: "भारी बारिश (7 दिन)",
    metric_soil_moist: "मृदा नमी",
    metric_confidence: "विश्वसनीयता",

    // Voice Assistant
    voice_summary: "ऑडियो सारांश",
    listen_voice: "ऑडियो सारांश सुनें",
    listen_advisory: "कृषि सलाह सुनें",
    stop_voice: "ऑडियो बंद करें",
    speaking_now: "पूर्वानुमान बोल रहा है...",
    speaking_advisory: "कृषि सलाह बोल रहा है...",

    // KPI Strip
    kpi_onset_label: "14-दिवसीय मानसून आगमन संभावना",
    kpi_break_label: "14-दिवसीय सूखा काल जोखिम",
    kpi_heavy_label: "14-दिवसीय भारी बारिश संभावना",
    kpi_confidence_label: "फेज 3B आइसोटोनिक मॉडल सहमति",
    trend_high: "उच्च",
    trend_moderate: "मध्यम",
    trend_elevated_risk: "गंभीर जोखिम",
    trend_low_risk: "कम जोखिम",
    trend_warning: "चेतावनी",
    trend_verified: "सत्यापित",

    // ForecastOutlook
    outlook_title: "मानसून पूर्वावलोकन",
    outlook_subtitle: "फेज 3B मॉडल पूर्वानुमान संभावनाएं",
    area_onset: "मानसून आगमन %",
    area_break: "सूखा काल (Break) %",

    // Advisory Card Header & Tags
    advisory_phase6_title: "फेज 6 कृषि सलाह प्रणाली",
    risk_high: "उच्च जोखिम",
    risk_very_high: "अत्यधिक उच्च जोखिम",
    risk_moderate: "मध्यम जोखिम",
    risk_low: "कम जोखिम",
    select_crop_label: "फसल चुनें:",
    select_stage_label: "वृद्धि अवस्था:",
    select_location_label: "स्थान चुनें:",
    active_region: "सक्रिय क्षेत्र:",
    scenario_sim_label: "जलवायु परिदृश्य का परीक्षण करें:",

    // Advisory Codes & Fallbacks
    advisory_default_title: "बुआई 3-4 दिन टालें",
    advisory_default_action: "संभावित बारिश के बाद सूखा काल आ सकता है। निरंतर नमी बनने तक बारिश पर निर्भर बुआई टालें।",

    code_FALSE_ONSET_WARNING_title: "⚠️ झूठे-आगमन (False-Onset) का जोखिम",
    code_FALSE_ONSET_WARNING_action: "केवल शुरुआती बारिश के आधार पर बुआई से बचें। पर्याप्त और निरंतर नमी बनने तक बारिश-आधारित बुआई टालें।",
    code_FALSE_ONSET_WARNING_msg: "मानसून का आगमन संभावित है, लेकिन अगले 14 दिनों में सूखा काल (Break Spell) का जोखिम भी उच्च है।",

    code_BREAK_SPELL_WARNING_title: "🟠 उच्च सूखा काल (Break-Spell) जोखिम",
    code_BREAK_SPELL_WARNING_action: "सूखा काल के कारण बारिश पर निर्भर बुआई को टालें। पूरक सिंचाई का विकल्प तैयार रखें।",
    code_BREAK_SPELL_WARNING_msg: "अगले 7–14 दिनों में लंबा सूखा काल संभावित है।",

    code_HEAVY_RAIN_WARNING_title: "⚡ भारी बारिश की चेतावनी",
    code_HEAVY_RAIN_WARNING_action: "जलजमाव और फसल क्षति से बचने के लिए खेत में जल निकासी चैनलों की सफाई करें।",
    code_HEAVY_RAIN_WARNING_msg: "अगले 7-14 दिनों में भारी बारिश की उच्च संभावना है।",

    code_ONSET_FAVORABLE_title: "🟢 अनुकूल मानसून आगमन चेतावनी",
    code_ONSET_FAVORABLE_action: "मृदा नमी स्थिर होने के साथ ही बुआई के लिए भूमि और बीज तैयार करें।",
    code_ONSET_FAVORABLE_msg: "मानसून का आगमन अनुकूल है और सूखा काल का जोखिम कम है।",

    code_ROUTINE_MONITORING_title: "ℹ️ नियमित मौसम निगरानी",
    code_ROUTINE_MONITORING_action: "सामान्य कृषि कार्य और नियमित खेत निरीक्षण जारी रखें।",
    code_ROUTINE_MONITORING_msg: "अगले 7-14 दिनों में कोई तात्कालिक गंभीर मौसम जोखिम नहीं है।",

    // Crop & Stage specific advisory actions in Hindi
    adv_rice_sowing: "मानसून आगमन की पुष्टि होने तक धान की बुआई टालें। नर्सरी को ढककर रखें।",
    adv_rice_vegetative: "धान के खेत में 2-5 सेमी पानी बनाए रखें। तना छेदक कीट की निगरानी करें।",
    adv_rice_flowering: "पुष्पन अवस्था में पर्याप्त पानी सुनिश्चित करें। दाना बनने तक खेत न सुखाएं।",

    adv_maize_sowing: "अचानक भारी बारिश से बीज सड़न रोकने के लिए मक्के की बुआई मेढ़ों (raised beds) पर करें।",
    adv_maize_vegetative: "पर्याप्त नमी मिलने पर नाइट्रोजन की टॉप-ड्रेसिंग करें। जल निकासी नाली साफ रखें।",
    adv_maize_flowering: "सिल्किंग अवस्था में नमी के तनाव से बचाएं। खेत में जलजमाव न होने दें।",

    adv_cotton_sowing: "सूखा काल का जोखिम होने पर कपास की बुआई टालें। मिट्टी में 15-20 सेमी गहराई तक नमी होने पर ही बुआई करें।",
    adv_cotton_vegetative: "खेत को खरपतवार मुक्त रखें। माहू (aphids) और चेपा कीट की नियमित निगरानी करें।",
    adv_cotton_flowering: "फूल एवं कलियां झड़ने से रोकने के लिए संतुलित सिंचाई करें और अधिक नाइट्रोजन न डालें।",

    adv_soybean_sowing: "बुआई से पहले सोयाबीन के बीज को राइजोबियम से उपचारित करें। 3-4 सेमी गहराई पर बुआई करें।",
    adv_soybean_vegetative: "शुरुआती 30-45 दिनों तक खेत को खरपतवार मुक्त रखें। तना मक्खी की निगरानी करें।",
    adv_soybean_flowering: "अत्यंत संवेदनशील अवस्था। यदि सूखा 7 दिन से अधिक रहे तो जीवन रक्षक सिंचाई दें।",

    // Crops & Stages
    crop_rice: "धान / चावल",
    crop_wheat: "गेहूं",
    crop_maize: "मक्का",
    crop_cotton: "कपास",
    crop_sugarcane: "गन्ना",
    crop_pulses: "दलहन",
    crop_soybean: "सोयाबीन",
    crop_mustard: "सरसों",
    crop_gram: "चना",
    crop_tur: "अरहर / तुअर",
    crop_bajra: "बाजरा",
    crop_jowar: "ज्वार",
    crop_groundnut: "मूंगफली",
    crop_potato: "आलू",
    crop_onion: "प्याज",
    crop_barley: "जौ",
    stage_sowing: "बुआई अवस्था",
    stage_germination___establishment: "अंकुरण अवस्था",
    stage_establishment: "अंकुरण अवस्था",
    stage_vegetative: "वानस्पतिक वृद्धि",
    stage_flowering: "पुष्पन अवस्था",
    stage_grain_fruit_development: "दाना / फल विकास",
    stage_harvest: "फसल कटाई",

    // Advisory Feed & Delivery Channels
    feed_title: "हाल की चेतावनियां और कृषि सलाह",
    channel_title: "सूचना वितरण माध्यम",
    channel_sms: "एसएमएस गेटवे",
    channel_whatsapp: "व्हाट्सएप बॉट",
    channel_voice: "आईवीआर वॉइस कॉल",
    channel_status_active: "सक्रिय",

    // Pages
    map_page_title: "भौगोलिक जोखिम और स्थानिक मानचित्र अवलोकन",
    map_page_desc: "जिला-स्तरीय मानसून संभावनाओं को दर्शाने वाला इंटरैक्टिव मानचित्र।",
    data_page_title: "जलवायु डेटा स्रोत और मौसम विज्ञान इनपुट",
    model_page_title: "फेज 3B मशीन लर्निंग मॉडल आर्किटेक्चर",
    advisory_page_title: "फेज 6 कृषि सलाह नियम प्रणाली",

    // Model Intelligence Page
    model_page_subtitle: "हाइब्रिड जलवायु-से-स्थानीय पूर्वानुमान ढांचा और आइसोटोनिक अंशांकन इंजन",
    architecture_title: "फेज 3B मॉडल आर्किटेक्चर पाइपलाइन",
    calibration_title: "आइसोटोनिक संभावना अंशांकन और विश्वसनीयता",
    ece_score: "अपेक्षित अंशांकन त्रुटि (ECE)",
    brier_score: "ब्रियर विश्वसनीयता स्कोर",
    feature_contribution: "विशेषता योगदान और महत्व",
    stage_inspect_title: "पाइपलाइन चरण निरीक्षण",

    // Settings Page
    settings_title: "सेटिंग्स",
    settings_subtitle: "अपने मानसून इंटेलिजेंस अनुभव को अनुकूलित करें",
    default_location: "डिफ़ॉल्ट स्थान",
    crop_preferences: "फसल प्राथमिकताएं",
    primary_crop: "प्राथमिक फसल",
    alert_notifications: "चेतावनी सूचनाएं",
    heavy_rain_alerts: "भारी बारिश की चेतावनियां",
    dry_spell_alerts: "सूखा काल (Break) की चेतावनियां",
    onset_alerts: "मानसून आगमन की चेतावनियां",
    irrigation_recs: "सिंचाई सिफारिशें",
    preferences_display: "प्राथमिकताएं और प्रदर्शन",
    app_language: "एप्लिकेशन भाषा",
    dashboard_density: "डैशबोर्ड घनत्व",
    tech_info: "तकनीकी जलवायु जानकारी दिखाएं",
    save_settings: "प्राथमिकताएं सहेजें",
    settings_saved: "सेटिंग्स सफलतापूर्वक सहेजी गईं!"
  }
};
