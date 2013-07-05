#!/bin/bash

# Database parameters and data directory
HOST="landobservatory.unibe.ch"
DBNAME="lokp"
USER="postgres"
LOCALUSER="lokpeditor"
DATADIR="/home/adrian/Data/GeoNames"

psql -d $DBNAME -U $USER -h $HOST -c "DROP TABLE IF EXISTS context.geonames;"
psql -d $DBNAME -U $USER -h $HOST -c "CREATE TABLE context.geonames (
    geonameid INT,
    name VARCHAR(200),
    asciiname VARCHAR(200),
    alternatenames VARCHAR(8000),
    latitude FLOAT,
    longitude FLOAT,
    fclass CHAR(1),
    fcode VARCHAR(10),
    country VARCHAR(2),
    cc2 VARCHAR(60),
    admin1 VARCHAR(20),
    admin2 VARCHAR(80),
    admin3 VARCHAR(20),
    admin4 VARCHAR(20),
    population BIGINT,
    elevation INT,
    gtopo30 INT,
    timezone VARCHAR(40),
    moddate DATE
 );"
psql -d $DBNAME -U $USER -h $HOST -c "COPY context.geonames (geonameid,name,asciiname,alternatenames,
latitude,longitude,fclass,fcode,country,cc2,
admin1,admin2,admin3,admin4,population,elevation,gtopo30,
timezone,moddate) FROM '${DATADIR}/KH/KH.txt' null as '';"
psql -d $DBNAME -U $USER -h $HOST -c "COPY context.geonames (geonameid,name,asciiname,alternatenames,
latitude,longitude,fclass,fcode,country,cc2,
admin1,admin2,admin3,admin4,population,elevation,gtopo30,
timezone,moddate) from '${DATADIR}/LA/LA.txt' null as '';"
psql -d $DBNAME -U $USER -h $HOST -c "COPY context.geonames (geonameid,name,asciiname,alternatenames,
latitude,longitude,fclass,fcode,country,cc2,
admin1,admin2,admin3,admin4,population,elevation,gtopo30,
timezone,moddate) from '${DATADIR}/MG/MG.txt' null as '';"
psql -d $DBNAME -U $USER -h $HOST -c "COPY context.geonames (geonameid,name,asciiname,alternatenames,
latitude,longitude,fclass,fcode,country,cc2,
admin1,admin2,admin3,admin4,population,elevation,gtopo30,
timezone,moddate) from '${DATADIR}/PE/PE.txt' null as '';"
psql -d $DBNAME -U $USER -h $HOST -c "COPY context.geonames (geonameid,name,asciiname,alternatenames,
latitude,longitude,fclass,fcode,country,cc2,
admin1,admin2,admin3,admin4,population,elevation,gtopo30,
timezone,moddate) from '${DATADIR}/TZ/TZ.txt' null as '';"

psql -d $DBNAME -U $USER -h $HOST -c "ALTER TABLE context.geonames ADD COLUMN id serial not null;"

# Add indexes
psql -d $DBNAME -U $USER -h $HOST -c "CREATE UNIQUE INDEX context_geonames_id ON context.geonames(id);"
psql -d $DBNAME -U $USER -h $HOST -c "CREATE INDEX context_geonames_name ON context.geonames(LOWER(name));"
psql -d $DBNAME -U $USER -h $HOST -c "CREATE INDEX context_geonames_asciiname ON context.geonames(LOWER(asciiname));"
psql -d $DBNAME -U $USER -h $HOST -c "CREATE INDEX context_geonames_alternatenames ON context.geonames(LOWER(alternatenames));"

# Add geometry column
#psql -d $DBNAME -U $USER -h $HOST -c "ALTER TABLE context.geonames ADD COLUMN wkb_geometry geometry;"
psql -d $DBNAME -U $USER -h $HOST -c "SELECT AddGeometryColumn('context', 'geonames', 'wkb_geometry', 4326, 'POINT', 2);"
psql -d $DBNAME -U $USER -h $HOST -c "UPDATE context.geonames SET wkb_geometry = ST_PointFromText('POINT(' || longitude || ' ' || latitude || ')', 4326);"

psql -d $DBNAME -U $USER -h $HOST -c "ALTER TABLE context.geonames ADD CONSTRAINT enforce_geotype_the_geom CHECK (geometrytype(wkb_geometry) = 'POINT'::text OR wkb_geometry IS NULL);"

psql -d $DBNAME -U $USER -h $HOST -c "CREATE INDEX idx_geonames_wkb_geometry ON context.geonames USING gist(wkb_geometry);"

# Change the owner to local user
psql -d $DBNAME -U $USER -h $HOST -c "ALTER TABLE context.geonames OWNER TO $LOCALUSER;"

psql -d $DBNAME -U $USER -h $HOST -c "SELECT Populate_Geometry_Columns();"