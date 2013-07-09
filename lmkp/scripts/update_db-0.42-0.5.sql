INSERT INTO data.categories(id, name, type, fk_language, description, fk_category) VALUES
  (51, NULL, 1, 'Contract date', 'Date', NULL, NULL, NULL)
;
SELECT setval('data.a_keys_id_seq', 51, true);