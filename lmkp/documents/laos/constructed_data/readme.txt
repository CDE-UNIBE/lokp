Use pg_restore to populate database.

Add constructed Activities:
curl -u "admin:adsf" -d @lmkp/documents/laos/constructed_data/activities.json -H "Content-Type: application/json" http://localhost:6543/activities?_PROFILE_=LA

Add constructed Stakeholders:
curl -u "admin:adsf" -d @lmkp/documents/laos/constructed_data/stakeholders.json -H "Content-Type: application/json" http://localhost:6543/stakeholders?_PROFILE_=LA

Set them active:
-- Activities
-- Set them all to 'inactive'
UPDATE data.activities
SET fk_status = 3
WHERE activity_identifier IN 
	(
		'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa1',
		'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa2', 
		'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa3'
	);
-- Set the latest version of each Activity to 'active'
UPDATE data.activities
SET fk_status = 2 
WHERE id IN (
        SELECT b.id
        FROM (
                SELECT activity_identifier, max(version) AS maxversion
                FROM data.activities
				WHERE activity_identifier IN 
					(
						'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa1',
						'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa2', 
						'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa3'
					)
                GROUP BY activity_identifier
        ) AS a
        INNER JOIN data.activities AS b ON b.activity_identifier = a.activity_identifier AND b.version = a.maxversion
);
-- Stakeholders
-- Set them all to 'inactive'
UPDATE data.stakeholders
SET fk_status = 3
WHERE stakeholder_identifier IN 
	(
		'00000000-0000-0000-0000-000000000001',
		'00000000-0000-0000-0000-000000000002', 
		'00000000-0000-0000-0000-000000000003', 
		'00000000-0000-0000-0000-000000000004', 
		'00000000-0000-0000-0000-000000000005',
		'00000000-0000-0000-0000-000000000006'
	);
-- Set the latest version of each Stakeholder to 'active'
UPDATE data.stakeholders
SET fk_status = 2 
WHERE id IN (
        SELECT b.id
        FROM (
                SELECT stakeholder_identifier, max(version) AS maxversion
                FROM data.stakeholders
				WHERE stakeholder_identifier IN
					(
						'00000000-0000-0000-0000-000000000001',
						'00000000-0000-0000-0000-000000000002', 
						'00000000-0000-0000-0000-000000000003', 
						'00000000-0000-0000-0000-000000000004', 
						'00000000-0000-0000-0000-000000000005',
						'00000000-0000-0000-0000-000000000006'
					)
                GROUP BY stakeholder_identifier
        ) AS a
        INNER JOIN data.stakeholders AS b ON b.stakeholder_identifier = a.stakeholder_identifier AND b.version = a.maxversion
);