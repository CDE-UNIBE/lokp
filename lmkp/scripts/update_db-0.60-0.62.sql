UPDATE data.a_keys SET id = 165 WHERE id = 57;
UPDATE data.a_keys SET id = 166 WHERE id = 113;

INSERT INTO data.a_keys(id, fk_a_key, fk_language, key, type, helptext, description, validator) VALUES
  (57, NULL, NULL, 'Remark (Nature of the deal)', 'Text', NULL, NULL, NULL),
  (113, 57, 1, 'Remark', NULL, NULL, NULL, NULL),
  (167, 57, 3, 'Observación', NULL, NULL, NULL, NULL);
SELECT setval('data.a_keys_id_seq', 167, true);