-- SQL function to get nearby facilities
-- Run this in your Supabase SQL Editor to enable efficient spatial queries

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

-- Grant execute permission to authenticated users
GRANT EXECUTE ON FUNCTION get_nearby_facilities TO authenticated;
GRANT EXECUTE ON FUNCTION get_nearby_facilities TO anon;
