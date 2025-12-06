"""API routes for the Court Service"""
from fastapi import APIRouter, HTTPException, status, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.models import (
    LocationInput, 
    NearbyCourtsResponse, 
    FacilityResponse, 
    FacilityLocation,
    FacilityCreate,
    FacilityDB
)
from typing import List
from uuid import UUID
from app.supabase_client import anon_supabase_client, admin_supabase_client
import logging

logger = logging.getLogger(__name__)

router = APIRouter(tags=["facilities"])


@router.post("/nearby", response_model=NearbyCourtsResponse, status_code=status.HTTP_200_OK)
async def get_nearby_courts(location: LocationInput):
    """
    Get courts within a specified radius from the given location.
    
    Uses PostGIS to calculate distance and returns facilities sorted by distance.
    """
    try:
        supabase = anon_supabase_client()
        
        # Use the RPC function to get nearby facilities
        # Note: function expects 'long' not 'lng', and radius_meters not radius_km
        response = supabase.rpc(
            'get_nearby_facilities',
            {
                'lat': location.latitude,
                'long': location.longitude,
                'radius_meters': location.radius_km * 1000  # Convert km to meters
            }
        ).execute()
        
        # Transform data to response model
        courts = []
        for facility in response.data:
            # Parse location
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
        logger.error(f"Error fetching nearby courts: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching nearby courts: {str(e)}"
        )


@router.post("/", response_model=FacilityDB, status_code=status.HTTP_201_CREATED)
async def create_facility(facility: FacilityCreate):
    """
    Create a new facility in the database.
    """
    try:
        # Use admin client to bypass RLS for facility creation
        supabase = admin_supabase_client()
        
        # Create PostGIS POINT - format: POINT(longitude latitude)
        # Note: longitude comes FIRST in PostGIS!
        location_wkt = f"POINT({facility.location.longitude} {facility.location.latitude})"
        
        # Prepare facility data with PostGIS point
        facility_data = {
            "name": facility.name,
            "location": location_wkt,  # Use geography column
            "address_line": facility.address_line,
            "city": facility.city,
            "country": facility.country,
            "image": facility.image,
        }
        
        # Add user_id if provided
        if facility.user_id:
            facility_data["user_id"] = str(facility.user_id)
        
        # Insert facility into database
        response = supabase.table("facilities").insert(facility_data).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create facility"
            )
        
        created_facility = response.data[0]
        
        # Build location object for response
        location_obj = FacilityLocation(
            latitude=facility.location.latitude,
            longitude=facility.location.longitude
        )
        
        return FacilityDB(
            id=created_facility['id'],
            name=created_facility.get('name'),
            location=location_obj,
            address_line=created_facility.get('address_line'),
            city=created_facility.get('city'),
            country=created_facility.get('country'),
            image=created_facility.get('image'),
            user_id=created_facility.get('user_id'),
            created_at=created_facility.get('created_at')
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating facility: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating facility: {str(e)}"
        )


@router.get("/{facility_id}", response_model=FacilityDB, status_code=status.HTTP_200_OK)
async def get_facility(facility_id: UUID):
    """
    Get a facility by ID.
    """
    try:
        logger.info(f"Fetching facility with ID: {facility_id}")
        supabase = anon_supabase_client()
        
        # Get location using RPC function that extracts lat/lng
        response = supabase.rpc(
            'get_facility_location',
            {'facility_id': str(facility_id)}
        ).execute()
        
        if not response.data or len(response.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Facility with id {facility_id} not found"
            )
        
        loc_data = response.data[0]
        
        # Build location object
        location_obj = FacilityLocation(
            latitude=loc_data['latitude'],
            longitude=loc_data['longitude']
        )
        
        return FacilityDB(
            id=loc_data['id'],
            name=loc_data.get('name'),
            location=location_obj,
            address_line=loc_data.get('address_line'),
            city=loc_data.get('city'),
            country=loc_data.get('country'),
            image=loc_data.get('image'),
            user_id=loc_data.get('user_id'),
            created_at=loc_data.get('created_at')
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching facility {facility_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/", response_model=List[FacilityDB], status_code=status.HTTP_200_OK)
async def list_facilities():
    """
    Get all facilities.
    
    Returns:
        List of all facilities
    """
    try:
        supabase = anon_supabase_client()
        
        # Use RPC function to get all facilities with extracted lat/lng
        response = supabase.rpc('get_all_facilities').execute()
        
        facilities = []
        for facility in response.data:
            # Build location object
            location_obj = FacilityLocation(
                latitude=facility['latitude'],
                longitude=facility['longitude']
            )
            
            facilities.append(FacilityDB(
                id=facility['id'],
                name=facility.get('name'),
                location=location_obj,
                address_line=facility.get('address_line'),
                city=facility.get('city'),
                country=facility.get('country'),
                image=facility.get('image'),
                user_id=facility.get('user_id'),
                created_at=facility.get('created_at')
            ))
        
        return facilities
        
    except Exception as e:
        logger.error(f"Error fetching facilities: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching facilities: {str(e)}"
        )


@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """
    Comprehensive health check endpoint.
    Checks database connectivity and service status.
    """
    health_status = {
        "status": "healthy",
        "service": "court-service",
        "checks": {
            "database": "unknown",
            "api": "healthy"
        }
    }
    
    try:
        # Test database connection by trying to fetch count
        supabase = anon_supabase_client()
        
        # Simple query to test connection
        response = supabase.table("facilities").select("id", count="exact").limit(1).execute()
        
        health_status["checks"]["database"] = "healthy"
        logger.info("Health check passed - database connected")
        
    except Exception as e:
        logger.error(f"Health check failed - database error: {str(e)}")
        health_status["status"] = "unhealthy"
        health_status["checks"]["database"] = f"error: {str(e)}"
        
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=health_status
        )
    
    return health_status


from app.models import CourtCreate, CourtResponse

@router.post("/{facility_id}/courts", response_model=CourtResponse, status_code=status.HTTP_201_CREATED)
async def create_court(facility_id: UUID, court: CourtCreate):
    """
    Add a new court to a facility.
    """
    try:
        supabase = admin_supabase_client()
        
        # Verify facility exists
        facility_check = supabase.table("facilities").select("id").eq("id", str(facility_id)).execute()
        if not facility_check.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f"Facility {facility_id} not found"
            )

        court_data = {
            "facility_id": str(facility_id),
            "name": court.name,
            "sport": court.sport,
            "indoor": court.indoor,
            "slot_minutes": court.slot_minutes,
            "min_duration": court.min_duration,
            "max_duration": court.max_duration
        }
        
        response = supabase.table("courts").insert(court_data).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create court"
            )
            
        created_court = response.data[0]
        return CourtResponse(**created_court)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating court: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating court: {str(e)}"
        )

@router.get("/{facility_id}/courts", response_model=List[CourtResponse], status_code=status.HTTP_200_OK)
async def get_facility_courts(facility_id: UUID):
    """
    Get all courts for a specific facility.
    """
    try:
        supabase = anon_supabase_client()
        
        response = supabase.table("courts").select("*").eq("facility_id", str(facility_id)).execute()
        
        return [CourtResponse(**court) for court in response.data]
        
    except Exception as e:
        logger.error(f"Error fetching courts for facility {facility_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching courts: {str(e)}"
        )

@router.get("/user/{user_id}", response_model=List[FacilityDB], status_code=status.HTTP_200_OK)
async def get_user_facilities(user_id: UUID):
    """
    Get all facilities managed by a specific user.
    """
    try:
        supabase = anon_supabase_client()
        
        # We need to get facilities and convert geography to lat/long
        # Since we can't easily do ST_X/ST_Y on a simple select, we might need a custom RPC or 
        # just select the raw column and hope our client handles it, 
        # BUT our models expect 'location' as object.
        # Let's use the same approach as list_facilities but filter in python or 
        # ideally use a query that supports filtering.
        # For now, let's use the 'get_all_facilities' RPC and filter by user_id if possible,
        # or just simple select if we can parse the location.
        
        # To keep it consistent and efficient, let's just query the table and parse the location manually if needed,
        # OR use a specific RPC for this if performance matters. 
        # Given the project state, let's try direct query and see if we can extract location.
        # Actually, the existing pattern uses RPC 'get_all_facilities' which returns lat/long. 
        # Let's see if we can filter that. 
        # If not, let's create a new RPC or use client side filtering (not ideal for large datasets).
        
        # BETTER APPROACH: Use the same pattern as get_facility but with a where clause?
        # Supabase-py doesn't support complex postgis parsing in simple select easily without view/rpc.
        
        # Let's try to finding if there's a way to filter the existing RPC? No.
        # Let's try to select and rely on a helper to parse or just `get_all_facilities` and filter in memory (MVP approach).
        
        response = supabase.rpc('get_all_facilities').execute()
        
        current_user_str = str(user_id)
        user_facilities = []
        
        for facility in response.data:
            if facility.get('user_id') == current_user_str:
                location_obj = FacilityLocation(
                    latitude=facility['latitude'],
                    longitude=facility['longitude']
                )
                
                # Fetch courts for this facility to be complete? 
                # The prompt asked for "endpoint to get facilities", usually implies list view.
                # Detailed view including courts can be fetched via get_facility_courts.
                
                user_facilities.append(FacilityDB(
                    id=facility['id'],
                    name=facility.get('name'),
                    location=location_obj,
                    address_line=facility.get('address_line'),
                    city=facility.get('city'),
                    country=facility.get('country'),
                    image=facility.get('image'),
                    user_id=facility.get('user_id'),
                    created_at=facility.get('created_at')
                ))
                
        return user_facilities

    except Exception as e:
        logger.error(f"Error fetching user facilities: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching user facilities: {str(e)}"
        )
