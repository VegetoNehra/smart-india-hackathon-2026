from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime

# --- FORECAST SCHEMAS ---
class ForecastBase(BaseModel):
    onset_prob: float
    break_spell_risk: float
    heavy_rain_prob: float
    confidence: float
    date: datetime

class ForecastCreate(ForecastBase):
    pass

class ForecastResponse(ForecastBase):
    id: int
    region_id: int
    
    model_config = ConfigDict(from_attributes=True)

# --- ADVISORY SCHEMAS ---
class AdvisoryBase(BaseModel):
    crop: str
    advisory_type: str
    title: str
    message: str
    created_at: datetime

class AdvisoryCreate(AdvisoryBase):
    pass

class AdvisoryResponse(AdvisoryBase):
    id: int
    region_id: int
    
    model_config = ConfigDict(from_attributes=True)

# --- REGION SCHEMAS ---
class RegionBase(BaseModel):
    name: str
    level: str
    lat: Optional[float] = None
    lng: Optional[float] = None
    parent_id: Optional[int] = None

class RegionCreate(RegionBase):
    pass

class RegionResponse(RegionBase):
    id: int
    # We might not want to always return full nested children/forecasts depending on the endpoint, 
    # but for simple hierarchical queries, this works.
    
    model_config = ConfigDict(from_attributes=True)

# A detailed region response that includes forecasts and advisories (e.g. for a dashboard view)
class RegionDetailResponse(RegionResponse):
    forecasts: List[ForecastResponse] = []
    advisories: List[AdvisoryResponse] = []
