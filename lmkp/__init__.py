from lmkp.authentication import CustomAuthenticationPolicy
from lmkp.models.database_objects import Group
from lmkp.models.database_objects import User
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
from pyramid_beaker import session_factory_from_settings
from pyramid.config import Configurator
from pyramid.events import BeforeRender
from pyramid.events import NewRequest
from pyramid.settings import aslist
from sqlalchemy import engine_from_config
import transaction

def main(global_config, ** settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)

    # Transform the list of valid file mime extensions from the ini file into a
    # python dict.
    # http://pyramid.readthedocs.org/en/latest/narr/environment.html#adding-a-custom-setting
    file_mime_extensions = {}
    for fme in aslist(settings.get('lmkp.file_mime_extensions', {}), False):
        fme_entry = fme.split(' ')
        if len(fme_entry) != 2:
            continue
        file_mime_extensions[fme_entry[0]] = fme_entry[1]
    settings['lmkp.file_mime_extensions'] = file_mime_extensions

    _update_admin_user(DBSession, settings)

    # Authentiaction policy
    authnPolicy = CustomAuthenticationPolicy('9ZbfPv Ez-eV8LeTJVNjUhQf FXWBBi_cWKn2fqnpz3PA', callback=group_finder)
    # Authorization policy
    authzPolicy = ACLAuthorizationPolicy()

    session_factory = session_factory_from_settings(settings)

    config = Configurator(settings=settings,
                          root_factory='lmkp.models.rootfactory.RootFactory',
                          session_factory=session_factory)
    config.set_authentication_policy(authnPolicy)
    config.set_authorization_policy(authzPolicy)

    config.include('pyramid_beaker')
    
    # Add the directory that includes the translations
    config.add_translation_dirs(
        'lmkp:locale/',
        'colander:locale/',
        'deform:locale/'
    )

    # Add event subscribers
    config.add_subscriber(add_renderer_globals, BeforeRender)
    config.add_subscriber(add_localizer, NewRequest)

    config.add_subscriber(add_user, NewRequest)

    config.include('pyramid_mailer')

    # Add papyrus includes
    config.include(papyrus.includeme)
    config.include('pyramid_handlers')
    # Return a JavaScript model
    #config.add_route('taggroups_model', 'static/app/model/TagGroup.js')
    #config.add_renderer('geojson', GeoJSON())
    config.add_renderer('geojson', GeoJsonRenderer())
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_static_view('formstatic', 'deform:static')
    config.add_route('index', '/')
    config.add_route('administration', '/administration')
    config.add_route('login', '/login', request_method='POST')
    config.add_route('login_form', '/login', request_method='GET')
    config.add_route('reset', '/reset', request_method='POST')
    config.add_route('reset_form', '/reset', request_method='GET')
    config.add_route('logout', '/logout')

    config.add_route('translation', '/translation')

    # Embedded start page
    config.add_route('embedded_index', '/embedded/{profile}')
    config.add_route('enclosing_demo_site', '/enclosing_demo_site')

    # Returns configuration parameters as JSON objects
    config.add_route('yaml_translate_activities', '/config/scan/activities')
    config.add_route('yaml_add_activity_fields', '/config/add/activities')

    config.add_route('yaml_translate_stakeholders', '/config/scan/stakeholders')
    config.add_route('yaml_add_stakeholder_fields', '/config/add/stakeholders')

    config.add_route('config', '/config/form/{parameter}')
    config.add_route('config_geomtaggroups', '/config/geometrytaggroups')

    # Manage sample values and tests
    config.add_route('sample_values', '/sample_values/insert')
    config.add_route('delete_sample_values', '/sample_values/delete')
    config.add_route('test_sample_values', '/sample_values/test')
    config.add_route('sample_values_constructed', '/sample_values/constructed')

    # Add a renderer to return ExtJS store configuration objects
    config.add_renderer('json', JsonRenderer())

    # Add a renderer to return JavaScript files
    config.add_renderer('javascript', JavaScriptRenderer())

    config.add_route('profile_cambodia', '/cambodia')
    config.add_route('profile_laos', '/laos')
    config.add_route('profile_peru', '/peru')
    config.add_route('profile_madagascar', '/madagascar')
    config.add_route('profile_global', '/global')

    #
    config.add_route("map_view", "/map")
    config.add_route("grid_view", "/grid")
    config.add_route('about_view', '/about')
    config.add_route('faq_view', '/faq')
    config.add_route('partners_view', '/partners')

    # Charts
    config.add_route("charts_view", "/charts")
    config.add_route('charts_overview', '/charts/overview')

    """
    Activities
    """
    # Activities controllers with an api once similar to Papyrus
    # Order matters!

    # Creates a new activity
    config.add_route('activities_create', '/activities', request_method='POST')

    config.add_route('activities_review_versions_html', '/activities/review/html/{uid}*versions')
    config.add_route('activities_review_versions_json', '/activities/review/json/{uid}*versions')
    config.add_handler('activities_compare_versions',
                       '/activities/compare/{action}/{uid}*versions',
                       'lmkp.views.activity_review.ActivityReview')

    # Reviews a pending activity
    config.add_route('activities_review', '/activities/review', request_method='POST')

    # Read one (special cases)
    config.add_route('activities_read_one_active', '/activities/active/{output}/{uid}')
    config.add_route('activities_read_one_public', '/activities/public/{output}/{uid}')

    # By Stakeholder
    config.add_route('activities_bystakeholder', '/activities/bystakeholder/{output}/{uid}')
    config.add_route('activities_bystakeholder_public', '/activities/bystakeholder/public/{output}/{uid}')

    # Read pending
    config.add_route('activities_read_many_pending', '/activities/pending/{output}')

    # Read many
    config.add_route('activities_public_read_many', '/activities/public/{output}')
    config.add_route('activities_read_many', '/activities/{output}')

    # Read one
    config.add_route('activities_read_one', '/activities/{output}/{uid}')

    """
    Stakeholders
    """
    # Stakeholders controllers, similar as Activities above
    # Order matters!

    # Creates a new stakeholder
    config.add_route('stakeholders_create', '/stakeholders', request_method='POST')

    # Reviews a pending stakeholder
    config.add_route('stakeholders_review_versions_html', '/stakeholders/review/html/{uid}*versions')
    config.add_route('stakeholders_review_versions_json', '/stakeholders/review/json/{uid}*versions')
    config.add_handler('stakeholders_compare_versions',
                       '/stakeholders/compare/{action}/{uid}*versions',
                       'lmkp.views.stakeholder_review.StakeholderReview')
    config.add_route('stakeholders_compare', '/stakeholders/compare/{output}/{uid}')
    config.add_route('stakeholders_review', '/stakeholders/review', request_method='POST')

    # Read one (special cases)
    config.add_route('stakeholders_read_one_active', '/stakeholders/active/{output}/{uid}')
    config.add_route('stakeholders_read_one_public', '/stakeholders/public/{output}/{uid}')

    # By Activity
    config.add_route('stakeholders_byactivity', '/stakeholders/byactivity/{output}/{uid}')
    config.add_route('stakeholders_byactivity_public', '/stakeholders/byactivity/public/{output}/{uid}')

    # Read pending
    config.add_route('stakeholders_read_many_pending', '/stakeholders/pending/{output}')

    # Read many
    config.add_route('stakeholders_read_many', '/stakeholders/{output}')
    config.add_route('stakeholders_read_many_public', '/stakeholders/public/{output}')

    # Read one
    config.add_route('stakeholders_read_one', '/stakeholders/{output}/{uid}')

    """
    Comments
    """
    # Returns a JSON representation of comments to an object
    config.add_route('comments_sitekey', '/comments/sitekey/{uid}')
    config.add_route('comments_all', '/comments/{object}/{uid}')
    # Adds a comment
    config.add_route('comment_add', '/comments/add')
    # Deletes a comment
    config.add_route('comment_delete', '/comments/delete')

    """
    Moderation
    """
    # Moderation overview
    config.add_route('moderation_html', '/moderation')

    # Directly jump to the moderation of a given object
    config.add_route('activities_moderate_item', '/moderation/activities/{uid}')
    config.add_route('stakeholders_moderate_item', '/moderation/stakeholders/{uid}')

    # Tests (not intended for public)
    config.add_route('moderation_tests', '/moderation/ug6uWaef2')

    """
    Files
    """
    # Upload a file
    config.add_route('file_upload', '/files/upload', request_method='POST')
    # Show or download a file
    config.add_route('file_view', '/files/{action}/{identifier}')

    """
    Translation
    """
    # A controller that returns the translation needed in the ExtJS user interface
    config.add_route('ui_translation', '/lang')
    # Return a json with all available languages from DB
    config.add_route('language_store', '/lang/all')
    # Try to add or edit a translation
    config.add_route('edit_translation', '/lang/edit')
    # Scan the directory of translation files
    config.add_route('translation_files', '/translation/files')
    # Do a batch translation based on a file
    config.add_route('translation_batch', '/translation/batch')
    # Extract the translatable strings of the database
    config.add_route('extractDatabaseTranslation', '/translation/extract/{type}')

    # A view that returns an editing toolbar configuration object
    config.add_route('edit_toolbar_config', '/app/view/EditToolbar.js')
    config.add_route('view_toolbar_config', '/app/view/ViewToolbar.js')
    config.add_route('moderator_toolbar_config', '/app/view/ModeratorToolbar.js')

    config.add_route('context_layers', '/app/view/layers.js')
    config.add_route('context_layers2', '/app/view/layers2.js')
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

    config.add_route('user_self_registration', '/users/register')
    config.add_route('user_activation', '/users/activate')
    config.add_route('user_account', '/users/account')
    config.add_route('user_approve', '/users/approve')

    config.add_route('form_clear_session', '/form/clearsession')

    # A WMS proxy
    config.add_route('wms_proxy', '/geoserver/lo/wms', request_method='GET')
    config.add_route('simple_proxy', '/proxy', request_method='GET')

    # Changeset protocol, query the changeset
    config.add_route('changesets_read', '/changesets')

    # Evaluation
    config.add_route('evaluation_json', '/evaluation/{temp}')
    # Some (hopefully) nice charts from the evalution
    config.add_route('charts', '/charts_old')

    # Yet another test
    config.add_route('privileges_test', '/privileges')

    config.add_route('lao_read_activities', '/read/lao/activities')
    config.add_route('lao_read_stakeholders', '/read/lao/stakeholders')
    config.add_route('set_lao_active', '/read/lao/active')

    config.add_route('cambodia_read_stakeholders', '/read/cambodia/stakeholders')
    config.add_route('cambodia_read_activities', '/read/cambodia/activities')

    # Add a route to search locations
    config.add_route('location_search', '/search')

    # A route for ajax queries to get values for a given key
    config.add_route('filterValues', '/json/filtervalues')
    
    # Error views
    config.add_forbidden_view(forbidden_view)
    config.add_notfound_view(notfound_view)

    config.scan()
    return config.make_wsgi_app()

def _update_admin_user(Session, settings):
    """
    Reads the init settings at application start up and sets or add the admin
    user with the set password.
    The necessary setting keys are \"lmkp.admin_password\" and \"lmkp.admin_email\".
    """

    try:
        pw = settings['lmkp.admin_password']
        email = settings['lmkp.admin_email']
    except KeyError:
        raise Exception('\"lmkp.admin_password\" or \"lmkp.admin_email\" setting is missing in configuration file.')

    # Try to get the admin user from the database
    admin_user = Session.query(User).filter(User.username == 'admin').first()

    if admin_user == None:

        admin_group = Session.query(Group).filter(Group.name == 'administrators').first()
        admin_user = User(username='admin', password=pw, email=email)
        admin_user.groups.append(admin_group)
        Session.add(admin_user)

    else:
        admin_user.password = pw
        admin_user.email = email

    transaction.commit()

