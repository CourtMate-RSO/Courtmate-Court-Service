"""Data models for the Court Service"""
from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime

class LocationInput(BaseModel):
    """Input model for location-based queries"""
    latitude: float = Field(..., ge=-90, le=90, description="Latitude coordinate")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude coordinate")
    radius_km: float = Field(default=10.0, gt=0, le=20000, description="Search radius in kilometers")


class FacilityLocation(BaseModel):
    """Facility location details"""
    latitude: float
    longitude: float


from enum import Enum

class CourtBase(BaseModel):
    """Base model for Court data"""
    
    class SportType(str, Enum):
        TENNIS = "TENNIS"
        PADEL = "PADEL"
        BADMINTON = "BADMINTON"
        PICKLEBALL = "PICKLEBALL"
        SQUASH = "SQUASH"
        OTHER = "OTHER"

    name: str = Field(..., min_length=1)
    sport: str = Field(..., description="Sport type (TENNIS, PADEL, etc)")
    indoor: bool = False
    slot_minutes: int = Field(60, ge=30, le=120)
    min_duration: int = Field(60, ge=30)
    max_duration: int = Field(120, ge=30)

class CourtCreate(CourtBase):
    """Model for creating a new court"""
    pass

class CourtResponse(CourtBase):
    """Response model for court data"""
    id: UUID
    facility_id: UUID
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class FacilityResponse(BaseModel):
    """Response model for facility data"""
    id: UUID
    name: Optional[str] = None
    location: Optional[FacilityLocation] = None
    address_line: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    image: Optional[str] = None
    distance_km: Optional[float] = Field(None, description="Distance from search point in kilometers")
    courts: Optional[list[CourtResponse]] = None
    
    class Config:
        from_attributes = True


class NearbyCourtsResponse(BaseModel):
    """Response model for nearby courts query"""
    courts: list[FacilityResponse]
    total_count: int
    search_location: LocationInput


class FacilityCreate(BaseModel):
    """Model for creating a facility (location required)"""
    user_id: Optional[UUID] = None
    name: Optional[str] = None
    location: FacilityLocation
    address_line: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    image: Optional[str] = None

class FacilityUpdate(BaseModel):
    """Model for updating a facility (all fields optional)"""
    name: Optional[str] = None
    location: Optional[FacilityLocation] = None
    address_line: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    image: Optional[str] = None

class FacilityDB(FacilityResponse):
    """Representation of facility as stored in DB (includes created_at and user_id)"""
    user_id: Optional[UUID] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
