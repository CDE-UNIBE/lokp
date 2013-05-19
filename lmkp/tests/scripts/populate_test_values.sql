/*
  *** IMPORTANT *** Do not use this script on a productive environment!

  Use this script to add values needed for the tests to run.

  Last update: 2013-19-05 13:37 to match data model of LMKP v0.42

  The script will:
  - Add 4 Users (the password always being 'asdf') with proper links to their groups and profiles:
    user1: moderator of Laos profile
    user2: moderator of Peru profile
    user3: editor
    user4: editor
  - Add 2 languages:
    3: French
    4: Spanish
*/

/*
INSERT INTO data.users (uuid, username, email, firstname, lastname, privacy, registration_timestamp, is_active, activation_uuid, is_approved, fk_institution, password) VALUES ('fe131371-ac1d-449a-87a6-0612b29b76c5', 'user1', '1@u.com', NULL, NULL, 1, '2013-05-15 08:33:14.213+02', true, NULL, true, NULL, '$p5k2$1000$zJjEqW0Szjt6mrQcpEiSXw==$zVfgK6jSCjASNt7oVLACEVgpYAY=');
INSERT INTO data.users (uuid, username, email, firstname, lastname, privacy, registration_timestamp, is_active, activation_uuid, is_approved, fk_institution, password) VALUES ('9cc2e556-c40a-48d3-9caa-07a61afeb2b0', 'user2', '2@u.com', NULL, NULL, 1, '2013-05-15 08:33:14.213+02', true, NULL, true, NULL, '$p5k2$1000$as95u38eiteYptwYRG2XHQ==$Eqp5WDw0SJwyypdEZLowynoLoO0=');
INSERT INTO data.users (uuid, username, email, firstname, lastname, privacy, registration_timestamp, is_active, activation_uuid, is_approved, fk_institution, password) VALUES ('d9c3e09d-2cb7-4a53-99f3-6c70d0879a0a', 'user3', '3@u.com', NULL, NULL, 1, '2013-05-15 08:33:14.213+02', true, NULL, true, NULL, '$p5k2$1000$iQzIRe57SRcExzUw1F4hnw==$N038LZPWJXnV844vxwFOObuhkD0=');
INSERT INTO data.users (uuid, username, email, firstname, lastname, privacy, registration_timestamp, is_active, activation_uuid, is_approved, fk_institution, password) VALUES ('d9dd5ccd-ba5a-4b56-980f-7f7c830d5bdb', 'user4', '4@u.com', NULL, NULL, 1, '2013-05-15 08:33:14.213+02', true, NULL, true, NULL, '$p5k2$1000$P-XuHPKYb4Ijug0XVRj-yw==$UrhGil6jF1ASlZibChfoVIF-9HE=');

INSERT INTO data.users_groups SELECT nextval('data.users_groups_id_seq'), users.id, groups.id FROM data.users AS users, data.groups AS groups WHERE users.username = 'user1' AND groups.name = 'moderators';
INSERT INTO data.users_groups SELECT nextval('data.users_groups_id_seq'), users.id, groups.id FROM data.users AS users, data.groups AS groups WHERE users.username = 'user1' AND groups.name = 'editors';
INSERT INTO data.users_groups SELECT nextval('data.users_groups_id_seq'), users.id, groups.id FROM data.users AS users, data.groups AS groups WHERE users.username = 'user2' AND groups.name = 'moderators';
INSERT INTO data.users_groups SELECT nextval('data.users_groups_id_seq'), users.id, groups.id FROM data.users AS users, data.groups AS groups WHERE users.username = 'user2' AND groups.name = 'editors';
INSERT INTO data.users_groups SELECT nextval('data.users_groups_id_seq'), users.id, groups.id FROM data.users AS users, data.groups AS groups WHERE users.username = 'user3' AND groups.name = 'editors';
INSERT INTO data.users_groups SELECT nextval('data.users_groups_id_seq'), users.id, groups.id FROM data.users AS users, data.groups AS groups WHERE users.username = 'user4' AND groups.name = 'editors';

SELECT setval('data.users_profiles_id_seq', 1000000, true);
INSERT INTO data.users_profiles SELECT nextval('data.users_profiles_id_seq'), users.id, profiles.id FROM data.users AS users, data.profiles AS profiles WHERE users.username = 'user1' and profiles.code = 'Laos';
INSERT INTO data.users_profiles SELECT nextval('data.users_profiles_id_seq'), users.id, profiles.id FROM data.users AS users, data.profiles AS profiles WHERE users.username = 'user2' and profiles.code = 'Peru';

INSERT INTO data.languages(id, english_name, local_name, locale) VALUES
  (3, 'French', 'Français', 'fr'),
  (4, 'Spanish', 'Español', 'es')
;
SELECT setval('data.languages_id_seq', 4, true);
*/