SELECT activities.id, CAST(activity_identifier AS varchar),
status.name,
activities.version,
activities.point,
users.username
FROM data.activities
JOIN data.status ON data.activities.fk_status = data.status.id
JOIN data.a_changesets ON data.a_changesets.fk_activity = data.activities.id
JOIN data.users ON data.a_changesets.fk_user = data.users.id
WHERE status.name = 'active' OR status.name = 'pending';