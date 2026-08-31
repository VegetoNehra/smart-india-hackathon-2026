from sqlalchemy.orm import Session
from datetime import datetime
from app.models.domain import Region, Forecast, Advisory
from app.services.ml_service import ml_predictor

def seed_initial_data(db: Session):
    """
    Seeds the SQLite database with initial dummy data if it is empty.
    Seeds all 28 Indian states and key weather monitoring districts.
    """
    # Check if regions already exist
    if db.query(Region).first() is not None:
        return  # Database is already seeded

    # --- 1. Create Regions Hierarchy ---
    states_data = [
        {"name": "Andhra Pradesh", "lat": 15.9129, "lng": 79.7400, "districts": [
            {"name": "Visakhapatnam", "lat": 17.6868, "lng": 83.2185},
            {"name": "Vijayawada", "lat": 16.5062, "lng": 80.6480}
        ]},
        {"name": "Arunachal Pradesh", "lat": 28.2180, "lng": 94.7278, "districts": [
            {"name": "Itanagar", "lat": 27.0844, "lng": 93.6053},
            {"name": "Tawang", "lat": 27.5855, "lng": 91.8594}
        ]},
        {"name": "Assam", "lat": 26.2006, "lng": 92.9376, "districts": [
            {"name": "Guwahati", "lat": 26.1445, "lng": 91.7362},
            {"name": "Dibrugarh", "lat": 27.4728, "lng": 94.9120}
        ]},
        {"name": "Bihar", "lat": 25.0961, "lng": 85.3131, "districts": [
            {"name": "Patna", "lat": 25.5941, "lng": 85.1376},
            {"name": "Gaya", "lat": 24.7914, "lng": 84.9997}
        ]},
        {"name": "Chhattisgarh", "lat": 21.2787, "lng": 81.8661, "districts": [
            {"name": "Raipur", "lat": 21.2514, "lng": 81.6296},
            {"name": "Bilaspur", "lat": 22.0790, "lng": 82.1391}
        ]},
        {"name": "Goa", "lat": 15.2993, "lng": 74.1240, "districts": [
            {"name": "Panaji", "lat": 15.4909, "lng": 73.8278},
            {"name": "Margao", "lat": 15.2736, "lng": 73.9582}
        ]},
        {"name": "Gujarat", "lat": 22.2587, "lng": 71.1924, "districts": [
            {"name": "Ahmedabad", "lat": 23.0225, "lng": 72.5714},
            {"name": "Surat", "lat": 21.1702, "lng": 72.8311}
        ]},
        {"name": "Haryana", "lat": 29.0588, "lng": 76.0856, "districts": [
            {"name": "Gurugram", "lat": 28.4595, "lng": 77.0266},
            {"name": "Faridabad", "lat": 28.4089, "lng": 77.3178}
        ]},
        {"name": "Himachal Pradesh", "lat": 31.1048, "lng": 77.1734, "districts": [
            {"name": "Shimla", "lat": 31.1048, "lng": 77.1734},
            {"name": "Dharamshala", "lat": 32.2190, "lng": 76.3234}
        ]},
        {"name": "Jharkhand", "lat": 23.6102, "lng": 85.2799, "districts": [
            {"name": "Ranchi", "lat": 23.3441, "lng": 85.3096},
            {"name": "Jamshedpur", "lat": 22.8046, "lng": 86.2029}
        ]},
        {"name": "Karnataka", "lat": 15.3173, "lng": 75.7139, "districts": [
            {"name": "Bengaluru", "lat": 12.9716, "lng": 77.5946},
            {"name": "Mysuru", "lat": 12.2958, "lng": 76.6394}
        ]},
        {"name": "Kerala", "lat": 10.8505, "lng": 76.2711, "districts": [
            {"name": "Wayanad", "lat": 11.6854, "lng": 76.1320},
            {"name": "Idukki", "lat": 9.8500, "lng": 76.9492},
            {"name": "Thiruvananthapuram", "lat": 8.5241, "lng": 76.9366}
        ]},
        {"name": "Madhya Pradesh", "lat": 22.9734, "lng": 78.6569, "districts": [
            {"name": "Bhopal", "lat": 23.2599, "lng": 77.4126},
            {"name": "Indore", "lat": 22.7196, "lng": 75.8577}
        ]},
        {"name": "Maharashtra", "lat": 19.7515, "lng": 75.7139, "districts": [
            {"name": "Mumbai", "lat": 19.0760, "lng": 72.8777},
            {"name": "Pune", "lat": 18.5204, "lng": 73.8567},
            {"name": "Nashik", "lat": 20.0059, "lng": 73.7900}
        ]},
        {"name": "Manipur", "lat": 24.6637, "lng": 93.9063, "districts": [
            {"name": "Imphal", "lat": 24.8174, "lng": 93.9368}
        ]},
        {"name": "Meghalaya", "lat": 25.4670, "lng": 91.3662, "districts": [
            {"name": "Shillong", "lat": 25.5788, "lng": 91.8833}
        ]},
        {"name": "Mizoram", "lat": 23.1645, "lng": 92.9376, "districts": [
            {"name": "Aizawl", "lat": 23.7307, "lng": 92.7173}
        ]},
        {"name": "Nagaland", "lat": 26.1584, "lng": 94.5624, "districts": [
            {"name": "Kohima", "lat": 25.6751, "lng": 94.1086}
        ]},
        {"name": "Odisha", "lat": 20.9517, "lng": 85.0985, "districts": [
            {"name": "Bhubaneswar", "lat": 20.2961, "lng": 85.8245},
            {"name": "Cuttack", "lat": 20.4625, "lng": 85.8830}
        ]},
        {"name": "Punjab", "lat": 31.1471, "lng": 75.3412, "districts": [
            {"name": "Amritsar", "lat": 31.6340, "lng": 74.8723},
            {"name": "Ludhiana", "lat": 30.9010, "lng": 75.8573}
        ]},
        {"name": "Rajasthan", "lat": 27.0238, "lng": 74.2179, "districts": [
            {"name": "Jaipur", "lat": 26.9124, "lng": 75.7873},
            {"name": "Udaipur", "lat": 24.5854, "lng": 73.7125}
        ]},
        {"name": "Sikkim", "lat": 27.5330, "lng": 88.5122, "districts": [
            {"name": "Gangtok", "lat": 27.3314, "lng": 88.6138}
        ]},
        {"name": "Tamil Nadu", "lat": 11.1271, "lng": 78.6569, "districts": [
            {"name": "Chennai", "lat": 13.0827, "lng": 80.2707},
            {"name": "Coimbatore", "lat": 11.0168, "lng": 76.9558}
        ]},
        {"name": "Telangana", "lat": 18.1124, "lng": 79.0193, "districts": [
            {"name": "Hyderabad", "lat": 17.3850, "lng": 78.4867},
            {"name": "Warangal", "lat": 17.9689, "lng": 79.5941}
        ]},
        {"name": "Tripura", "lat": 23.9408, "lng": 91.9882, "districts": [
            {"name": "Agartala", "lat": 23.8315, "lng": 91.2868}
        ]},
        {"name": "Uttar Pradesh", "lat": 26.8467, "lng": 80.9462, "districts": [
            {"name": "Lucknow", "lat": 26.8467, "lng": 80.9462},
            {"name": "Kanpur", "lat": 26.4499, "lng": 80.3319},
            {"name": "Meerut", "lat": 28.9845, "lng": 77.7064}
        ]},
        {"name": "Uttarakhand", "lat": 30.0668, "lng": 79.0193, "districts": [
            {"name": "Dehradun", "lat": 30.3165, "lng": 78.0322},
            {"name": "Nainital", "lat": 29.3919, "lng": 79.4542}
        ]},
        {"name": "West Bengal", "lat": 22.9868, "lng": 87.8550, "districts": [
            {"name": "Kolkata", "lat": 22.5726, "lng": 88.3639},
            {"name": "Darjeeling", "lat": 27.0410, "lng": 88.2627}
        ]}
    ]

    for state_info in states_data:
        state = Region(name=state_info["name"], level="State", lat=state_info["lat"], lng=state_info["lng"])
        db.add(state)
        db.commit() # Commit to generate state.id
        db.refresh(state)

        for dist_info in state_info["districts"]:
            district = Region(
                name=dist_info["name"], 
                level="District", 
                parent_id=state.id, 
                lat=dist_info["lat"], 
                lng=dist_info["lng"]
            )
            db.add(district)
    
    db.commit()

    # --- 2. Create Forecasts & Advisories ---
    all_regions = db.query(Region).all()
    for r in all_regions:
        parent_name = None
        if r.parent_id:
            parent = db.query(Region).filter(Region.id == r.parent_id).first()
            if parent:
                parent_name = parent.name
                
        preds = ml_predictor.predict_for_region(r.name, parent_name=parent_name)
        
        # Add Forecast
        forecast = Forecast(
            region_id=r.id,
            date=datetime.utcnow(),
            onset_prob=preds["onset_prob"],
            break_spell_risk=preds["break_spell_risk"],
            heavy_rain_prob=preds["heavy_rain_prob"],
            confidence=preds["confidence"]
        )
        db.add(forecast)

        # Add logic-based Advisory if heavy rain is highly probable
        if preds["heavy_rain_prob"] > 0.6:
            adv = Advisory(
                region_id=r.id,
                crop="All Crops",
                advisory_type="ALERT",
                title=f"Heavy Rainfall Warning in {r.name}",
                message=f"High probability ({int(preds['heavy_rain_prob']*100)}%) of extreme rain. Delay sowing and ensure proper drainage."
            )
            db.add(adv)
        elif preds["break_spell_risk"] > 0.5:
            adv = Advisory(
                region_id=r.id,
                crop="Paddy",
                advisory_type="IRRIGATION",
                title=f"Dry Spell Risk in {r.name}",
                message=f"Monsoon break spell likely. Maintain backup irrigation systems for standing crops."
            )
            db.add(adv)

    db.commit()
