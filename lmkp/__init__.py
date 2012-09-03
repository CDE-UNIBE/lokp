from lmkp.authentication import CustomAuthenticationPolicy
from lmkp.models.meta import DBSession
from lmkp.renderers.renderers import GeoJsonRenderer
from lmkp.renderers.renderers import JavaScriptRenderer
from lmkp.renderers.renderers import JsonRenderer
from lmkp.security import group_finder
from lmkp.subscribers import add_localizer
from lmkp.subscribers import add_renderer_globals
from lmkp.subscribers import add_user
from lmkp.views.errors import forbidden_view
from lmkp.views.errors import notfound_view
import papyrus
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.config import Configurator
from pyramid.events import BeforeRender
from pyramid.events import NewRequest
from sqlalchemy import engine_from_config

def main(global_config, ** settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)

    # Authentiaction policy
    authnPolicy = CustomAuthenticationPolicy('walhalla', callback=group_finder)
    # Authorization policy
    authzPolicy = ACLAuthorizationPolicy()

    config = Configurator(settings=settings,
                          root_factory='lmkp.models.rootfactory.RootFactory')
    config.set_authentication_policy(authnPolicy)
    config.set_authorization_policy(authzPolicy)

    # Add the directory that includes the translations
    config.add_translation_dirs('lmkp:locale/')

    # Add event subscribers
    config.add_subscriber(add_renderer_globals, BeforeRender)
    config.add_subscriber(add_localizer, NewRequest)

    config.add_subscriber(add_user, NewRequest)

    # Add papyrus includes
    config.include(papyrus.includeme)
    # Return a JavaScript model
    #config.add_route('taggroups_model', 'static/app/model/TagGroup.js')
    #config.add_renderer('geojson', GeoJSON())
    config.add_renderer('geojson', GeoJsonRenderer())
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('index', '/')
    config.add_route('login', '/login')
    config.add_route('logout', '/logout')
    config.add_route('db_test', '/db_test')

    # Returns configuration parameters as JSON objects
    config.add_route('yaml_translate_activities', '/config/scan/activities')
    config.add_route('yaml_add_activity_fields', '/config/add/activities')

    config.add_route('yaml_translate_stakeholders', '/config/scan/stakeholders')
    config.add_route('yaml_add_stakeholder_fields', '/config/add/stakeholders')

    config.add_route('config', '/config/form/{parameter}')

    # Manage sample values and tests
    config.add_route('sample_values', '/sample_values/insert')
    config.add_route('delete_sample_values', '/sample_values/delete')
    config.add_route('test_sample_values', '/sample_values/test')

    # Add a renderer to return ExtJS store configuration objects
    config.add_renderer('json', JsonRenderer())

    # Add a renderer to return JavaScript files
    config.add_renderer('javascript', JavaScriptRenderer())

    # Activities controllers with an api similar to Papyrus
    # Order matters!
    config.add_route('activities_read_pending', '/activities/pending')
    # Reads one or many activities and returns GeoJSON Feature or FeatureCollection
    config.add_route('activities_read_many', '/activities', request_method='GET')
    config.add_route('activities_read_one', '/activities/{uid}', request_method='GET')

    # Reviews a pending activity
    config.add_route('activities_review', '/activities/review', request_method='POST')

    # Creates a new activity
    config.add_route('activities_create', '/activities', request_method='POST')

    # Returns a JSON representation of comments to ...
    config.add_route('comments_all', '/comments/{object}/{uid}')
    # Adds a comment
    config.add_route('comment_add', '/comments/add')
    # Deletes a comment
    config.add_route('comment_delete', '/comments/delete')
    
    # Return the history of an activity
    config.add_route('activities_history', '/activities/history/{uid}')

    config.add_route('stakeholders_read_many', '/stakeholders', request_method='GET')
    config.add_route('stakeholders_read_one', '/stakeholders/{uid}', request_method='GET')
    config.add_route('stakeholders_review', '/stakeholders/review', request_method='POST')
    config.add_route('stakeholders_create', '/stakeholders', request_method='POST')
    config.add_route('stakeholders_history', '/stakeholders/history/{uid}')

    # A controller that returns the translation needed in the ExtJS user interface
    config.add_route('ui_translation', '/lang')
    # Return a json with all available languages from DB
    config.add_route('language_store', '/lang/all')
    # Try to add or edit a translation
    config.add_route('edit_translation', '/lang/edit')

    # A view that returns an editing toolbar configuration object
    config.add_route('edit_toolbar_config', '/app/view/EditToolbar.js')
    config.add_route('view_toolbar_config', '/app/view/ViewToolbar.js')
    config.add_route('moderator_toolbar_config', '/app/view/ModeratorToolbar.js')

    config.add_route('context_layers', '/app/view/layers.js')
    # Return a json with all available profiles from disk
    config.add_route('profile_store', '/profiles/all')

    # An user profile page (maybe not needed anymore?)
    # [inserted ../profile/.. to link, otherwise could be conflicting with some usernames ('update', 'json')]
    config.add_route('user_profile', '/users/profile/{userid}')
    # A json representation of user information
    config.add_route('user_profile_json', '/users/json/{userid}')
    # Updates the information of a user
    config.add_route('user_update', '/users/update', request_method='POST')
    # Add a new user
    config.add_route('add_user', '/users/add', request_method='POST')

    # Codes
    config.add_route('codes_files', '/codes/files')
    config.add_route('codes_add', '/codes/add')

    # A WMS proxy
    config.add_route('wms_proxy', '/geoserver/lo/wms', request_method='GET')

    # Changeset protocol, query the changeset
    config.add_route('changesets_read', '/changesets')

    # Evaluation
    config.add_route('evaluation_json', '/evaluation/{temp}')
    # Some (hopefully) nice charts from the evalution
    config.add_route('charts', '/charts')

    # Yet another test
    config.add_route('privileges_test', '/privileges')

    config.add_route('lao_read_activities', '/read/lao/activities')
    config.add_route('lao_read_stakeholders', '/read/lao/stakeholders')
    config.add_route('set_lao_active', '/read/lao/active')

    config.add_route('cambodia_read_stakeholders', '/read/cambodia/stakeholders')
    config.add_route('cambodia_read_activities', '/read/cambodia/activities')
    
    # Error views
    config.add_forbidden_view(forbidden_view)
    config.add_notfound_view(notfound_view)

    config.scan()
    return config.make_wsgi_app()
