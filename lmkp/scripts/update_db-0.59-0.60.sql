/**
This script can be used to update the database to version 0.6.
It updates the names of the countries (both for Activities and Stakeholders) to
match ISO 3166-1 (http://en.wikipedia.org/wiki/ISO_3166-1).
*/

/*
ACTIVITIES
*/
-- Update old entries to match new ISO codes.
UPDATE data.a_values SET value = 'Åland Islands' WHERE fk_a_key = 4 AND value = 'Åland';
UPDATE data.a_values SET value = 'Bolivia, Plurinational State of' WHERE fk_a_key = 4 AND value = 'Bolivia';
UPDATE data.a_values SET value = 'Bonaire, Sint Eustatius and Saba' WHERE fk_a_key = 4 AND value = 'Bonaire, Saint Eustatius and Saba';
UPDATE data.a_values SET value = 'Virgin Islands, British' WHERE fk_a_key = 4 AND value = 'British Virgin Islands';
UPDATE data.a_values SET value = 'Brunei Darussalam' WHERE fk_a_key = 4 AND value = 'Brunei';
UPDATE data.a_values SET value = 'Cocos (Keeling) Islands' WHERE fk_a_key = 4 AND value = 'Cocos Islands';
UPDATE data.a_values SET value = 'Congo, the Democratic Republic of the' WHERE fk_a_key = 4 AND value = 'Democratic Republic of the Congo';
UPDATE data.a_values SET value = 'Timor-Leste' WHERE fk_a_key = 4 AND value = 'East Timor';
UPDATE data.a_values SET value = 'Falkland Islands (Malvinas)' WHERE fk_a_key = 4 AND value = 'Falkland Islands';
UPDATE data.a_values SET value = 'Iran, Islamic Republic of' WHERE fk_a_key = 4 AND value = 'Iran';
UPDATE data.a_values SET value = 'Lao People''s Democratic Republic' WHERE fk_a_key = 4 AND value = 'Laos';
UPDATE data.a_values SET value = 'Macedonia, The Former Yugoslav Republic of' WHERE fk_a_key = 4 AND value = 'Macedonia';
UPDATE data.a_values SET value = 'Micronesia, Federated States of' WHERE fk_a_key = 4 AND value = 'Micronesia';
UPDATE data.a_values SET value = 'Moldova, Republic of' WHERE fk_a_key = 4 AND value = 'Moldova';
UPDATE data.a_values SET value = 'Korea, Democratic People''s Republic of' WHERE fk_a_key = 4 AND value = 'North Korea';
UPDATE data.a_values SET value = 'Palestine, State of' WHERE fk_a_key = 4 AND value = 'Palestina';
UPDATE data.a_values SET value = 'Pitcairn' WHERE fk_a_key = 4 AND value = 'Pitcairn Islands';
UPDATE data.a_values SET value = 'Congo' WHERE fk_a_key = 4 AND value = 'Republic of Congo';
UPDATE data.a_values SET value = 'Réunion' WHERE fk_a_key = 4 AND value = 'Reunion';
UPDATE data.a_values SET value = 'Russian Federation' WHERE fk_a_key = 4 AND value = 'Russia';
UPDATE data.a_values SET value = 'Saint Helena, Ascension and Tristan da Cunha' WHERE fk_a_key = 4 AND value = 'Saint Helena';
UPDATE data.a_values SET value = 'Saint Barthélemy' WHERE fk_a_key = 4 AND value = 'Saint-Barthélemy';
UPDATE data.a_values SET value = 'Saint Martin (French part)' WHERE fk_a_key = 4 AND value = 'Saint-Martin';
UPDATE data.a_values SET value = 'Sint Maarten (Dutch part)' WHERE fk_a_key = 4 AND value = 'Sint Maarten';
UPDATE data.a_values SET value = 'Korea, Republic of' WHERE fk_a_key = 4 AND value = 'South Korea';
UPDATE data.a_values SET value = 'Syrian Arab Republic' WHERE fk_a_key = 4 AND value = 'Syria';
UPDATE data.a_values SET value = 'Taiwan, Province of China' WHERE fk_a_key = 4 AND value = 'Taiwan';
UPDATE data.a_values SET value = 'Tanzania, United Republic of' WHERE fk_a_key = 4 AND value = 'Tanzania';
UPDATE data.a_values SET value = 'Holy See (Vatican City State)' WHERE fk_a_key = 4 AND value = 'Vatican City';
UPDATE data.a_values SET value = 'Venezuela, Bolivarian Republic of' WHERE fk_a_key = 4 AND value = 'Venezuela';
UPDATE data.a_values SET value = 'Viet Nam' WHERE fk_a_key = 4 AND value = 'Vietnam';

-- Delete old entries which are not in the new ISO codes anymore.
DELETE FROM data.a_values WHERE fk_a_key = 4 AND value = 'Caspian Sea';
DELETE FROM data.a_values WHERE fk_a_key = 4 AND value = 'Clipperton Island';
DELETE FROM data.a_values WHERE fk_a_key = 4 AND value = 'Kosovo';
DELETE FROM data.a_values WHERE fk_a_key = 4 AND value = 'Spratly islands';


/*
STAKEHOLDERS
*/
-- Update old entries to match new ISO codes.
UPDATE data.sh_values SET value = 'Åland Islands' WHERE fk_sh_key = 1 AND value = 'Åland';
UPDATE data.sh_values SET value = 'Bolivia, Plurinational State of' WHERE fk_sh_key = 1 AND value = 'Bolivia';
UPDATE data.sh_values SET value = 'Bonaire, Sint Eustatius and Saba' WHERE fk_sh_key = 1 AND value = 'Bonaire, Saint Eustatius and Saba';
UPDATE data.sh_values SET value = 'Virgin Islands, British' WHERE fk_sh_key = 1 AND value = 'British Virgin Islands';
UPDATE data.sh_values SET value = 'Brunei Darussalam' WHERE fk_sh_key = 1 AND value = 'Brunei';
UPDATE data.sh_values SET value = 'Cocos (Keeling) Islands' WHERE fk_sh_key = 1 AND value = 'Cocos Islands';
UPDATE data.sh_values SET value = 'Congo, the Democratic Republic of the' WHERE fk_sh_key = 1 AND value = 'Democratic Republic of the Congo';
UPDATE data.sh_values SET value = 'Timor-Leste' WHERE fk_sh_key = 1 AND value = 'East Timor';
UPDATE data.sh_values SET value = 'Falkland Islands (Malvinas)' WHERE fk_sh_key = 1 AND value = 'Falkland Islands';
UPDATE data.sh_values SET value = 'Iran, Islamic Republic of' WHERE fk_sh_key = 1 AND value = 'Iran';
UPDATE data.sh_values SET value = 'Lao People''s Democratic Republic' WHERE fk_sh_key = 1 AND value = 'Laos';
UPDATE data.sh_values SET value = 'Macedonia, The Former Yugoslav Republic of' WHERE fk_sh_key = 1 AND value = 'Macedonia';
UPDATE data.sh_values SET value = 'Micronesia, Federated States of' WHERE fk_sh_key = 1 AND value = 'Micronesia';
UPDATE data.sh_values SET value = 'Moldova, Republic of' WHERE fk_sh_key = 1 AND value = 'Moldova';
UPDATE data.sh_values SET value = 'Korea, Democratic People''s Republic of' WHERE fk_sh_key = 1 AND value = 'North Korea';
UPDATE data.sh_values SET value = 'Palestine, State of' WHERE fk_sh_key = 1 AND value = 'Palestina';
UPDATE data.sh_values SET value = 'Pitcairn' WHERE fk_sh_key = 1 AND value = 'Pitcairn Islands';
UPDATE data.sh_values SET value = 'Congo' WHERE fk_sh_key = 1 AND value = 'Republic of Congo';
UPDATE data.sh_values SET value = 'Réunion' WHERE fk_sh_key = 1 AND value = 'Reunion';
UPDATE data.sh_values SET value = 'Russian Federation' WHERE fk_sh_key = 1 AND value = 'Russia';
UPDATE data.sh_values SET value = 'Saint Helena, Ascension and Tristan da Cunha' WHERE fk_sh_key = 1 AND value = 'Saint Helena';
UPDATE data.sh_values SET value = 'Saint Barthélemy' WHERE fk_sh_key = 1 AND value = 'Saint-Barthélemy';
UPDATE data.sh_values SET value = 'Saint Martin (French part)' WHERE fk_sh_key = 1 AND value = 'Saint-Martin';
UPDATE data.sh_values SET value = 'Sint Maarten (Dutch part)' WHERE fk_sh_key = 1 AND value = 'Sint Maarten';
UPDATE data.sh_values SET value = 'Korea, Republic of' WHERE fk_sh_key = 1 AND value = 'South Korea';
UPDATE data.sh_values SET value = 'Syrian Arab Republic' WHERE fk_sh_key = 1 AND value = 'Syria';
UPDATE data.sh_values SET value = 'Taiwan, Province of China' WHERE fk_sh_key = 1 AND value = 'Taiwan';
UPDATE data.sh_values SET value = 'Tanzania, United Republic of' WHERE fk_sh_key = 1 AND value = 'Tanzania';
UPDATE data.sh_values SET value = 'Holy See (Vatican City State)' WHERE fk_sh_key = 1 AND value = 'Vatican City';
UPDATE data.sh_values SET value = 'Venezuela, Bolivarian Republic of' WHERE fk_sh_key = 1 AND value = 'Venezuela';
UPDATE data.sh_values SET value = 'Viet Nam' WHERE fk_sh_key = 1 AND value = 'Vietnam';

-- Delete old entries which are not in the new ISO codes anymore.
DELETE FROM data.sh_values WHERE fk_sh_key = 1 AND value = 'Caspian Sea';
DELETE FROM data.sh_values WHERE fk_sh_key = 1 AND value = 'Clipperton Island';
DELETE FROM data.sh_values WHERE fk_sh_key = 1 AND value = 'Kosovo';
DELETE FROM data.sh_values WHERE fk_sh_key = 1 AND value = 'Spratly islands';
