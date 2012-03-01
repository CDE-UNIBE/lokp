from lmkp.models.meta import DBSession
from lmkp.renderers.renderers import ExtJSTree
from lmkp.security import group_finder
import papyrus
from papyrus.renderers import GeoJSON
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.config import Configurator
from sqlalchemy import engine_from_config

def main(global_config, ** settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)

    # Authentiaction policy
    authnPolicy = AuthTktAuthenticationPolicy('walhalla', callback=group_finder)
    # Authorization policy
    authzPolicy = ACLAuthorizationPolicy()

    config = Configurator(settings=settings,
                          root_factory='lmkp.models.rootfactory.RootFactory')
    config.set_authentication_policy(authnPolicy)
    config.set_authorization_policy(authzPolicy)

    # Add papyrus includes
    config.include(papyrus.includeme)
    config.add_renderer('geojson', GeoJSON())
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('index', '/')
    config.add_route('login', '/login')
    config.add_route('logout', '/logout')
    config.add_route('db_test', '/db_test')
    config.add_route('manage_events', '/manage')
    config.add_route('config', '/config')
    config.add_route('sample_values', '/sample_values/insert')
    config.add_route('delete_sample_values', '/sample_values/delete')
    config.add_route('geo_test', '/geo_test')
    config.add_route('ext_tests', '/tests')

    # Add a renderer to return ExtJS tree configuration objects
    config.add_renderer('extjstree', ExtJSTree())

    # Activities controllers with an api similar to Papyrus
    # Order matters!
    config.add_route('activities_tree', '/activities/tree', request_method='GET')
    config.add_route('activities_count', '/activities/count', request_method='GET')
    config.add_route('activities_read_many', '/activities', request_method='GET')
    config.add_route('activities_read_one', '/activities/{id}', request_method='GET')
    config.add_route('activities_create', '/activities', request_method='POST')

    # Return a JavaScript model
    config.add_route('activities_model', '/app/model/Activity.js')

    # Test
    config.add_route('geojson_test', '/geojson')
    
    config.scan()
    return config.make_wsgi_app()

