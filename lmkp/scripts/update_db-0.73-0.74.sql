INSERT INTO data.languages(id, english_name, local_name, locale) VALUES
    (4, 'French', 'Français', 'fr')
;
SELECT setval('data.languages_id_seq', 4, true);