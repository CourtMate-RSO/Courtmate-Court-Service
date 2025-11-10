-- Insert 10 test courts in Ljubljana, Slovenia
-- 8 courts within 10km radius, 2 courts beyond 10km radius
-- Center point: 46.052752141747376, 14.49548414351014

-- Note: You may need to replace 'user_id_here' with an actual UUID from your users_data table
-- or remove the user_id field if it's nullable and you want to keep it NULL

INSERT INTO public.facilities (user_id, name, location, address_line, city, country, image) VALUES

-- Courts within 10km radius (8 courts)

-- Court 1: ~2km north (Šiška area)
(
  NULL,
  'test_court_siska',
  ST_SetSRID(ST_MakePoint(14.4950, 46.0700), 4326)::geography,
  'Celovška cesta 123',
  'Ljubljana',
  'Slovenia',
  NULL
),

-- Court 2: ~3km east (Moste area)
(
  NULL,
  'test_court_moste',
  ST_SetSRID(ST_MakePoint(14.5450, 46.0550), 4326)::geography,
  'Smartinska cesta 45',
  'Ljubljana',
  'Slovenia',
  NULL
),

-- Court 3: ~4km south (Rudnik area)
(
  NULL,
  'test_court_rudnik',
  ST_SetSRID(ST_MakePoint(14.4800, 46.0200), 4326)::geography,
  'Dolenjska cesta 78',
  'Ljubljana',
  'Slovenia',
  NULL
),

-- Court 4: ~2.5km west (Rožnik area)
(
  NULL,
  'test_court_roznik',
  ST_SetSRID(ST_MakePoint(14.4700, 46.0600), 4326)::geography,
  'Tržaška cesta 56',
  'Ljubljana',
  'Slovenia',
  NULL
),

-- Court 5: ~5km northeast (Črnuče area)
(
  NULL,
  'test_court_crnuce',
  ST_SetSRID(ST_MakePoint(14.5500, 46.0850), 4326)::geography,
  'Dunajska cesta 234',
  'Ljubljana',
  'Slovenia',
  NULL
),

-- Court 6: ~1.5km center (close to main point)
(
  NULL,
  'test_court_center',
  ST_SetSRID(ST_MakePoint(14.5050, 46.0550), 4326)::geography,
  'Slovenska cesta 12',
  'Ljubljana',
  'Slovenia',
  NULL
),

-- Court 7: ~6km southeast (Šmartno area)
(
  NULL,
  'test_court_smartno',
  ST_SetSRID(ST_MakePoint(14.5700, 46.0300), 4326)::geography,
  'Kajuhova ulica 90',
  'Ljubljana',
  'Slovenia',
  NULL
),

-- Court 8: ~7km northwest (Medvode direction)
(
  NULL,
  'test_court_medvode_direction',
  ST_SetSRID(ST_MakePoint(14.4200, 46.1000), 4326)::geography,
  'Gorenjska cesta 188',
  'Ljubljana',
  'Slovenia',
  NULL
),

-- Courts beyond 10km radius (2 courts)

-- Court 9: ~15km north (Vodice area)
(
  NULL,
  'test_court_vodice_far',
  ST_SetSRID(ST_MakePoint(14.4900, 46.1900), 4326)::geography,
  'Vodice naselje 45',
  'Ljubljana',
  'Slovenia',
  NULL
),

-- Court 10: ~18km southeast (Grosuplje direction)
(
  NULL,
  'test_court_grosuplje_far',
  ST_SetSRID(ST_MakePoint(14.6500, 45.9000), 4326)::geography,
  'Ljubljanska cesta 156',
  'Ljubljana',
  'Slovenia',
  NULL
);

-- Verify the inserted data with distances from center point
SELECT 
    name,
    address_line,
    ST_Y(location::geometry) as latitude,
    ST_X(location::geometry) as longitude,
    ROUND(
        ST_Distance(
            location,
            ST_SetSRID(ST_MakePoint(14.49548414351014, 46.052752141747376)::geometry, 4326)::geography
        ) / 1000.0,
        2
    ) as distance_km
FROM facilities
WHERE name LIKE 'test_%'
ORDER BY distance_km;
