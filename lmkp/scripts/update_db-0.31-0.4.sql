BEGIN;
-- Create a new table for files
CREATE TABLE data.files
(
    id serial NOT NULL,
    identifier uuid NOT NULL,
    name character varying(511) NOT NULL,
    mime character varying(255) NOT NULL,
    size integer,
    hash character varying(255),
    CONSTRAINT files_pkey PRIMARY KEY (id )
)
WITH (
  OIDS=FALSE
);
ALTER TABLE data.files OWNER TO lmkpeditor;

-- Add new columns to table user
-- Add a column for the registration timestamp
ALTER TABLE data.users ADD COLUMN registration_timestamp timestamp with time zone;
-- Set an imaginary registration date for all approved and active users
UPDATE data.users SET registration_timestamp = '2001-01-01 01:01:01+01' WHERE registration_timestamp IS NULL;
-- Set this column not null
ALTER TABLE data.users ALTER COLUMN registration_timestamp SET NOT NULL;

-- Add a new column is_active and set the default value to false
ALTER TABLE data.users ADD COLUMN is_active boolean NOT NULL DEFAULT FALSE;
-- Set all existing users active
UPDATE data.users SET is_active = TRUE;
-- Add a new column activation_uuid
ALTER TABLE data.users ADD COLUMN activation_uuid uuid;
-- Add a new column is_approved and set the default value to false
ALTER TABLE data.users ADD COLUMN is_approved boolean NOT NULL DEFAULT FALSE;
-- Set all existing users approved
UPDATE data.users SET is_approved = TRUE;
-- Add an additional constraint to prevent inactive users without an activation uuid
ALTER TABLE data.users ADD CONSTRAINT data_users_activation_uuid_not_null CHECK ((is_active = FALSE) = (activation_uuid IS NOT NULL));

COMMIT;