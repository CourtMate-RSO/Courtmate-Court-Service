"""API routes for the Court Service"""
from fastapi import APIRouter, HTTPException, status, Depends
from app.models import LocationInput, NearbyCourtsResponse, FacilityResponse, FacilityLocation
from app.database import Database, get_database
from typing import List

router = APIRouter(tags=["facilities"])


@router.post("/nearby", response_model=NearbyCourtsResponse, status_code=status.HTTP_200_OK)
async def get_nearby_courts(
    location: LocationInput,
    db: Database = Depends(get_database)
) -> NearbyCourtsResponse:
    """
    Get courts within a specified radius from the given location.
    
    Args:
        location: Location input with latitude, longitude, and optional radius
        
    Returns:
        List of nearby courts with their details and distances
        
    Raises:
        HTTPException: If there's an error fetching the data
    """
    try:
        # Fetch nearby facilities from database
        facilities_data = await db.get_nearby_facilities(
            latitude=location.latitude,
            longitude=location.longitude,
            radius_km=location.radius_km
        )
        
        # Transform data to response model
        courts = []
        for facility in facilities_data:
            # Handle location data
            facility_location = None
            if 'latitude' in facility and 'longitude' in facility:
                facility_location = FacilityLocation(
                    latitude=facility['latitude'],
                    longitude=facility['longitude']
                )
            
            court = FacilityResponse(
                id=facility['id'],
                name=facility.get('name'),
                location=facility_location,
                address_line=facility.get('address_line'),
                city=facility.get('city'),
                country=facility.get('country'),
                image=facility.get('image'),
                distance_km=facility.get('distance_km')
            )
            courts.append(court)
        
        return NearbyCourtsResponse(
            courts=courts,
            total_count=len(courts),
            search_location=location
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching nearby courts: {str(e)}"
        )


@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "court-service"
    }
