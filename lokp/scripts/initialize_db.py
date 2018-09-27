import os

import sys

import datetime
import transaction
from pyramid.paster import setup_logging, get_appsettings
from sqlalchemy import engine_from_config
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

from lokp.models import DBSession, Base, Language, Status, Permission, Group, \
    User


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri>\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)


def main(argv=sys.argv):
    if len(argv) != 2:
        usage(argv)
    config_uri = argv[1]
    setup_logging(config_uri)
    settings = get_appsettings(config_uri)
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.create_all(engine)

    add_sql_triggers(engine)
    add_initial_values(engine, settings)


def add_sql_triggers(engine):
    engine.execute("""
        CREATE OR REPLACE FUNCTION data.check_uniqueVersionActive() 
        RETURNS TRIGGER AS $check_uniqueVersionActive$
        DECLARE
            active_count integer;
            version_count integer;
        BEGIN
            IF (NEW.fk_status = 2) THEN
                IF (TG_TABLE_NAME = 'activities') THEN
                    SELECT INTO active_count COUNT(*) FROM data.activities WHERE activity_identifier = NEW.activity_identifier AND fk_status = 2;
                ELSIF (TG_TABLE_NAME = 'stakeholders') THEN
                    SELECT INTO active_count COUNT(*) FROM data.stakeholders WHERE stakeholder_identifier = NEW.stakeholder_identifier AND fk_status = 2;
                END IF;
            END IF;
            IF (active_count >= 1) THEN
                IF NOT (active_count = 1 AND TG_OP = 'UPDATE' AND OLD.fk_status = NEW.fk_status) THEN
                    RAISE EXCEPTION 'There can be only one! Only one entry per identifier is allowed to be active in tables stakeholders and activities.';
                END IF;
            END IF;
            IF (TG_TABLE_NAME = 'activities') THEN
                SELECT INTO version_count COUNT(*) FROM data.activities WHERE activity_identifier = NEW.activity_identifier AND version = NEW.version;
            ELSIF (TG_TABLE_NAME = 'stakeholders') THEN
                SELECT INTO version_count COUNT(*) FROM data.stakeholders WHERE stakeholder_identifier = NEW.stakeholder_identifier AND version = NEW.version;
            END IF;
            IF (version_count >= 1) THEN
                IF NOT (version_count = 1 AND TG_OP = 'UPDATE' AND OLD.version = NEW.version) THEN
                    RAISE EXCEPTION 'Not a unique version! Each version number within an identifier must be unique in tables stakeholders and activities.';
                END IF;
            END IF;
            RETURN NEW;
        END;
        $check_uniqueVersionActive$ LANGUAGE plpgsql;""")
    engine.execute(
        "DROP TRIGGER IF EXISTS check_uniqueVersionActive ON data.activities;")
    engine.execute(
        "DROP TRIGGER IF EXISTS check_uniqueVersionActive ON data.stakeholders;")
    engine.execute("""
        CREATE TRIGGER check_uniqueVersionActive \
        BEFORE UPDATE OR INSERT ON data.activities \
        FOR EACH ROW \
        EXECUTE PROCEDURE data.check_uniqueVersionActive();
    """)
    engine.execute("""
        CREATE TRIGGER check_uniqueVersionActive \
        BEFORE UPDATE OR INSERT ON data.stakeholders \
        FOR EACH ROW \
        EXECUTE PROCEDURE data.check_uniqueVersionActive();
    """)


def add_initial_values(engine, settings):

    def _create_id_unique(obj):
        q = DBSession.query(obj.__mapper__).get(obj.id)
        if q is None:
            DBSession.add(obj)
            return obj, True
        return q, False

    with transaction.manager:

        # Languages
        _create_id_unique(Language(
            id=1, english_name='English', local_name='English', locale='en'))

        # Status
        _create_id_unique(Status(
            id=1, name='pending',
            description='Review pending. Not published yet.'))
        _create_id_unique(Status(
            id=2, name='active',
            description='Reviewed and accepted. Currently published.'))
        _create_id_unique(Status(
            id=3, name='inactive',
            description='Inactive. Previously active.'))
        _create_id_unique(Status(
            id=4, name='deleted',
            description='Deleted. Not published anymore.'))
        _create_id_unique(Status(
            id=5, name='rejected',
            description='Reviewed and rejected. Never published.'))
        _create_id_unique(Status(
            id=6, name='edited', description='Edited. Previously pending.'))

        # Permissions
        permission1, __ = _create_id_unique(Permission(
            id=1, name='administer',
            description='Can add key/values and do batch translations.'))
        permission2, __ = _create_id_unique(Permission(
            id=2, name='moderate',
            description='Can make review decisions on reported information.'))
        permission3, __ = _create_id_unique(Permission(
            id=3, name='edit', description='Can report information.'))
        permission4, __ = _create_id_unique(Permission(
            id=4, name='view',
            description='Can see information. (basic permission - '
                        'granted to everyone)'))
        permission5, __ = _create_id_unique(Permission(
            id=5, name='translate',
            description='Can add and modify translations.'))

        # Groups (with Permissions)
        group1, created = _create_id_unique(Group(id=1, name='administrators'))
        if created is True:
            group1.permissions.append(permission1)
            group1.permissions.append(permission3)
            group1.permissions.append(permission4)
        group2, created = _create_id_unique(Group(id=2, name='moderators'))
        if created is True:
            group2.permissions.append(permission2)
            group2.permissions.append(permission3)
            group2.permissions.append(permission4)
        group3, created = _create_id_unique(Group(id=3, name='editors'))
        if created is True:
            group3.permissions.append(permission3)
            group3.permissions.append(permission4)
        group4, created = _create_id_unique(Group(id=4, name='translators'))
        if created is True:
            group4.permissions.append(permission5)

        # Users (Admin user)
        admin_password = settings['lokp.admin_password']
        admin_email = settings['lokp.admin_email']
        try:
            DBSession.query(User).filter(User.username == 'admin').one()
        except (NoResultFound, MultipleResultsFound) as __:
            user = User(
                username='admin', password=admin_password, email=admin_email,
                is_active=True, is_approved=True,
                registration_timestamp=datetime.datetime.now())
            user.groups = [group1, group2, group3, group4]
            DBSession.add(user)
