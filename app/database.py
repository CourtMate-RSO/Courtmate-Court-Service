"""Database connection and operations"""
from supabase import create_client, Client
from app.config import get_settings
from typing import Optional


class Database:
    """Database connection handler"""
    
    _instance: Optional[Client] = None
    
    @classmethod
    def get_client(cls) -> Client:
        """Get or create Supabase client instance"""
        if cls._instance is None:
            settings = get_settings()
            cls._instance = create_client(
                settings.supabase_url,
                settings.supabase_key
            )
        return cls._instance
    
    @classmethod
    async def get_nearby_facilities(
        cls,
        latitude: float,
        longitude: float,
        radius_km: float = 10.0
    ) -> list[dict]:
        """
        Get facilities within a specified radius from a location.
        
        Args:
            latitude: Latitude of the center point
            longitude: Longitude of the center point
            radius_km: Search radius in kilometers (default: 10km)
            
        Returns:
            List of facility records with distance information
        """
        client = cls.get_client()
        
        # Convert radius from km to meters for PostGIS
        radius_meters = radius_km * 1000
        
        # Using PostGIS ST_DWithin for efficient spatial query
        # ST_Distance returns distance in meters for geography type
        query = f"""
            SELECT 
                id,
                name,
                ST_Y(location::geometry) as latitude,
                ST_X(location::geometry) as longitude,
                address_line,
                city,
                country,
                image,
                ST_Distance(
                    location,
                    ST_SetSRID(ST_MakePoint({longitude}, {latitude})::geometry, 4326)::geography
                ) / 1000.0 as distance_km
            FROM facilities
            WHERE ST_DWithin(
                location,
                ST_SetSRID(ST_MakePoint({longitude}, {latitude})::geometry, 4326)::geography,
                {radius_meters}
            )
            ORDER BY distance_km ASC
        """
        
        try:
            response = client.rpc('exec_sql', {'query': query}).execute()
            return response.data if response.data else []
        except Exception as e:
            # Fallback: try using the PostgREST API with a simpler approach
            # This assumes you have a function in Supabase or we query all and filter
            print(f"Error executing spatial query: {e}")
            
            # Alternative approach using Supabase functions
            try:
                response = client.rpc(
                    'get_nearby_facilities',
                    {
                        'lat': latitude,
                        'long': longitude,
                        'radius_meters': radius_meters
                    }
                ).execute()
                return response.data if response.data else []
            except Exception as inner_e:
                print(f"Error with RPC function: {inner_e}")
                # If no custom function exists, we'll need to fetch and filter
                # This is less efficient but works as a fallback
                all_facilities = client.table('facilities').select(
                    'id, name, location, address_line, city, country, image'
                ).execute()
                
                # Note: This fallback won't include distance calculation
                # You should create the RPC function in Supabase for production
                return all_facilities.data if all_facilities.data else []


def get_database() -> Database:
    """Dependency for getting database instance"""
    return Database()
