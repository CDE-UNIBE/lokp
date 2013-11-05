ALTER TABLE data.activities
DROP CONSTRAINT enforce_geotype_point,
ADD CONSTRAINT enforce_geotype_point CHECK (geometrytype(point) = 'POINT'::text OR geometrytype(point) = 'MULTIPOINT'::text OR point IS NULL);