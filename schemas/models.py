from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from enum import Enum


class BusinessType(str, Enum):
    COFFEE_SHOP = "coffee_shop"
    GYM = "gym"
    SALON = "salon"
    RESTAURANT = "restaurant"
    RETAIL = "retail"


class Borough(str, Enum):
    MANHATTAN = "Manhattan"
    BROOKLYN = "Brooklyn"
    QUEENS = "Queens"
    BRONX = "Bronx"
    STATEN_ISLAND = "Staten Island"


class UserInput(BaseModel):
    business_type: BusinessType
    borough_filter: Optional[List[Borough]] = None
    weight_demand: float = Field(default=0.25, ge=0, le=1)
    weight_foot_traffic: float = Field(default=0.20, ge=0, le=1)
    weight_income: float = Field(default=0.20, ge=0, le=1)
    weight_competition: float = Field(default=0.20, ge=0, le=1)
    weight_rent: float = Field(default=0.15, ge=0, le=1)


class AnalysisPlan(BaseModel):
    business_type: str
    data_sources: List[str]
    metrics_to_compute: List[str]
    filters: Dict[str, any]


class NeighborhoodMetrics(BaseModel):
    neighborhood: str
    borough: str
    competition_count: int
    median_income: float
    population_density: float
    foot_traffic_score: float
    rent_proxy: float
    demand_score: float
    final_score: float


class DatasetInfo(BaseModel):
    source: str
    rows: int
    columns: List[str]
    date_retrieved: str


class Recommendation(BaseModel):
    best_location: str
    borough: str
    score: float
    reasoning: List[str]
    trade_offs: List[str]
    top_alternatives: List[Dict[str, any]]


class CriticFeedback(BaseModel):
    approved: bool
    issues: List[str]
    suggestions: List[str]


class FinalReport(BaseModel):
    recommendation: Recommendation
    data_sources: List[DatasetInfo]
    analysis_summary: str
    visualizations: List[str]
