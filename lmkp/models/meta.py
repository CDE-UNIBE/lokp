from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
)
from zope.sqlalchemy import ZopeTransactionExtension

# wuilly.com/index.php/2011/10/07/uuid-objects-in-pylons-with-sqlalchemy/
import psycopg2.extras
psycopg2.extras.register_uuid()


DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()
