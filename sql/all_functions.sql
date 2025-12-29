-- Complete set of SQL functions for Court Service
-- Run this in your Supabase SQL Editor

-- Function 1: Get nearby facilities
CREATE OR REPLACE FUNCTION get_nearby_facilities(
    lat double precision,
    long double precision,
    radius_meters double precision DEFAULT 10000
)
RETURNS TABLE (
    id uuid,
    name text,
    latitude double precision,
    longitude double precision,
    address_line text,
    city text,
    country text,
    image text,
    distance_km double precision
) 
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        f.id,
        f.name,
        ST_Y(f.location::geometry) as latitude,
        ST_X(f.location::geometry) as longitude,
        f.address_line,
        f.city,
        f.country,
        f.image,
        ST_Distance(
            f.location,
            ST_SetSRID(ST_MakePoint(long, lat)::geometry, 4326)::geography
        ) / 1000.0 as distance_km
    FROM facilities f
    WHERE ST_DWithin(
        f.location,
        ST_SetSRID(ST_MakePoint(long, lat)::geometry, 4326)::geography,
        radius_meters
    )
    ORDER BY distance_km ASC;
END;
$$;

-- Function 2: Get all facilities with extracted lat/lng
CREATE OR REPLACE FUNCTION get_all_facilities()
RETURNS TABLE (
    id uuid,
    name text,
    latitude double precision,
    longitude double precision,
    address_line text,
    city text,
    country text,
    image text,
    user_id uuid,
    created_at timestamptz
) 
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        f.id,
        f.name,
        ST_Y(f.location::geometry) as latitude,
        ST_X(f.location::geometry) as longitude,
        f.address_line,
        f.city,
        f.country,
        f.image,
        f.user_id,
        f.created_at
    FROM facilities f
    ORDER BY f.created_at DESC;
END;
$$;

-- Function 3: Get facility by ID with extracted lat/lng
CREATE OR REPLACE FUNCTION get_facility_location(facility_id uuid)
RETURNS TABLE (
    id uuid,
    name text,
    latitude double precision,
    longitude double precision,
    address_line text,
    city text,
    country text,
    image text,
    user_id uuid,
    created_at timestamptz
) 
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        f.id,
        f.name,
        ST_Y(f.location::geometry) as latitude,
        ST_X(f.location::geometry) as longitude,
        f.address_line,
        f.city,
        f.country,
        f.image,
        f.user_id,
        f.created_at
    FROM facilities f
    WHERE f.id = facility_id;
END;
$$;

-- Grant execute permissions to all roles
GRANT EXECUTE ON FUNCTION get_nearby_facilities TO authenticated;
GRANT EXECUTE ON FUNCTION get_nearby_facilities TO anon;
GRANT EXECUTE ON FUNCTION get_all_facilities TO authenticated;
GRANT EXECUTE ON FUNCTION get_all_facilities TO anon;
GRANT EXECUTE ON FUNCTION get_facility_location TO authenticated;
GRANT EXECUTE ON FUNCTION get_facility_location TO anon;

-- Verify functions were created
SELECT routine_name, routine_type
FROM information_schema.routines 
WHERE routine_schema = 'public' 
  AND routine_name IN ('get_nearby_facilities', 'get_all_facilities', 'get_facility_location')
ORDER BY routine_name;
