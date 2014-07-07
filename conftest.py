# Somewhat based on:
# http://blog.lostpropertyhq.com/testing-with-sqlalchemy-and-pytest/

import pytest
from lmkp.models import meta
import os
from sqlalchemy import engine_from_config
from pyramid.paster import get_appsettings
from lmkp.scripts.populate import _populate
from selenium import webdriver

@pytest.fixture(scope='session')
def connection(request):
    
    config_uri = 'unit_tests.ini'
    settings = get_appsettings(config_uri)
    engine = engine_from_config(settings, 'sqlalchemy.')
    
    meta.Base.metadata.create_all(engine)
    connection = engine.connect()
    meta.DBSession.registry.clear()
    meta.DBSession.configure(bind=connection)
    meta.Base.metadata.bind = engine
    
    _populate(engine, settings)
    
    request.addfinalizer(meta.Base.metadata.drop_all)
    return connection


@pytest.fixture
def db_session(request, connection):
    from transaction import abort
    trans = connection.begin()
    
    here = os.path.dirname(__file__)
    location = os.path.join(here, 'lmkp', 'customization', 'testing', 'scripts', 'populate_keyvalues.sql')
    
    sql_file = open(location, 'r')
    sql_query = sql_file.read()
    sql_file.close()
    connection.execute(sql_query)
    
    request.addfinalizer(trans.rollback)
    request.addfinalizer(abort)
    
    from lmkp.models.meta import DBSession
    return DBSession


browsers = {
    'firefox': webdriver.Firefox,
#    'chrome': webdriver.Chrome,
}

@pytest.fixture
def driver(request):
    #b = browsers[request.param]()
    b = browsers['firefox']()

    request.addfinalizer(lambda *args: b.quit())

    return b
