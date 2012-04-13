import os
import sys
import transaction

from sqlalchemy import engine_from_config

from pyramid.paster import (
    get_appsettings,
    setup_logging,
    )

from ..models.meta import (
    DBSession,
    Base,
    )

from ..models.database_objects import *

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
    engine.execute("CREATE OR REPLACE FUNCTION data.check_uniqueVersionActive() RETURNS TRIGGER AS $check_uniqueVersionActive$ \
                        DECLARE \
                            active_count integer; \
                            version_count integer; \
                        BEGIN \
                            IF (NEW.fk_status = 2) THEN \
                                IF (TG_TABLE_NAME = 'activities') THEN \
                                    SELECT INTO active_count COUNT(*) FROM data.activities WHERE activity_identifier = NEW.activity_identifier AND fk_status = 2; \
                                ELSIF (TG_TABLE_NAME = 'stakeholders') THEN \
                                    SELECT INTO active_count COUNT(*) FROM data.stakeholders WHERE stakeholder_identifier = NEW.stakeholder_identifier AND fk_status = 2; \
                                END IF; \
                            END IF; \
                            IF (active_count >= 1) THEN \
                                IF NOT (active_count = 1 AND TG_OP = 'UPDATE' AND OLD.fk_status = NEW.fk_status) THEN \
                                    RAISE EXCEPTION 'There can be only one! Only one entry per identifier is allowed to be active in tables stakeholders and activities.'; \
                                END IF; \
                            END IF; \
                            IF (TG_TABLE_NAME = 'activities') THEN \
                                SELECT INTO version_count COUNT(*) FROM data.activities WHERE activity_identifier = NEW.activity_identifier AND version = NEW.version; \
                            ELSIF (TG_TABLE_NAME = 'stakeholders') THEN \
                                SELECT INTO version_count COUNT(*) FROM data.stakeholders WHERE stakeholder_identifier = NEW.stakeholder_identifier AND version = NEW.version; \
                            END IF; \
                            IF (version_count >= 1) THEN \
                                IF NOT (version_count = 1 AND TG_OP = 'UPDATE' AND OLD.version = NEW.version) THEN \
                                    RAISE EXCEPTION 'Not a unique version! Each version number within an identifier must be unique in tables stakeholders and activities.'; \
                                END IF; \
                            END IF; \
                            RETURN NEW; \
                        END; \
                        $check_uniqueVersionActive$ LANGUAGE plpgsql;")
    engine.execute("DROP TRIGGER IF EXISTS check_uniqueVersionActive ON data.activities;")
    engine.execute("DROP TRIGGER IF EXISTS check_uniqueVersionActive ON data.stakeholders;")
    engine.execute("CREATE TRIGGER check_uniqueVersionActive \
                    BEFORE UPDATE OR INSERT ON data.activities \
                    FOR EACH ROW \
                    EXECUTE PROCEDURE data.check_uniqueVersionActive();")
    engine.execute("CREATE TRIGGER check_uniqueVersionActive \
                    BEFORE UPDATE OR INSERT ON data.stakeholders \
                    FOR EACH ROW \
                    EXECUTE PROCEDURE data.check_uniqueVersionActive();")
