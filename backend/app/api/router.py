from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from app.db.session import get_db
from app.models.domain import Region, Forecast, Advisory
from app.schemas.domain import RegionResponse, RegionDetailResponse, ForecastResponse, AdvisoryResponse

try:
    from inference_pipeline import run_production_inference
except ImportError:
    from backend.inference_pipeline import run_production_inference

router = APIRouter()

class ForecastPredictRequest(BaseModel):
    state: str = "Uttar Pradesh"
    prediction_date: str = "2024-06-15"
    crop_name: str = "Rice"
    growth_stage: str = "Sowing"
    soil_moisture_pct: Optional[float] = 25.0

@router.post("/forecast/predict")
def predict_forecast(req: ForecastPredictRequest):
    """
    Executes Phase 7 production inference pipeline using official Phase 3B models & Phase 6 Advisory Engine.
    """
    try:
        res = run_production_inference(
            state=req.state,
            prediction_date_str=req.prediction_date,
            crop_name=req.crop_name,
            growth_stage=req.growth_stage,
            soil_moisture_pct=req.soil_moisture_pct
        )
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/forecast/live")
def get_live_forecast(
    state: str = Query("Uttar Pradesh", description="State name"),
    prediction_date: str = Query("2024-06-15", description="Prediction date (YYYY-MM-DD)"),
    crop_name: str = Query("Rice", description="Crop name"),
    growth_stage: str = Query("Sowing", description="Growth stage"),
    soil_moisture_pct: Optional[float] = Query(25.0, description="Soil moisture percentage")
):
    """
    GET endpoint executing live production inference for dashboard widgets.
    """
    try:
        res = run_production_inference(
            state=state,
            prediction_date_str=prediction_date,
            crop_name=crop_name,
            growth_stage=growth_stage,
            soil_moisture_pct=soil_moisture_pct
        )
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/regions", response_model=List[RegionDetailResponse])
def get_all_regions(db: Session = Depends(get_db)):
    """Fetch all geographic regions (States, Districts, etc.)"""
    return db.query(Region).all()

@router.get("/regions/{region_id}", response_model=RegionDetailResponse)
def get_region_details(region_id: int, db: Session = Depends(get_db)):
    """Fetch a specific region along with its forecasts and advisories"""
    region = db.query(Region).filter(Region.id == region_id).first()
    if not region:
        raise HTTPException(status_code=404, detail="Region not found")
    return region

@router.get("/forecast/map", response_model=List[ForecastResponse])
def get_map_forecasts(db: Session = Depends(get_db)):
    """Fetch the latest forecasts for all regions to populate the Map pins"""
    return db.query(Forecast).all()

@router.get("/advisories", response_model=List[AdvisoryResponse])
def get_active_advisories(db: Session = Depends(get_db)):
    """Fetch all active advisories, sorted by newest first"""
    return db.query(Advisory).order_by(Advisory.created_at.desc()).all()
