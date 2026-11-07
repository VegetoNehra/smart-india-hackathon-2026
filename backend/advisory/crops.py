"""
Crop and Growth Stage Catalog & Agronomic Action Engine.
Defines supported crops, stages, and agronomic risk sensitivity profiles.
Generates tailored advisory actions for 50+ crops across 6 growth stages in English and Hindi.
"""

SUPPORTED_CROPS = [
    "Rice", "Wheat", "Maize", "Cotton", "Soybean", "Sugarcane", "Gram",
    "Tur (Pigeon Pea)", "Groundnut", "Mustard", "Bajra", "Jowar", "Potato",
    "Onion", "Barley", "Moong", "Urad", "Ragi", "Sunflower", "Jute"
]

GROWTH_STAGES = [
    "Sowing",
    "Germination / Establishment",
    "Vegetative",
    "Flowering",
    "Grain/Fruit Development",
    "Harvest"
]

def get_crop_category(crop_name: str) -> str:
    c = crop_name.lower()
    if "rice" in c or "paddy" in c:
        return "RICE"
    elif "wheat" in c or "barley" in c:
        return "WHEAT"
    elif "cotton" in c or "jute" in c or "mesta" in c:
        return "FIBER"
    elif "sugarcane" in c:
        return "SUGARCANE"
    elif "soybean" in c or "groundnut" in c or "mustard" in c or "sunflower" in c or "sesamum" in c or "castor" in c or "linseed" in c or "oilseed" in c:
        return "OILSEED"
    elif "gram" in c or "tur" in c or "pulse" in c or "moong" in c or "urad" in c or "arhar" in c or "masoor" in c or "pea" in c:
        return "PULSES"
    elif "maize" in c or "bajra" in c or "jowar" in c or "ragi" in c or "millet" in c or "cereal" in c:
        return "COARSE_GRAINS"
    elif "potato" in c or "onion" in c or "garlic" in c or "chilli" in c or "turmeric" in c or "ginger" in c or "vegetable" in c or "spice" in c:
        return "HORTICULTURE"
    else:
        return "GENERAL"

def generate_crop_stage_action(crop_name: str, stage: str, event_type: str, soil_moisture: float = None, lang: str = "en") -> tuple[str, list]:
    """
    Generates specific primary action and supporting actions for any crop, stage, and climate event.
    Supports English ('en') and Hindi ('hi').
    """
    cat = get_crop_category(crop_name)
    s = stage.lower()
    is_hi = (lang == "hi")

    # 1. FALSE ONSET RISK
    if event_type == "FALSE_ONSET":
        if "sow" in s or "establis" in s or "germina" in s:
            if is_hi:
                primary = f"केवल शुरुआती बारिश के आधार पर {crop_name} की {stage} कार्य न करें। निरंतर नमी बनने तक बारिश-आधारित बुआई टालें या सिंचाई व्यवस्था रखें।"
                supp = ["नर्सरी/बीज तैयार रखें पर मुख्य खेत में बुआई बारिश स्थिर होने तक स्थगित रखें", "बुआई से पहले 7-दिवसीय मृदा नमी रुझान की जांच करें"]
            else:
                primary = f"Avoid relying solely on initial monsoon rain for {crop_name} {stage.lower()}. Delay rain-dependent sowing until sustained moisture settles, or ensure backup irrigation."
                supp = ["Keep seeds/nurseries ready but postpone field sowing until rainfall stabilizes", "Monitor 7-day soil moisture trend before committing main field sowing"]
        elif "flower" in s or "fruit" in s or "grain" in s:
            if is_hi:
                primary = f"शुरुआती बारिश के बाद सूखा काल संभावित है। अत्यंत संवेदनशील {stage} अवस्था पर {crop_name} के लिए जीवनरक्षक सूक्ष्म-सिंचाई तैयार रखें।"
                supp = ["जड़ क्षेत्र में पानी रोकने के लिए मेढ़बंदी करें", "मृदा वाष्पीकरण रोकने हेतु जैविक मल्चिंग अपनाएं"]
            else:
                primary = f"Initial monsoon rain will be followed by an early dry spell. Prepare life-saving micro-irrigation for {crop_name} at critical {stage.lower()} stage."
                supp = ["Construct field bunds to harvest initial rain water in root zone", "Apply organic mulch to minimize evaporative soil water loss"]
        elif "harvest" in s:
            if is_hi:
                primary = f"शुरुआती बारिश के बाद सूखा काल आ सकता है। {crop_name} की कटाई के लिए बारिश के अंतराल का उपयोग करें और तिरपाल तैयार रखें।"
                supp = ["कटी हुई फसल को ऊंचे शेड में रखें", "अचानक बारिश से बचाने हेतु खलिहान में तिरपाल ढकें"]
            else:
                primary = f"Initial rainfall may be followed by a dry spell. Utilize rain breaks for {crop_name} harvesting, keeping tarpaulins ready for sudden early showers."
                supp = ["Move harvested produce to covered sheds", "Keep heavy tarpaulins ready at threshing yards"]
        else:
            if is_hi:
                primary = f"शुरुआती बारिश के बाद लंबा सूखा आ सकता है। नमी स्थिर होने तक {crop_name} ({stage}) पर अधिक उर्वरक न डालें।"
                supp = ["संरक्षित सिंचाई व्यवस्था तैयार रखें", "मिट्टी की नमी बचाने के लिए न्यूनतम निराई करें"]
            else:
                primary = f"Initial rainfall may be followed by a prolonged dry spell. Avoid heavy fertilizer top-dressing on {crop_name} ({stage}) until moisture settles."
                supp = ["Prepare protective irrigation facilities", "Keep weeding operations minimal to retain soil cover"]
        return primary, supp

    # 2. BREAK SPELL (DRY SPELL) RISK
    elif event_type == "BREAK_SPELL":
        if "sow" in s or "establis" in s or "germina" in s:
            if cat == "RICE":
                primary = "धान की बुआई / रोपाई टालें। पौधशाला (nursery) में हल्की सिंचाई देकर नमी बनाए रखें।" if is_hi else "Delay rain-dependent Rice transplanting/sowing. Keep paddy nurseries hydrated under light irrigation."
                supp = ["धान नर्सरी के लिए गीली क्यारी विधि अपनाएं", "तेज धूप के समय पौधशाला को हल्की छाया दें"] if is_hi else ["Use wet seedbed method for paddy nursery", "Apply protective shade cover during peak dry hours"]
            elif cat == "WHEAT":
                primary = "सूखी मिट्टी में अंकुरण विफलता से बचने के लिए गेहूं की बुआई से पहले पलेवा (Pre-sowing irrigation) अवश्य करें।" if is_hi else "Ensure pre-sowing irrigation (Palewa) before sowing Wheat to prevent germination failure in dry soil."
                supp = ["बुआई की गहराई 3-5 सेमी बनाए रखें", "जड़ वृद्धि हेतु बीजों को ट्राइकोडर्मा से उपचारित करें"] if is_hi else ["Maintain optimum 3-5 cm sowing depth", "Treat seeds with Trichoderma for root vigor"]
            elif cat == "FIBER":
                primary = "मिट्टी में 15-20 सेमी गहराई तक नमी होने तक कपास/जूट की बुआई टालें या ड्रिप सिंचाई से बुआई करें।" if is_hi else "Delay Cotton/Jute sowing until soil moisture reaches 15-20 cm depth, or sow with drip irrigation."
                supp = ["नमी संरक्षण हेतु मेढ़ों/कूड़ों पर बुआई करें", "शुष्क ऊपरी मिट्टी में गहरी बुआई से बचें"] if is_hi else ["Sow on ridges/furrows to concentrate moisture", "Avoid deep sowing in dry topsoil"]
            elif cat == "SUGARCANE":
                primary = "सूखा काल के दौरान मिट्टी की नमी बचाने के लिए गन्ने की पंक्तियों के बीच सूखी पत्ती की मल्चिंग करें।" if is_hi else "Apply trash mulching between sugarcane rows to conserve soil moisture during imminent dry spell."
                supp = ["एक छोड़कर एक नाली में सिंचाई करें", "वाष्पोत्सर्जन घटाने हेतु 1% केसीएल का छिड़काव करें"] if is_hi else ["Irrigate alternate furrows to stretch water supply", "Spray 1% Potassium Chloride (KCl) to reduce transpiration"]
            elif cat == "PULSES":
                primary = f"बारिश पर निर्भर {crop_name} की बुआई टालें। मिट्टी की नमी 15% से कम होने पर अंकुरण प्रभावित होता है।" if is_hi else f"Delay rain-dependent {crop_name} sowing. Seed germination fails rapidly if soil moisture drops below 15%."
                supp = ["बीजों को राइजोबियम कल्चर से उपचारित करें", "जीवनरक्षक सिंचाई हेतु स्प्रिंकलर तैयार रखें"] if is_hi else ["Inoculate seeds with Rhizobium culture", "Prepare farm ponds/sprinklers for life-saving irrigation"]
            elif cat == "HORTICULTURE":
                primary = f"खुले खेतों में {crop_name} की रोपाई टालें। नर्सरी को छाया प्रदान करें और ड्रिप से सिंचाई दें।" if is_hi else f"Delay planting {crop_name} in open fields. Provide shaded nursery protection and light drip irrigation."
                supp = ["एंटी-ट्रांसपायरेंट स्प्रे का प्रयोग करें", "जड़ क्षेत्र के चारों ओर पुआल की मल्चिंग करें"] if is_hi else ["Use anti-transpirant sprays if available", "Apply straw mulch around root zones"]
            else:
                primary = f"आसन्न सूखा काल के कारण {crop_name} की बुआई टालें। पूरक सिंचाई का विकल्प तैयार रखें।" if is_hi else f"Delay rain-dependent {crop_name} sowing if practical due to imminent 14D dry spell."
                supp = ["पूरक सिंचाई के विकल्प तैयार रखें", "नर्सरी क्यारियों को ढककर नमीयुक्त रखें"] if is_hi else ["Prepare supplemental irrigation alternatives", "Keep nursery beds covered and hydrated"]

        elif "flower" in s or "fruit" in s or "grain" in s:
            if cat == "RICE":
                primary = "अत्यंत संवेदनशील अवस्था: दाना बांझपन रोकने के लिए धान की बालियां निकलने और पुष्पन अवस्था में 3-5 सेमी पानी बनाए रखें।" if is_hi else "CRITICAL STAGE: Maintain 3-5 cm standing water layer in Rice during panicle initiation and flowering to prevent grain sterility."
                supp = ["पानी की कमी होने पर एकांतर सुखाने व भिगोने (AWD) की विधि अपनाएं", "पुष्पन के दौरान खेत का पानी न निकालें"] if is_hi else ["Execute alternate wetting and drying (AWD) if water supply is constrained", "Refrain from draining fields during flowering"]
            elif cat == "WHEAT":
                primary = "अत्यंत संवेदनशील अवस्था: सूखे और गर्मी के तनाव से बचाने के लिए गेहूं की बालियां निकलने/पुष्पन अवस्था में सिंचाई करें।" if is_hi else "CRITICAL STAGE: Provide booting/flowering stage irrigation for Wheat to protect against drought and terminal heat stress."
                supp = ["दाना भरने के दौरान हल्की व बार-बार सिंचाई करें", "तेज हवा वाले दिनों में सिंचाई से बचें"] if is_hi else ["Apply light frequent irrigation during grain filling", "Avoid irrigation during strong windy days to prevent lodging"]
            elif cat == "FIBER":
                primary = "अत्यंत संवेदनशील अवस्था: फूल एवं गूलर (boll) झड़ने से रोकने के लिए कपास में जीवनरक्षक सिंचाई दें।" if is_hi else "CRITICAL STAGE: Provide protective micro-irrigation to Cotton during flowering/boll formation to prevent boll shedding."
                supp = ["फूल झड़ने से रोकने हेतु 2% डीएपी या पोटेशियम नाइट्रेट का छिड़काव करें", "खेत को खरपतवार मुक्त रखें"] if is_hi else ["Spray 2% DAP or Potassium Nitrate to reduce flower drop", "Maintain weed-free field to eliminate water competition"]
            elif cat == "PULSES":
                primary = f"अत्यंत संवेदनशील अवस्था: {crop_name} में फूल आते समय नमी की कमी से फूल झड़ने लगते हैं। तुरंत सिंचाई दें।" if is_hi else f"CRITICAL STAGE: Moisture stress during {crop_name} flowering causes severe flower drop. Provide life-saving irrigation immediately."
                supp = ["अधिक नाइट्रोजन न डालें; 2% यूरिया या 1% केएनओ3 का पर्णीय छिड़काव करें", "शुष्क गर्मी में फली छेदक कीट की निगरानी करें"] if is_hi else ["Avoid excess nitrogen; apply foliar spray of 2% urea or 1% KNO3", "Monitor for pod borer pest buildup under dry heat"]
            elif cat == "OILSEED":
                primary = f"अत्यंत संवेदनशील अवस्था: दाना/फल विकास हेतु {crop_name} में पुष्पन/फली बनते समय सिंचाई करें।" if is_hi else f"CRITICAL STAGE: Provide protective irrigation for {crop_name} during pegging/flowering to ensure optimum seed development."
                supp = ["जड़ की गहराई तक मिट्टी में नमी बनाए रखें", "शुष्क मिट्टी होने पर जिप्सम या सल्फर दें"] if is_hi else ["Maintain soil moisture at root depth", "Apply gypsum / sulphur inputs if soil is dry"]
            else:
                primary = f"अत्यंत संवेदनशील अवस्था: उपज क्षति और फूल झड़ने से रोकने के लिए {crop_name} ({stage}) में सिंचाई करें।" if is_hi else f"CRITICAL STAGE: Provide protective irrigation for {crop_name} ({stage}) to prevent flower drop and yield loss."
                supp = ["दैनिक आधार पर मृदा नमी की निगरानी करें", "नमी संरक्षण हेतु जैविक मल्चिंग करें"] if is_hi else ["Monitor soil moisture daily", "Apply organic mulch to conserve root-zone moisture"]

        elif "harvest" in s:
            primary = f"मौसम शुष्क और कटाई के लिए अनुकूल है। {crop_name} की कटाई और गहाई (threshing) शीघ्र पूरी करें।" if is_hi else f"Weather conditions are dry and favorable for harvesting. Complete {crop_name} harvesting and threshing early."
            supp = ["कटाई किए गए अनाज को सुरक्षित नमी स्तर (<12%) तक सुखाएं", "अनाज को नमी-रोधी बोरियों में रखें"] if is_hi else ["Sun-dry harvested grains to safe moisture level (<12%)", "Store produce in moisture-proof bags"]

        else: # VEGETATIVE STAGE
            if soil_moisture is not None and soil_moisture <= 20.0:
                primary = f"मृदा नमी अत्यधिक कम है ({soil_moisture:.0f}%)। {crop_name} ({stage}) में तुरंत जीवनरक्षक सिंचाई करें।" if is_hi else f"Soil moisture is critically low ({soil_moisture:.0f}%). Execute protective irrigation immediately for {crop_name} ({stage})."
            else:
                primary = f"मृदा नमी संरक्षण हेतु {crop_name} ({stage}) में निराई-गुड़ाई (intercultural weeding) करें।" if is_hi else f"Execute intercultural weeding and shallow hoeing in {crop_name} to create dust mulch and conserve root-zone soil moisture."
            supp = ["सिंचाई के बाद ही उर्वरक की टॉप-ड्रेसिंग करें", "पानी की बचत हेतु एकांतर नाली सिंचाई अपनाएं"] if is_hi else ["Top-dress fertilizer only after irrigation", "Prepare alternate furrow irrigation to save water"]

        return primary, supp

    # 3. HEAVY RAIN THREAT
    elif event_type == "HEAVY_RAIN":
        if "sow" in s or "establis" in s or "germina" in s:
            if cat == "RICE":
                primary = "धान की नर्सरी में जल निकासी नाली साफ करें। अत्यधिक जलजमाव से पौध सड़न की समस्या होती है।" if is_hi else "Clear nursery drainage channels. Excess standing water submerges young Rice seedlings and causes root rot."
                supp = ["पौधशाला क्यारियों से अतिरिक्त पानी निकालें", "भारी बारिश बीतने तक नई बुआई न करें"] if is_hi else ["Drain excess water from seedbeds", "Avoid fresh sowing until heavy rainfall passes"]
            elif cat == "COARSE_GRAINS" or cat == "PULSES":
                primary = f"जलजमाव से बीज सड़न रोकने के लिए {crop_name} की बुआई मेढ़ों (raised beds) पर करें।" if is_hi else f"Sow {crop_name} on raised beds / ridges. Standing water for >24h causes seed rot and germination failure."
                supp = ["खेत की सीमा नालियों को साफ करें", "निचले जलभराव वाले खेतों में बुआई से बचें"] if is_hi else ["Clear field boundary furrows", "Refrain from sowing in low-lying un-drained fields"]
            elif cat == "HORTICULTURE":
                primary = f"जलभराव वाले खेतों में {crop_name} न लगाएं। कंद/जड़ सड़न रोकने के लिए गहरी जल निकासी नाली बनाएं।" if is_hi else f"Do not plant {crop_name} in flooded fields. Ensure deep drainage furrows to prevent seed tuber rot."
                supp = ["रोपाई के लिए उठी हुई क्यारियां बनाएं", "रोपाई से पूर्व कंदों का फफूंदनाशी उपचार करें"] if is_hi else ["Construct raised mounds for planting", "Spray fungicidal seed treatment before planting"]
            else:
                primary = f"भारी बारिश बीतने तक {crop_name} की बुआई टालें। खेत की जल निकासी व्यवस्था दुरुस्त करें।" if is_hi else f"Postpone {crop_name} sowing until heavy rainfall passes. Check and clear field drainage systems."
                supp = ["जल निकासी नालियों से रुकावट हटाएं", "बीज भंडार को सूखे ऊंचे स्थानों पर रखें"] if is_hi else ["Ensure drainage channels are clear of debris", "Protect seed stocks in dry elevated storage"]

        elif "flower" in s or "fruit" in s or "grain" in s or "vegetat" in s:
            if cat == "FIBER":
                primary = "कपास के खेत की नालियां तुरंत साफ करें। 48 घंटे से अधिक जलभराव से जड़ सड़न रोग हो सकता है।" if is_hi else "Clear Cotton field furrows immediately. Waterlogging for >48 hours causes root hypoxia and fungal wilt."
                supp = ["बारिश के बाद रस चूसक कीटों की निगरानी करें", "बारिश के दौरान कीटनाशक छिड़काव न करें"] if is_hi else ["Inspect for sucking pest outbreaks after rain", "Avoid spraying pesticides during rain spells"]
            elif cat == "SUGARCANE":
                primary = "भारी बारिश और तेज हवा से गन्ने को गिरने (lodging) से बचाने के लिए बंधाई (propping) करें।" if is_hi else "Tie up Sugarcane stalks (propping) to prevent crop lodging under heavy rain and strong winds."
                supp = ["मुख्य जल निकासी नालियों को साफ रखें", "जड़ सड़न रोकने हेतु जमा पानी निकालें"] if is_hi else ["Clear main drainage canals", "Drain standing water to prevent root rot"]
            elif cat == "PULSES" or cat == "COARSE_GRAINS":
                primary = f"{crop_name} ({stage}) के खेत से अतिरिक्त पानी तुरंत निकालें। अधिक नमी से उकठा (wilt) रोग फैलता है।" if is_hi else f"Ensure rapid surface drainage for {crop_name} ({stage}). Excess soil moisture triggers wilt and phytophthora rot."
                supp = ["भारी बारिश में उर्वरक न डालें", "उघड़ने पर सर्वांगीण फफूंदनाशी का छिड़काव करें"] if is_hi else ["Refrain from applying fertilizer during heavy rain", "Spray systemic fungicide after rain clears"]
            elif cat == "HORTICULTURE":
                primary = f"सड़न व फफूंद जनित रोगों को रोकने के लिए {crop_name} के खेत में खड़ा पानी तुरंत बाहर निकालें।" if is_hi else f"Drain standing water immediately from {crop_name} fields to prevent soft rot and fungal blight outbreaks."
                supp = ["जल निकासी के बाद कॉपर ऑक्सीक्लोराइड का छिड़काव करें", "क्यारियों को जलभराव मुक्त रखें"] if is_hi else ["Apply drenching of Copper Oxychloride after drainage", "Keep raised beds free of stagnant water"]
            else:
                primary = f"जलभराव व फसल नुकसान से बचने के लिए {crop_name} ({stage}) के खेत की जल निकासी नाली साफ करें।" if is_hi else f"Check and clear field drainage channels for {crop_name} ({stage}) to prevent waterlogging and crop damage."
                supp = ["खेत का अतिरिक्त पानी मुख्य नाली में बहने दें", "खेत में किसी भी प्रकार की सिंचाई रोक दें"] if is_hi else ["Ensure field runoff flows freely into main drains", "Refrain from all field irrigation"]

        elif "harvest" in s:
            primary = f"बारिश रुकने तक {crop_name} की कटाई स्थगित रखें। कटी हुई फसल को तिरपाल से ढककर रखें।" if is_hi else f"Postpone {crop_name} harvesting until rain clears. Cover harvested crop bundles in field with heavy tarpaulins."
            supp = ["कटी हुई फसल को ऊंचे ढके हुए शेड में ले जाएं", "सड़न व अंकुरण रोकने हेतु खलिहान सुखाएं"] if is_hi else ["Move harvested produce to raised covered sheds", "Drain threshing yards to prevent grain molding and sprouting"]

        else:
            primary = f"जलभराव रोकने के लिए {crop_name} ({stage}) के खेत की जल निकासी नालियों की जांच करें।" if is_hi else f"Inspect field drainage furrows for {crop_name} ({stage}) to prevent waterlogging."
            supp = ["मुख्य जल निकास द्वार खुला रखें", "भारी बारिश के दौरान उर्वरक न डालें"] if is_hi else ["Keep main drainage outlets open", "Avoid fertilizer application during heavy rain"]

        return primary, supp

    # 4. MONSOON ONSET (FAVORABLE RAIN)
    elif event_type == "MONSOON_ONSET":
        if "sow" in s or "establis" in s or "germina" in s:
            primary = f"🟢 अनुकूल मानसून आगमन: नमी अनुकूल होते ही {crop_name} की {stage} हेतु भूमि व बीज तैयार करें।" if is_hi else f"🟢 Favorable Monsoon Onset: Prepare land and seed stocks for {crop_name} {stage.lower()} as soil moisture conditions settle."
            supp = ["जैव-उर्वरकों से बीज उपचार पूरा करें", "बीज शय्या को भुरभुरा और नम बनाएं"] if is_hi else ["Finalize seed treatment with bio-fertilizers", "Ensure seedbed is well-pulverized and moist"]
        elif "harvest" in s:
            primary = f"🟢 अनुकूल मानसून आगमन: कटाई के समय मानसून बारिश संभावित है। गहाई शीघ्र कर उपज को सुरक्षित स्थान पर रखें।" if is_hi else f"🟢 Favorable Monsoon Onset: Monsoon rain incoming during {crop_name} harvest. Complete threshing and move produce to safe indoor storage."
            supp = ["कटाई की गति तेज करें", "भंडारण गृह को नमी-मुक्त रखें"] if is_hi else ["Accelerate harvesting pace", "Ensure storage structure remains moisture-free"]
        else:
            primary = f"🟢 अनुकूल मानसून आगमन: पर्याप्त नमी मिलने पर {crop_name} ({stage}) में अनुशंसित नाइट्रोजन की टॉप-ड्रेसिंग करें।" if is_hi else f"🟢 Favorable Monsoon Onset: Apply recommended top-dressing nitrogen fertilizer for {crop_name} ({stage}) as soil moisture is optimum."
            supp = ["पोषण प्रतिस्पर्धा घटाने हेतु खरपतवार नियंत्रण करें", "खेत की मेढ़बंदी मजबूत रखें"] if is_hi else ["Perform intercultural weeding to eliminate nutrient competition", "Maintain optimum field bunding"]

        return primary, supp

    # 5. ROUTINE WEATHER
    else:
        primary = f"{crop_name} ({stage}) हेतु सामान्य कृषि कार्य और नियमित मौसम निगरानी जारी रखें।" if is_hi else f"Continue standard field practices and routine weather monitoring for {crop_name} ({stage})."
        supp = ["नियमित खेत निरीक्षण बनाए रखें", "साप्ताहिक वर्षा अपडेट की निगरानी करें"] if is_hi else ["Maintain routine field inspections", "Monitor weekly rainfall updates"]
        return primary, supp
