/*
  *** IMPORTANT *** Make sure that the id's of the keys and values correspond to
    the ones defined in the populate script. These are the same as they are on
    the productive database version as of 2013-05-19.

  Use this script to update a database of version 0.4.

  It adds a table Categories and adds new columns to A_Keys, A_Values, SH_Keys
  and SH_Values.

  Last update: 2013-05-19 14:06
*/

CREATE TABLE data.categories
(
  id serial NOT NULL,
  name character varying(511) NOT NULL,
  "type" character varying(255) NOT NULL,
  fk_language integer NOT NULL,
  description text,
  fk_category integer,
  CONSTRAINT categories_pkey PRIMARY KEY (id ),
  CONSTRAINT categories_fk_category_fkey FOREIGN KEY (fk_category)
      REFERENCES data.categories (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION,
  CONSTRAINT categories_fk_language_fkey FOREIGN KEY (fk_language)
      REFERENCES data.languages (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION
)
WITH (
  OIDS=FALSE
);

INSERT INTO data.categories(id, name, type, fk_language, description, fk_category) VALUES
  (1, 'Spatial Data', 'activities', 1, NULL, NULL),
  (2, 'General Information', 'activities', 1, NULL, NULL),
  (3, 'Employment', 'activities', 1, NULL, NULL),
  (4, 'Investor Info', 'activities', 1, NULL, NULL),
  (5, 'Data Sources', 'activities', 1, NULL, NULL),
  (6, 'Local Communities', 'activities', 1, NULL, NULL),
  (7, 'Former Use', 'activities', 1, NULL, NULL),
  (8, 'Produce Info', 'activities', 1, NULL, NULL),
  (9, 'Water', 'activities', 1, NULL, NULL),
  (10, 'Overall Comment', 'activities', 1, NULL, NULL),
  (11, 'Location', 'activities', 1, NULL, NULL),
  (12, 'Land Area', 'activities', 1, NULL, NULL),
  (13, 'Intention of Investment', 'activities', 1, NULL, NULL),
  (14, 'Nature of the Deal', 'activities', 1, NULL, NULL),
  (15, 'Negotiation Status', 'activities', 1, NULL, NULL),
  (16, 'Duration of the Agreement', 'activities', 1, NULL, NULL),
  (17, 'Implementation Status', 'activities', 1, NULL, NULL),
  (18, 'Purchase Price', 'activities', 1, NULL, NULL),
  (19, 'Leasing Fees', 'activities', 1, NULL, NULL),
  (20, 'Contract Farming', 'activities', 1, NULL, NULL),
  (21, 'Number of Jobs Created', 'activities', 1, NULL, NULL),
  (22, 'Primary Investor', 'activities', 1, NULL, NULL),
  (23, 'Secondary Investors', 'activities', 1, NULL, NULL),
  (24, 'Data Source', 'activities', 1, NULL, NULL),
  (25, 'How did Community React?', 'activities', 1, NULL, NULL),
  (26, 'Consultation of Local Community', 'activities', 1, NULL, NULL),
  (27, 'Promised or Received Compensation', 'activities', 1, NULL, NULL),
  (28, 'Benefits for Local Communities', 'activities', 1, NULL, NULL),
  (29, 'Number of People Actually Displaced', 'activities', 1, NULL, NULL),
  (30, 'Former Land Owner', 'activities', 1, NULL, NULL),
  (31, 'Former Land Use', 'activities', 1, NULL, NULL),
  (32, 'Former Land Cover', 'activities', 1, NULL, NULL),
  (33, 'Detailed Crop, Animal and Mineral Information', 'activities', 1, NULL, NULL),
  (34, 'Use of Produce', 'activities', 1, NULL, NULL),
  (35, 'Water Extraction Envisaged', 'activities', 1, NULL, NULL),
  (36, 'Source of Water Extraction', 'activities', 1, NULL, NULL),
  (37, 'How Much do Investors Pay for Water and the Use of Water Infrastruture?', 'activities', 1, NULL, NULL),
  (38, 'How Much Water Is Extracted?', 'activities', 1, NULL, NULL),
  (39, 'Overall Comment', 'activities', 1, NULL, NULL)
;

ALTER TABLE data.a_keys ADD COLUMN "type" character varying(255) NOT NULL DEFAULT 'string';
ALTER TABLE data.a_keys ADD COLUMN helptext text;
ALTER TABLE data.a_keys ADD COLUMN description text;
ALTER TABLE data.a_keys ADD COLUMN validator text;

ALTER TABLE data.sh_keys ADD COLUMN "type" character varying(255) NOT NULL DEFAULT 'string';
ALTER TABLE data.sh_keys ADD COLUMN helptext text;
ALTER TABLE data.sh_keys ADD COLUMN description text;
ALTER TABLE data.sh_keys ADD COLUMN validator text;

ALTER TABLE data.a_values ADD COLUMN fk_a_key integer;
ALTER TABLE data.a_values ADD COLUMN "order" integer;
ALTER TABLE data.a_values ADD CONSTRAINT a_values_fk_a_key_fkey FOREIGN KEY (fk_a_key)
  REFERENCES data.a_keys (id) MATCH SIMPLE
  ON UPDATE NO ACTION ON DELETE NO ACTION;

ALTER TABLE data.sh_values ADD COLUMN fk_sh_key integer;
ALTER TABLE data.sh_values ADD COLUMN "order" integer;
ALTER TABLE data.sh_values ADD CONSTRAINT sh_values_fk_sh_key_fkey FOREIGN KEY (fk_sh_key)
  REFERENCES data.sh_keys (id) MATCH SIMPLE
  ON UPDATE NO ACTION ON DELETE NO ACTION;

UPDATE data.a_keys SET "type" = 'Dropdown', helptext = NULL, description = NULL, validator = NULL WHERE id=1;
UPDATE data.a_keys SET "type" = 'Dropdown', helptext = NULL, description = NULL, validator = NULL WHERE id=2;
UPDATE data.a_keys SET "type" = 'Dropdown', helptext = NULL, description = NULL, validator = NULL WHERE id=3;
UPDATE data.a_keys SET "type" = 'Dropdown', helptext = NULL, description = NULL, validator = NULL WHERE id=4;
UPDATE data.a_keys SET "type" = 'Number', helptext = 'ha', description = NULL, validator = '[0]' WHERE id=5;
UPDATE data.a_keys SET "type" = 'Checkbox', helptext = NULL, description = NULL, validator = NULL WHERE id=6;
UPDATE data.a_keys SET "type" = 'Integer', helptext = 'years', description = NULL, validator = '[0]' WHERE id=7;
UPDATE data.a_keys SET "type" = 'Dropdown', helptext = NULL, description = NULL, validator = NULL WHERE id=8;
UPDATE data.a_keys SET "type" = 'Checkbox', helptext = NULL, description = NULL, validator = NULL WHERE id=9;
UPDATE data.a_keys SET "type" = 'String', helptext = NULL, description = NULL, validator = NULL WHERE id=10;
UPDATE data.a_keys SET "type" = 'Dropdown', helptext = NULL, description = NULL, validator = NULL WHERE id=11;
UPDATE data.a_keys SET "type" = 'Integer', helptext = NULL, description = NULL, validator = '[0,100]' WHERE id=12;
UPDATE data.a_keys SET "type" = 'Checkbox', helptext = NULL, description = NULL, validator = NULL WHERE id=13;
UPDATE data.a_keys SET "type" = 'Number', helptext = NULL, description = NULL, validator = NULL WHERE id=14;
UPDATE data.a_keys SET "type" = 'Number', helptext = 'ha', description = NULL, validator = '[0]' WHERE id=15;
UPDATE data.a_keys SET "type" = 'String', helptext = NULL, description = NULL, validator = NULL WHERE id=16;
UPDATE data.a_keys SET "type" = 'String', helptext = NULL, description = NULL, validator = NULL WHERE id=17;
UPDATE data.a_keys SET "type" = 'Integer', helptext = NULL, description = NULL, validator = '[0]' WHERE id=18;
UPDATE data.a_keys SET "type" = 'Integer', helptext = NULL, description = NULL, validator = '[0]' WHERE id=19;
UPDATE data.a_keys SET "type" = 'Date', helptext = NULL, description = NULL, validator = NULL WHERE id=20;
UPDATE data.a_keys SET "type" = 'Integer', helptext = NULL, description = NULL, validator = NULL WHERE id=21;
UPDATE data.a_keys SET "type" = 'String', helptext = 'per year', description = NULL, validator = NULL WHERE id=22;
UPDATE data.a_keys SET "type" = 'Integer', helptext = NULL, description = NULL, validator = '[0]' WHERE id=23;
UPDATE data.a_keys SET "type" = 'Number', helptext = 'm3/year', description = NULL, validator = '[0]' WHERE id=24;
UPDATE data.a_keys SET "type" = 'Text', helptext = NULL, description = NULL, validator = NULL WHERE id=25;
UPDATE data.a_keys SET "type" = 'Checkbox', helptext = NULL, description = NULL, validator = NULL WHERE id=26;
UPDATE data.a_keys SET "type" = 'String', helptext = NULL, description = NULL, validator = NULL WHERE id=27;
UPDATE data.a_keys SET "type" = 'Dropdown', helptext = NULL, description = NULL, validator = NULL WHERE id=28;
UPDATE data.a_keys SET "type" = 'Text', helptext = NULL, description = NULL, validator = NULL WHERE id=29;
UPDATE data.a_keys SET "type" = 'Number', helptext = NULL, description = NULL, validator = NULL WHERE id=30;
UPDATE data.a_keys SET "type" = 'Number', helptext = 'ha', description = NULL, validator = '[0]' WHERE id=31;
UPDATE data.a_keys SET "type" = 'Number', helptext = 'ha', description = NULL, validator = '[0]' WHERE id=32;
UPDATE data.a_keys SET "type" = 'Checkbox', helptext = NULL, description = NULL, validator = NULL WHERE id=33;
UPDATE data.a_keys SET "type" = 'Number', helptext = 'ha', description = NULL, validator = '[0]' WHERE id=34;
UPDATE data.a_keys SET "type" = 'Checkbox', helptext = NULL, description = NULL, validator = NULL WHERE id=35;
UPDATE data.a_keys SET "type" = 'Checkbox', helptext = NULL, description = NULL, validator = NULL WHERE id=36;
UPDATE data.a_keys SET "type" = 'Integer', helptext = NULL, description = NULL, validator = '[0]' WHERE id=37;
UPDATE data.a_keys SET "type" = 'Number', helptext = 'ha', description = NULL, validator = '[0]' WHERE id=38;
UPDATE data.a_keys SET "type" = 'Checkbox', helptext = NULL, description = NULL, validator = NULL WHERE id=39;
UPDATE data.a_keys SET "type" = 'Integer', helptext = NULL, description = NULL, validator = '[0]' WHERE id=40;
UPDATE data.a_keys SET "type" = 'String', helptext = NULL, description = NULL, validator = NULL WHERE id=41;
UPDATE data.a_keys SET "type" = 'String', helptext = NULL, description = NULL, validator = NULL WHERE id=42;
UPDATE data.a_keys SET "type" = 'Dropdown', helptext = NULL, description = NULL, validator = NULL WHERE id=43;
UPDATE data.a_keys SET "type" = 'Checkbox', helptext = NULL, description = NULL, validator = NULL WHERE id=44;
UPDATE data.a_keys SET "type" = 'Integer', helptext = NULL, description = NULL, validator = '[0]' WHERE id=45;
UPDATE data.a_keys SET "type" = 'Checkbox', helptext = NULL, description = NULL, validator = NULL WHERE id=46;
UPDATE data.a_keys SET "type" = 'Integer', helptext = NULL, description = NULL, validator = '[0]' WHERE id=47;
UPDATE data.a_keys SET "type" = 'Integer', helptext = NULL, description = NULL, validator = '[1900,2100]' WHERE id=48;
UPDATE data.a_keys SET "type" = 'Checkbox', helptext = NULL, description = NULL, validator = NULL WHERE id=49;
UPDATE data.a_keys SET "type" = 'Text', helptext = NULL, description = NULL, validator = NULL WHERE id=50;


UPDATE data.sh_keys SET "type" = 'Dropdown', helptext = NULL, description = NULL, validator = NULL WHERE id=1;
UPDATE data.sh_keys SET "type" = 'String', helptext = NULL, description = NULL, validator = NULL WHERE id=2;
UPDATE data.sh_keys SET "type" = 'String', helptext = NULL, description = NULL, validator = NULL WHERE id=3;
UPDATE data.sh_keys SET "type" = 'Dropdown', helptext = NULL, description = NULL, validator = NULL WHERE id=4;
UPDATE data.sh_keys SET "type" = 'String', helptext = NULL, description = NULL, validator = NULL WHERE id=5;
UPDATE data.sh_keys SET "type" = 'String', helptext = NULL, description = NULL, validator = NULL WHERE id=6;
UPDATE data.sh_keys SET "type" = 'String', helptext = NULL, description = NULL, validator = NULL WHERE id=7;
UPDATE data.sh_keys SET "type" = 'Dropdown', helptext = NULL, description = NULL, validator = NULL WHERE id=8;


UPDATE data.a_values SET fk_a_key = 1, "order" = NULL WHERE id=1;
UPDATE data.a_values SET fk_a_key = 1, "order" = NULL WHERE id=2;
UPDATE data.a_values SET fk_a_key = 1, "order" = NULL WHERE id=3;
UPDATE data.a_values SET fk_a_key = 1, "order" = NULL WHERE id=4;
UPDATE data.a_values SET fk_a_key = 1, "order" = NULL WHERE id=5;
UPDATE data.a_values SET fk_a_key = 1, "order" = NULL WHERE id=6;
UPDATE data.a_values SET fk_a_key = 1, "order" = NULL WHERE id=7;
UPDATE data.a_values SET fk_a_key = 2, "order" = NULL WHERE id=8;
UPDATE data.a_values SET fk_a_key = 2, "order" = NULL WHERE id=9;
UPDATE data.a_values SET fk_a_key = 2, "order" = NULL WHERE id=10;
UPDATE data.a_values SET fk_a_key = 2, "order" = NULL WHERE id=11;
UPDATE data.a_values SET fk_a_key = 2, "order" = NULL WHERE id=12;
UPDATE data.a_values SET fk_a_key = 3, "order" = 1 WHERE id=13;
UPDATE data.a_values SET fk_a_key = 3, "order" = 2 WHERE id=14;
UPDATE data.a_values SET fk_a_key = 3, "order" = 3 WHERE id=15;
UPDATE data.a_values SET fk_a_key = 3, "order" = 4 WHERE id=16;
UPDATE data.a_values SET fk_a_key = 3, "order" = 5 WHERE id=17;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=18;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=19;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=20;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=21;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=22;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=23;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=24;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=25;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=26;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=27;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=28;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=29;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=30;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=31;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=32;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=33;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=34;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=35;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=36;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=37;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=38;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=39;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=40;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=41;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=42;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=43;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=44;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=45;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=46;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=47;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=48;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=49;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=50;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=51;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=52;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=53;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=54;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=55;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=56;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=57;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=58;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=59;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=60;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=61;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=62;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=63;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=64;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=65;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=66;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=67;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=68;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=69;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=70;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=71;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=72;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=73;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=74;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=75;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=76;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=77;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=78;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=79;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=80;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=81;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=82;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=83;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=84;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=85;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=86;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=87;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=88;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=89;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=90;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=91;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=92;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=93;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=94;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=95;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=96;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=97;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=98;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=99;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=100;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=101;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=102;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=103;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=104;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=105;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=106;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=107;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=108;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=109;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=110;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=111;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=112;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=113;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=114;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=115;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=116;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=117;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=118;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=119;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=120;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=121;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=122;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=123;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=124;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=125;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=126;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=127;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=128;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=129;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=130;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=131;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=132;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=133;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=134;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=135;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=136;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=137;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=138;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=139;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=140;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=141;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=142;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=143;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=144;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=145;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=146;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=147;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=148;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=149;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=150;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=151;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=152;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=153;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=154;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=155;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=156;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=157;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=158;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=159;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=160;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=161;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=162;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=163;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=164;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=165;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=166;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=167;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=168;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=169;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=170;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=171;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=172;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=173;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=174;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=175;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=176;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=177;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=178;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=179;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=180;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=181;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=182;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=183;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=184;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=185;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=186;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=187;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=188;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=189;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=190;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=191;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=192;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=193;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=194;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=195;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=196;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=197;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=198;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=199;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=200;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=201;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=202;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=203;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=204;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=205;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=206;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=207;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=208;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=209;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=210;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=211;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=212;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=213;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=214;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=215;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=216;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=217;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=218;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=219;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=220;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=221;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=222;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=223;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=224;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=225;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=226;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=227;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=228;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=229;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=230;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=231;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=232;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=233;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=234;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=235;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=236;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=237;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=238;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=239;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=240;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=241;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=242;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=243;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=244;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=245;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=246;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=247;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=248;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=249;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=250;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=251;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=252;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=253;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=254;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=255;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=256;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=257;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=258;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=259;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=260;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=261;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=262;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=263;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=264;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=265;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=266;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=267;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=268;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=269;
UPDATE data.a_values SET fk_a_key = 4, "order" = NULL WHERE id=270;
UPDATE data.a_values SET fk_a_key = 6, "order" = NULL WHERE id=271;
UPDATE data.a_values SET fk_a_key = 6, "order" = NULL WHERE id=272;
UPDATE data.a_values SET fk_a_key = 6, "order" = NULL WHERE id=273;
UPDATE data.a_values SET fk_a_key = 6, "order" = NULL WHERE id=274;
UPDATE data.a_values SET fk_a_key = 6, "order" = NULL WHERE id=275;
UPDATE data.a_values SET fk_a_key = 6, "order" = NULL WHERE id=276;
UPDATE data.a_values SET fk_a_key = 6, "order" = NULL WHERE id=277;
UPDATE data.a_values SET fk_a_key = 6, "order" = NULL WHERE id=278;
UPDATE data.a_values SET fk_a_key = 8, "order" = NULL WHERE id=279;
UPDATE data.a_values SET fk_a_key = 8, "order" = NULL WHERE id=280;
UPDATE data.a_values SET fk_a_key = 9, "order" = NULL WHERE id=281;
UPDATE data.a_values SET fk_a_key = 9, "order" = NULL WHERE id=282;
UPDATE data.a_values SET fk_a_key = 11, "order" = NULL WHERE id=283;
UPDATE data.a_values SET fk_a_key = 11, "order" = NULL WHERE id=284;
UPDATE data.a_values SET fk_a_key = 11, "order" = NULL WHERE id=285;
UPDATE data.a_values SET fk_a_key = 13, "order" = NULL WHERE id=286;
UPDATE data.a_values SET fk_a_key = 13, "order" = NULL WHERE id=287;
UPDATE data.a_values SET fk_a_key = 13, "order" = NULL WHERE id=288;
UPDATE data.a_values SET fk_a_key = 13, "order" = NULL WHERE id=289;
UPDATE data.a_values SET fk_a_key = 13, "order" = NULL WHERE id=290;
UPDATE data.a_values SET fk_a_key = 13, "order" = NULL WHERE id=291;
UPDATE data.a_values SET fk_a_key = 13, "order" = NULL WHERE id=292;
UPDATE data.a_values SET fk_a_key = 13, "order" = NULL WHERE id=293;
UPDATE data.a_values SET fk_a_key = 13, "order" = NULL WHERE id=294;
UPDATE data.a_values SET fk_a_key = 13, "order" = NULL WHERE id=295;
UPDATE data.a_values SET fk_a_key = 13, "order" = NULL WHERE id=296;
UPDATE data.a_values SET fk_a_key = 13, "order" = NULL WHERE id=297;
UPDATE data.a_values SET fk_a_key = 13, "order" = NULL WHERE id=298;
UPDATE data.a_values SET fk_a_key = 13, "order" = NULL WHERE id=299;
UPDATE data.a_values SET fk_a_key = 13, "order" = NULL WHERE id=300;
UPDATE data.a_values SET fk_a_key = 13, "order" = NULL WHERE id=301;
UPDATE data.a_values SET fk_a_key = 13, "order" = NULL WHERE id=302;
UPDATE data.a_values SET fk_a_key = 13, "order" = NULL WHERE id=303;
UPDATE data.a_values SET fk_a_key = 13, "order" = NULL WHERE id=304;
UPDATE data.a_values SET fk_a_key = 13, "order" = NULL WHERE id=305;
UPDATE data.a_values SET fk_a_key = 13, "order" = NULL WHERE id=306;
UPDATE data.a_values SET fk_a_key = 13, "order" = NULL WHERE id=307;
UPDATE data.a_values SET fk_a_key = 13, "order" = NULL WHERE id=308;
UPDATE data.a_values SET fk_a_key = 13, "order" = NULL WHERE id=309;
UPDATE data.a_values SET fk_a_key = 13, "order" = NULL WHERE id=310;
UPDATE data.a_values SET fk_a_key = 13, "order" = NULL WHERE id=311;
UPDATE data.a_values SET fk_a_key = 13, "order" = NULL WHERE id=312;
UPDATE data.a_values SET fk_a_key = 13, "order" = NULL WHERE id=313;
UPDATE data.a_values SET fk_a_key = 13, "order" = NULL WHERE id=314;
UPDATE data.a_values SET fk_a_key = 13, "order" = NULL WHERE id=315;
UPDATE data.a_values SET fk_a_key = 13, "order" = NULL WHERE id=316;
UPDATE data.a_values SET fk_a_key = 13, "order" = NULL WHERE id=317;
UPDATE data.a_values SET fk_a_key = 13, "order" = NULL WHERE id=318;
UPDATE data.a_values SET fk_a_key = 13, "order" = NULL WHERE id=319;
UPDATE data.a_values SET fk_a_key = 13, "order" = NULL WHERE id=320;
UPDATE data.a_values SET fk_a_key = 13, "order" = NULL WHERE id=321;
UPDATE data.a_values SET fk_a_key = 13, "order" = NULL WHERE id=322;
UPDATE data.a_values SET fk_a_key = 13, "order" = NULL WHERE id=323;
UPDATE data.a_values SET fk_a_key = 13, "order" = NULL WHERE id=324;
UPDATE data.a_values SET fk_a_key = 13, "order" = NULL WHERE id=325;
UPDATE data.a_values SET fk_a_key = 13, "order" = NULL WHERE id=326;
UPDATE data.a_values SET fk_a_key = 13, "order" = NULL WHERE id=327;
UPDATE data.a_values SET fk_a_key = 26, "order" = NULL WHERE id=328;
UPDATE data.a_values SET fk_a_key = 26, "order" = NULL WHERE id=329;
UPDATE data.a_values SET fk_a_key = 26, "order" = NULL WHERE id=330;
UPDATE data.a_values SET fk_a_key = 26, "order" = NULL WHERE id=331;
UPDATE data.a_values SET fk_a_key = 26, "order" = NULL WHERE id=332;
UPDATE data.a_values SET fk_a_key = 26, "order" = NULL WHERE id=333;
UPDATE data.a_values SET fk_a_key = 26, "order" = NULL WHERE id=334;
UPDATE data.a_values SET fk_a_key = 26, "order" = NULL WHERE id=335;
UPDATE data.a_values SET fk_a_key = 26, "order" = NULL WHERE id=336;
UPDATE data.a_values SET fk_a_key = 28, "order" = NULL WHERE id=337;
UPDATE data.a_values SET fk_a_key = 28, "order" = NULL WHERE id=338;
UPDATE data.a_values SET fk_a_key = 33, "order" = NULL WHERE id=339;
UPDATE data.a_values SET fk_a_key = 33, "order" = NULL WHERE id=340;
UPDATE data.a_values SET fk_a_key = 33, "order" = NULL WHERE id=341;
UPDATE data.a_values SET fk_a_key = 33, "order" = NULL WHERE id=342;
UPDATE data.a_values SET fk_a_key = 33, "order" = NULL WHERE id=343;
UPDATE data.a_values SET fk_a_key = 33, "order" = NULL WHERE id=344;
UPDATE data.a_values SET fk_a_key = 35, "order" = NULL WHERE id=345;
UPDATE data.a_values SET fk_a_key = 35, "order" = NULL WHERE id=346;
UPDATE data.a_values SET fk_a_key = 35, "order" = NULL WHERE id=347;
UPDATE data.a_values SET fk_a_key = 35, "order" = NULL WHERE id=348;
UPDATE data.a_values SET fk_a_key = 36, "order" = NULL WHERE id=349;
UPDATE data.a_values SET fk_a_key = 36, "order" = NULL WHERE id=350;
UPDATE data.a_values SET fk_a_key = 36, "order" = NULL WHERE id=351;
UPDATE data.a_values SET fk_a_key = 36, "order" = NULL WHERE id=352;
UPDATE data.a_values SET fk_a_key = 36, "order" = NULL WHERE id=353;
UPDATE data.a_values SET fk_a_key = 36, "order" = NULL WHERE id=354;
UPDATE data.a_values SET fk_a_key = 36, "order" = NULL WHERE id=355;
UPDATE data.a_values SET fk_a_key = 36, "order" = NULL WHERE id=356;
UPDATE data.a_values SET fk_a_key = 39, "order" = NULL WHERE id=357;
UPDATE data.a_values SET fk_a_key = 39, "order" = NULL WHERE id=358;
UPDATE data.a_values SET fk_a_key = 39, "order" = NULL WHERE id=359;
UPDATE data.a_values SET fk_a_key = 43, "order" = NULL WHERE id=360;
UPDATE data.a_values SET fk_a_key = 43, "order" = NULL WHERE id=361;
UPDATE data.a_values SET fk_a_key = 43, "order" = NULL WHERE id=362;
UPDATE data.a_values SET fk_a_key = 43, "order" = NULL WHERE id=363;
UPDATE data.a_values SET fk_a_key = 44, "order" = NULL WHERE id=364;
UPDATE data.a_values SET fk_a_key = 44, "order" = NULL WHERE id=365;
UPDATE data.a_values SET fk_a_key = 44, "order" = NULL WHERE id=366;
UPDATE data.a_values SET fk_a_key = 44, "order" = NULL WHERE id=367;
UPDATE data.a_values SET fk_a_key = 44, "order" = NULL WHERE id=368;
UPDATE data.a_values SET fk_a_key = 44, "order" = NULL WHERE id=369;
UPDATE data.a_values SET fk_a_key = 44, "order" = NULL WHERE id=370;
UPDATE data.a_values SET fk_a_key = 44, "order" = NULL WHERE id=371;
UPDATE data.a_values SET fk_a_key = 44, "order" = NULL WHERE id=372;
UPDATE data.a_values SET fk_a_key = 44, "order" = NULL WHERE id=373;
UPDATE data.a_values SET fk_a_key = 44, "order" = NULL WHERE id=374;
UPDATE data.a_values SET fk_a_key = 44, "order" = NULL WHERE id=375;
UPDATE data.a_values SET fk_a_key = 44, "order" = NULL WHERE id=376;
UPDATE data.a_values SET fk_a_key = 44, "order" = NULL WHERE id=377;
UPDATE data.a_values SET fk_a_key = 44, "order" = NULL WHERE id=378;
UPDATE data.a_values SET fk_a_key = 44, "order" = NULL WHERE id=379;
UPDATE data.a_values SET fk_a_key = 44, "order" = NULL WHERE id=380;
UPDATE data.a_values SET fk_a_key = 44, "order" = NULL WHERE id=381;
UPDATE data.a_values SET fk_a_key = 44, "order" = NULL WHERE id=382;
UPDATE data.a_values SET fk_a_key = 44, "order" = NULL WHERE id=383;
UPDATE data.a_values SET fk_a_key = 44, "order" = NULL WHERE id=384;
UPDATE data.a_values SET fk_a_key = 44, "order" = NULL WHERE id=385;
UPDATE data.a_values SET fk_a_key = 44, "order" = NULL WHERE id=386;
UPDATE data.a_values SET fk_a_key = 44, "order" = NULL WHERE id=387;
UPDATE data.a_values SET fk_a_key = 44, "order" = NULL WHERE id=388;
UPDATE data.a_values SET fk_a_key = 44, "order" = NULL WHERE id=389;
UPDATE data.a_values SET fk_a_key = 44, "order" = NULL WHERE id=390;
UPDATE data.a_values SET fk_a_key = 44, "order" = NULL WHERE id=391;
UPDATE data.a_values SET fk_a_key = 44, "order" = NULL WHERE id=392;
UPDATE data.a_values SET fk_a_key = 44, "order" = NULL WHERE id=393;
UPDATE data.a_values SET fk_a_key = 44, "order" = NULL WHERE id=394;
UPDATE data.a_values SET fk_a_key = 44, "order" = NULL WHERE id=395;
UPDATE data.a_values SET fk_a_key = 44, "order" = NULL WHERE id=396;
UPDATE data.a_values SET fk_a_key = 44, "order" = NULL WHERE id=397;
UPDATE data.a_values SET fk_a_key = 44, "order" = NULL WHERE id=398;
UPDATE data.a_values SET fk_a_key = 44, "order" = NULL WHERE id=399;
UPDATE data.a_values SET fk_a_key = 44, "order" = NULL WHERE id=400;
UPDATE data.a_values SET fk_a_key = 44, "order" = NULL WHERE id=401;
UPDATE data.a_values SET fk_a_key = 44, "order" = NULL WHERE id=402;
UPDATE data.a_values SET fk_a_key = 44, "order" = NULL WHERE id=403;
UPDATE data.a_values SET fk_a_key = 44, "order" = NULL WHERE id=404;
UPDATE data.a_values SET fk_a_key = 44, "order" = NULL WHERE id=405;
UPDATE data.a_values SET fk_a_key = 44, "order" = NULL WHERE id=406;
UPDATE data.a_values SET fk_a_key = 44, "order" = NULL WHERE id=407;
UPDATE data.a_values SET fk_a_key = 44, "order" = NULL WHERE id=408;
UPDATE data.a_values SET fk_a_key = 44, "order" = NULL WHERE id=409;
UPDATE data.a_values SET fk_a_key = 44, "order" = NULL WHERE id=410;
UPDATE data.a_values SET fk_a_key = 44, "order" = NULL WHERE id=411;
UPDATE data.a_values SET fk_a_key = 44, "order" = NULL WHERE id=412;
UPDATE data.a_values SET fk_a_key = 44, "order" = NULL WHERE id=413;
UPDATE data.a_values SET fk_a_key = 44, "order" = NULL WHERE id=414;
UPDATE data.a_values SET fk_a_key = 44, "order" = NULL WHERE id=415;
UPDATE data.a_values SET fk_a_key = 44, "order" = NULL WHERE id=416;
UPDATE data.a_values SET fk_a_key = 44, "order" = NULL WHERE id=417;
UPDATE data.a_values SET fk_a_key = 44, "order" = NULL WHERE id=418;
UPDATE data.a_values SET fk_a_key = 44, "order" = NULL WHERE id=419;
UPDATE data.a_values SET fk_a_key = 44, "order" = NULL WHERE id=420;
UPDATE data.a_values SET fk_a_key = 44, "order" = NULL WHERE id=421;
UPDATE data.a_values SET fk_a_key = 44, "order" = NULL WHERE id=422;
UPDATE data.a_values SET fk_a_key = 44, "order" = NULL WHERE id=423;
UPDATE data.a_values SET fk_a_key = 44, "order" = NULL WHERE id=424;
UPDATE data.a_values SET fk_a_key = 44, "order" = NULL WHERE id=425;
UPDATE data.a_values SET fk_a_key = 44, "order" = NULL WHERE id=426;
UPDATE data.a_values SET fk_a_key = 44, "order" = NULL WHERE id=427;
UPDATE data.a_values SET fk_a_key = 44, "order" = NULL WHERE id=428;
UPDATE data.a_values SET fk_a_key = 44, "order" = NULL WHERE id=429;
UPDATE data.a_values SET fk_a_key = 44, "order" = NULL WHERE id=430;
UPDATE data.a_values SET fk_a_key = 44, "order" = NULL WHERE id=431;
UPDATE data.a_values SET fk_a_key = 44, "order" = NULL WHERE id=432;
UPDATE data.a_values SET fk_a_key = 44, "order" = NULL WHERE id=433;
UPDATE data.a_values SET fk_a_key = 44, "order" = NULL WHERE id=434;
UPDATE data.a_values SET fk_a_key = 44, "order" = NULL WHERE id=435;
UPDATE data.a_values SET fk_a_key = 44, "order" = NULL WHERE id=436;
UPDATE data.a_values SET fk_a_key = 44, "order" = NULL WHERE id=437;
UPDATE data.a_values SET fk_a_key = 44, "order" = NULL WHERE id=438;
UPDATE data.a_values SET fk_a_key = 44, "order" = NULL WHERE id=439;
UPDATE data.a_values SET fk_a_key = 44, "order" = NULL WHERE id=440;
UPDATE data.a_values SET fk_a_key = 44, "order" = NULL WHERE id=441;
UPDATE data.a_values SET fk_a_key = 44, "order" = NULL WHERE id=442;
UPDATE data.a_values SET fk_a_key = 44, "order" = NULL WHERE id=443;
UPDATE data.a_values SET fk_a_key = 44, "order" = NULL WHERE id=444;
UPDATE data.a_values SET fk_a_key = 44, "order" = NULL WHERE id=445;
UPDATE data.a_values SET fk_a_key = 44, "order" = NULL WHERE id=446;
UPDATE data.a_values SET fk_a_key = 44, "order" = NULL WHERE id=447;
UPDATE data.a_values SET fk_a_key = 44, "order" = NULL WHERE id=448;
UPDATE data.a_values SET fk_a_key = 44, "order" = NULL WHERE id=449;
UPDATE data.a_values SET fk_a_key = 46, "order" = NULL WHERE id=450;
UPDATE data.a_values SET fk_a_key = 46, "order" = NULL WHERE id=451;
UPDATE data.a_values SET fk_a_key = 46, "order" = NULL WHERE id=452;
UPDATE data.a_values SET fk_a_key = 46, "order" = NULL WHERE id=453;
UPDATE data.a_values SET fk_a_key = 49, "order" = NULL WHERE id=454;
UPDATE data.a_values SET fk_a_key = 49, "order" = NULL WHERE id=455;
UPDATE data.a_values SET fk_a_key = 49, "order" = NULL WHERE id=456;
UPDATE data.a_values SET fk_a_key = 49, "order" = NULL WHERE id=457;
UPDATE data.a_values SET fk_a_key = 49, "order" = NULL WHERE id=458;


UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=1;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=2;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=3;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=4;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=5;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=6;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=7;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=8;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=9;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=10;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=11;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=12;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=13;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=14;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=15;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=16;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=17;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=18;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=19;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=20;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=21;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=22;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=23;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=24;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=25;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=26;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=27;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=28;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=29;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=30;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=31;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=32;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=33;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=34;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=35;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=36;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=37;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=38;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=39;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=40;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=41;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=42;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=43;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=44;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=45;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=46;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=47;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=48;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=49;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=50;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=51;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=52;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=53;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=54;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=55;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=56;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=57;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=58;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=59;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=60;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=61;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=62;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=63;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=64;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=65;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=66;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=67;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=68;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=69;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=70;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=71;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=72;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=73;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=74;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=75;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=76;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=77;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=78;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=79;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=80;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=81;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=82;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=83;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=84;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=85;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=86;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=87;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=88;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=89;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=90;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=91;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=92;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=93;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=94;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=95;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=96;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=97;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=98;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=99;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=100;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=101;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=102;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=103;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=104;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=105;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=106;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=107;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=108;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=109;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=110;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=111;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=112;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=113;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=114;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=115;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=116;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=117;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=118;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=119;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=120;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=121;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=122;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=123;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=124;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=125;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=126;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=127;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=128;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=129;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=130;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=131;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=132;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=133;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=134;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=135;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=136;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=137;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=138;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=139;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=140;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=141;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=142;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=143;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=144;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=145;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=146;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=147;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=148;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=149;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=150;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=151;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=152;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=153;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=154;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=155;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=156;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=157;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=158;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=159;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=160;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=161;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=162;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=163;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=164;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=165;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=166;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=167;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=168;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=169;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=170;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=171;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=172;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=173;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=174;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=175;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=176;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=177;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=178;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=179;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=180;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=181;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=182;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=183;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=184;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=185;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=186;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=187;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=188;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=189;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=190;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=191;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=192;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=193;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=194;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=195;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=196;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=197;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=198;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=199;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=200;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=201;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=202;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=203;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=204;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=205;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=206;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=207;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=208;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=209;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=210;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=211;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=212;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=213;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=214;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=215;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=216;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=217;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=218;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=219;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=220;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=221;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=222;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=223;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=224;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=225;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=226;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=227;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=228;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=229;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=230;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=231;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=232;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=233;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=234;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=235;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=236;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=237;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=238;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=239;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=240;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=241;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=242;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=243;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=244;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=245;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=246;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=247;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=248;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=249;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=250;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=251;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=252;
UPDATE data.sh_values SET fk_sh_key = 1, "order" = NULL WHERE id=253;
UPDATE data.sh_values SET fk_sh_key = 4, "order" = NULL WHERE id=254;
UPDATE data.sh_values SET fk_sh_key = 4, "order" = NULL WHERE id=255;
UPDATE data.sh_values SET fk_sh_key = 4, "order" = NULL WHERE id=256;
UPDATE data.sh_values SET fk_sh_key = 4, "order" = NULL WHERE id=257;
UPDATE data.sh_values SET fk_sh_key = 4, "order" = NULL WHERE id=258;
UPDATE data.sh_values SET fk_sh_key = 4, "order" = NULL WHERE id=259;
UPDATE data.sh_values SET fk_sh_key = 4, "order" = NULL WHERE id=260;
UPDATE data.sh_values SET fk_sh_key = 4, "order" = NULL WHERE id=261;
UPDATE data.sh_values SET fk_sh_key = 8, "order" = NULL WHERE id=262;
UPDATE data.sh_values SET fk_sh_key = 8, "order" = NULL WHERE id=263;
UPDATE data.sh_values SET fk_sh_key = 8, "order" = NULL WHERE id=264;
UPDATE data.sh_values SET fk_sh_key = 8, "order" = NULL WHERE id=265;
UPDATE data.sh_values SET fk_sh_key = 8, "order" = NULL WHERE id=266;
UPDATE data.sh_values SET fk_sh_key = 8, "order" = NULL WHERE id=267;
UPDATE data.sh_values SET fk_sh_key = 8, "order" = NULL WHERE id=268;




