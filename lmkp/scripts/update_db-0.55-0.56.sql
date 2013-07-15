/*
CATEGORIES
*/

-- Insert new category
INSERT INTO data.categories(id, name, type, fk_language, description, fk_category) VALUES
  (41, 'Amount of Investment', 'activities', 1, NULL, NULL);
SELECT setval('data.categories_id_seq', 41, true);


/*
A_KEYS
*/

-- Drop NULL constraint on language and key
ALTER TABLE data.a_keys
ALTER fk_language DROP NOT NULL,
ALTER "type" DROP NOT NULL;

-- Set language of original entries to NULL
UPDATE data.a_keys
SET fk_language = NULL
WHERE id <= 51;

-- Add new A_Keys
INSERT INTO data.a_keys(id, fk_a_key, fk_language, key, type, helptext, description, validator) VALUES
  (52, NULL, NULL, 'Announced amount of investment', 'Text', NULL, NULL, NULL),
  (53, NULL, NULL, 'Remark (Intention of Investment)', 'Text', NULL, NULL, NULL),
  (54, NULL, NULL, 'Remark (Negotiation Status)', 'Text', NULL, NULL, NULL),
  (55, NULL, NULL, 'Remark (Number of Jobs Created)', 'Text', NULL, NULL, NULL),
  (56, NULL, NULL, 'Contract Number', 'String', NULL, NULL, NULL);

-- Insert translations to English for each
INSERT INTO data.a_keys(id, fk_a_key, fk_language, key, type, helptext, description, validator) VALUES
  (57, 1, 1, 'Data source', NULL, NULL, NULL, NULL),
  (58, 2, 1, 'Negotiation Status', NULL, NULL, NULL, NULL),
  (59, 3, 1, 'Spatial Accuracy', NULL, NULL, NULL, NULL),
  (60, 4, 1, 'Country', NULL, NULL, NULL, NULL),
  (61, 5, 1, 'Intended area (ha)', NULL, NULL, NULL, NULL),
  (62, 6, 1, 'Intention of Investment', NULL, NULL, NULL, NULL),
  (63, 7, 1, 'Duration of Agreement (years)', NULL, NULL, NULL, NULL),
  (64, 8, 1, 'Contract farming', NULL, NULL, NULL, NULL),
  (65, 9, 1, 'Scope of forestry', NULL, NULL, NULL, NULL),
  (66, 10, 1, 'URL / Web', NULL, NULL, NULL, NULL),
  (67, 11, 1, 'Water extraction', NULL, NULL, NULL, NULL),
  (68, 12, 1, 'Percentage', NULL, NULL, NULL, NULL),
  (69, 13, 1, 'Mineral', NULL, NULL, NULL, NULL),
  (70, 14, 1, 'Announced amount of investement', NULL, NULL, NULL, NULL),
  (71, 15, 1, 'Current area in operation (ha)', NULL, NULL, NULL, NULL),
  (72, 16, 1, 'How much do investors pay for water', NULL, NULL, NULL, NULL),
  (73, 17, 1, 'Original reference number', NULL, NULL, NULL, NULL),
  (74, 18, 1, 'Number of farmers', NULL, NULL, NULL, NULL),
  (75, 19, 1, 'Current number of employees', NULL, NULL, NULL, NULL),
  (76, 20, 1, 'Date', NULL, NULL, NULL, NULL),
  (77, 21, 1, 'Number of people actually displaced', NULL, NULL, NULL, NULL),
  (78, 22, 1, 'Leasing fee (per year)', NULL, NULL, NULL, NULL),
  (79, 23, 1, 'Current total number of jobs', NULL, NULL, NULL, NULL),
  (80, 24, 1, 'How much water is extracted (m3/year)', NULL, NULL, NULL, NULL),
  (81, 25, 1, 'Remark', NULL, NULL, NULL, NULL),
  (82, 26, 1, 'Animals', NULL, NULL, NULL, NULL),
  (83, 27, 1, 'Name', NULL, NULL, NULL, NULL),
  (84, 28, 1, 'Use of produce', NULL, NULL, NULL, NULL),
  (85, 29, 1, 'How did community react', NULL, NULL, NULL, NULL),
  (86, 30, 1, 'Purchase price', NULL, NULL, NULL, NULL),
  (87, 31, 1, 'Annual leasing fee area (ha)', NULL, NULL, NULL, NULL),
  (88, 32, 1, 'Area (ha)', NULL, NULL, NULL, NULL),
  (89, 33, 1, 'Former predominant land use', NULL, NULL, NULL, NULL),
  (90, 34, 1, 'Contract area (ha)', NULL, NULL, NULL, NULL),
  (91, 35, 1, 'Former predominant land cover', NULL, NULL, NULL, NULL),
  (92, 36, 1, 'Benefits for local communities', NULL, NULL, NULL, NULL),
  (93, 37, 1, 'Current Number of daily/seasonal workers', NULL, NULL, NULL, NULL),
  (94, 38, 1, 'Purchase price area (ha)', NULL, NULL, NULL, NULL),
  (95, 39, 1, 'Nature of the deal', NULL, NULL, NULL, NULL),
  (96, 40, 1, 'Planned number of employees', NULL, NULL, NULL, NULL),
  (97, 41, 1, 'Consultation of local community', NULL, NULL, NULL, NULL),
  (98, 42, 1, 'Promised or received compensation', NULL, NULL, NULL, NULL),
  (99, 43, 1, 'Implementation status', NULL, NULL, NULL, NULL),
  (100, 44, 1, 'Crop', NULL, NULL, NULL, NULL),
  (101, 45, 1, 'Planned Number of daily/seasonal workers', NULL, NULL, NULL, NULL),
  (102, 46, 1, 'Scope of agriculture', NULL, NULL, NULL, NULL),
  (103, 47, 1, 'Planned total number of jobs', NULL, NULL, NULL, NULL),
  (104, 48, 1, 'Year', NULL, NULL, NULL, NULL),
  (105, 49, 1, 'Former predominant land owner', NULL, NULL, NULL, NULL),
  (106, 50, 1, 'Files', NULL, NULL, NULL, NULL),
  (107, 51, 1, 'Contract date', NULL, NULL, NULL, NULL),
  (108, 52, 1, 'Announced amount of investment', NULL, NULL, NULL, NULL),
  (109, 53, 1, 'Remark', NULL, NULL, NULL, NULL),
  (110, 54, 1, 'Remark', NULL, NULL, NULL, NULL),
  (111, 55, 1, 'Remark', NULL, NULL, NULL, NULL),
  (112, 56, 1, 'Contract Number', NULL, NULL, NULL, NULL);
SELECT setval('data.a_keys_id_seq', 112, true);


/*
SH_KEYS
*/

-- Drop NULL constraint on language and key
ALTER TABLE data.sh_keys
ALTER fk_language DROP NOT NULL,
ALTER "type" DROP NOT NULL;

-- Set language of original entries to NULL
UPDATE data.sh_keys
SET fk_language = NULL
WHERE id <= 8;

-- Insert translations to English for each
INSERT INTO data.sh_keys(id, fk_sh_key, fk_language, key, type, helptext, description, validator) VALUES
  (9, 1, 1, 'Country of origin', NULL, NULL, NULL, NULL),
  (10, 2, 1, 'Name', NULL, NULL, NULL, NULL),
  (11, 3, 1, 'Website', NULL, NULL, NULL, NULL),
  (12, 4, 1, 'Economic Sector', NULL, NULL, NULL, NULL),
  (13, 5, 1, 'Phone', NULL, NULL, NULL, NULL),
  (14, 6, 1, 'Domestic Partner', NULL, NULL, NULL, NULL),
  (15, 7, 1, 'Address', NULL, NULL, NULL, NULL),
  (16, 8, 1, 'Type of Institution', NULL, NULL, NULL, NULL);
SELECT setval('data.sh_keys_id_seq', 16, true);
