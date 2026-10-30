-- ============================================
-- NAGARPAALAN AI — PostGIS Initialization
-- ============================================
-- This script runs automatically on first database creation.
-- It enables the PostGIS spatial extension for geospatial queries.

-- Enable PostGIS extension idempotently
CREATE EXTENSION IF NOT EXISTS postgis;

-- Verify installation
SELECT PostGIS_Version();
