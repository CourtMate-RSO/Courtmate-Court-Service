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
        # Use admin client to bypass RLS and ensure we can read all courts
        supabase = admin_supabase_client()
        
        facility_id_str = str(facility_id)
        logger.info(f"Fetching courts for facility {facility_id_str}")
        
        response = supabase.table("courts").select("*").eq("facility_id", facility_id_str).execute()
        
        logger.info(f"Query returned {len(response.data) if response.data else 0} courts")
        
        if not response.data:
            logger.info(f"No courts found for facility {facility_id_str}")
            return []
        
        courts = []
        for court in response.data:
            logger.info(f"Processing court: {court.get('id')} for facility {facility_id_str}")
            courts.append(CourtResponse(**court))
        
        logger.info(f"Successfully returned {len(courts)} courts for facility {facility_id_str}")
        return courts
        
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
        # Use admin client to bypass RLS and ensure we can read all facilities
        supabase = admin_supabase_client()
        
        current_user_str = str(user_id)
        logger.info(f"Fetching facilities for user {current_user_str}")
        
        # Query facilities table directly with user_id filter
        response = supabase.table("facilities").select("*").eq("user_id", current_user_str).execute()
        
        logger.info(f"Direct query returned {len(response.data) if response.data else 0} facilities")
        
        if not response.data:
            logger.info(f"No facilities found for user {current_user_str}")
            return []
        
        user_facilities = []
        
        for facility in response.data:
            facility_id = facility.get('id')
            location_geom = facility.get('location')
            
            logger.info(f"Processing facility {facility_id}: location type={type(location_geom)}")
            
            try:
                # Extract latitude and longitude from PostGIS geometry
                # location is stored as geography/geometry in WKB or GeoJSON format
                if location_geom:
                    # Handle different geometry formats
                    if isinstance(location_geom, dict):
                        # GeoJSON format
                        coords = location_geom.get('coordinates', [0, 0])
                        latitude = coords[1] if len(coords) > 1 else 0
                        longitude = coords[0] if len(coords) > 0 else 0
                    else:
                        # WKB format - extract using PostGIS function
                        # For now, use 0,0 as fallback and let client handle
                        latitude = 0
                        longitude = 0
                        logger.warning(f"Could not parse geometry for {facility_id}: {location_geom}")
                else:
                    latitude = 0
                    longitude = 0
                
                location_obj = FacilityLocation(
                    latitude=latitude,
                    longitude=longitude
                )
                
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
                
                logger.info(f"✓ Added facility {facility_id} to results")
                
            except Exception as e:
                logger.error(f"Error processing facility {facility_id}: {str(e)}")
                continue
        
        logger.info(f"Found {len(user_facilities)} facilities for user {current_user_str}")
        return user_facilities

    except Exception as e:
        logger.error(f"Error fetching user facilities: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching user facilities: {str(e)}"
        )
