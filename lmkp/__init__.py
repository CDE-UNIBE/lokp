from lmkp.authentication import CustomAuthenticationPolicy
from lmkp.custom import get_customization_name
from lmkp.models.database_objects import Group
from lmkp.models.database_objects import User
from lmkp.models.meta import DBSession
from lmkp.renderers.renderers import GeoJsonRenderer
from lmkp.renderers.renderers import JavaScriptRenderer
from lmkp.renderers.renderers import JsonRenderer
from lmkp.renderers.renderers import CSVRenderer
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


    # Used when called through Tests
    if 'settings' in settings:
        settings = settings['settings']

    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)

    # Transform the list of valid file mime extensions from the ini file into a
    # python dict.
    # http://pyramid.readthedocs.org/en/latest/narr/environment.html#adding-a-
    # custom-setting
    file_mime_extensions = {}
    for fme in aslist(settings.get('lmkp.file_mime_extensions', {}), False):
        fme_entry = fme.split(' ')
        if len(fme_entry) != 2:
            continue
        file_mime_extensions[fme_entry[0]] = fme_entry[1]
    settings['lmkp.file_mime_extensions'] = file_mime_extensions

    _update_admin_user(DBSession, settings)

    # Customization: Determine the name of the customization
    customization = get_customization_name(settings=settings)

    # Authentication policy
    authnPolicy = CustomAuthenticationPolicy(
        '9ZbfPv Ez-eV8LeTJVNjUhQf FXWBBi_cWKn2fqnpz3PA', callback=group_finder)
    # Authorization policy
    authzPolicy = ACLAuthorizationPolicy()

    session_factory = session_factory_from_settings(settings)

    config = Configurator(settings=settings,
                          root_factory='lmkp.models.rootfactory.RootFactory',
                          session_factory=session_factory)
    config.set_authentication_policy(authnPolicy)
    config.set_authorization_policy(authzPolicy)

    config.include('pyramid_beaker')

    config.include('pyramid_mako')
    config.include('pyramid_chameleon')

    # Add the directories that include the translations, also include the
    # translation directory for the customization
    config.add_translation_dirs(
        'lmkp:locale/',
        'colander:locale/',
        'deform:locale/'
    )
    if customization is not None:
        config.add_translation_dirs(
            'customization/%s/locale/' % customization
        )

    # Add event subscribers
    config.add_subscriber(add_renderer_globals, BeforeRender)
    config.add_subscriber(add_localizer, NewRequest)

    config.add_subscriber(add_user, NewRequest)

    config.include('pyramid_mailer')

    # Add papyrus includes
    config.include(papyrus.includeme)
    config.include('pyramid_handlers')

    # Renderers
    config.add_renderer('geojson', GeoJsonRenderer())
    config.add_renderer('csv', CSVRenderer())
    config.add_renderer('json', JsonRenderer())
    config.add_renderer('javascript', JavaScriptRenderer())

    # Static views
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_static_view('formstatic', 'deform:static')

    # Customization: Add the static customization folder as view
    if customization is not None:
        config.add_static_view(
            'custom', 'customization/%s/static' % customization,
            cache_max_age=3600)

    # Main views
    config.add_route('index', '/')
    config.add_route('administration', '/administration')
    config.add_route("map_view", "/map")
    config.add_route("grid_view", "/grid")
    config.add_route('about_view', '/about')
    config.add_route('faq_view', '/faq')
    config.add_route('showcases_view', '/showcases')
    config.add_route('partners_view', '/partners')

    # Login / Logout
    config.add_route('login', '/login', request_method='POST')
    config.add_route('login_json', '/login/json', request_method='POST')
    config.add_route('login_form', '/login', request_method='GET')
    config.add_route('reset', '/reset', request_method='POST')
    config.add_route('reset_form', '/reset', request_method='GET')
    config.add_route('logout', '/logout')

    # Translation
    config.add_route('yaml_translate_activities', '/config/scan/activities')
    config.add_route('yaml_add_activity_fields', '/config/add/activities')
    config.add_route(
        'yaml_translate_stakeholders', '/config/scan/stakeholders')
    config.add_route('yaml_add_stakeholder_fields', '/config/add/stakeholders')

    # Configuration
    config.add_route('config', '/config/form/{parameter}')
    config.add_route('config_geomtaggroups', '/config/geometrytaggroups')

    # Profiles
    config.add_route('profile_cambodia', '/cambodia')
    config.add_route('profile_laos', '/laos')
    config.add_route('profile_peru', '/peru')
    config.add_route('profile_madagascar', '/madagascar')
    config.add_route('profile_myanmar', '/myanmar')
    config.add_route('profile_global', '/global')

    # Evaluation
    config.add_route('evaluation', '/evaluation', request_method='POST')

    # Charts
    config.add_route("charts_view", "/charts")
    config.add_route('charts_overview', '/charts/overview')
    config.add_route('charts_no_slash', '/charts/{type}*params')
    config.add_route('charts', '/charts/{type}/*params')

    """
    Activities
    """
    # Activities controllers with an api once similar to Papyrus
    # Order matters!

    # Creates a new activity
    config.add_route('activities_create', '/activities', request_method='POST')

    # Reviews a pending activity
    config.add_route(
        'activities_review', '/activities/review', request_method='POST')

    # Read one (special cases)
    config.add_route(
        'activities_read_one_active', '/activities/active/{output}/{uid}')
    config.add_route(
        'activities_read_one_public', '/activities/public/{output}/{uid}')

    # By Stakeholder
    config.add_route(
        'activities_bystakeholders',
        '/activities/bystakeholders/{output}/{uids}')
    config.add_route(
        'activities_bystakeholders_public',
        '/activities/bystakeholders/public/{output}/{uids}')

    # Read many
    config.add_route(
        'activities_public_read_many', '/activities/public/{output}')
    config.add_route('activities_read_many', '/activities/{output}')

    # Read one
    config.add_route('activities_read_one', '/activities/{output}/{uid}')

    # Read one history
    config.add_route(
        'activities_read_one_history', '/activities/history/{output}/{uid}')

    """
    Stakeholders
    """
    # Stakeholders controllers, similar as Activities above
    # Order matters!

    # Creates a new stakeholder
    config.add_route(
        'stakeholders_create', '/stakeholders', request_method='POST')

    # Reviews a pending stakeholder
    config.add_route(
        'stakeholders_review', '/stakeholders/review', request_method='POST')

    # Read one (special cases)
    config.add_route(
        'stakeholders_read_one_active', '/stakeholders/active/{output}/{uid}')
    config.add_route(
        'stakeholders_read_one_public', '/stakeholders/public/{output}/{uid}')

    # By Activities
    config.add_route(
        'stakeholders_byactivities_all', '/stakeholders/byactivities/{output}')
    config.add_route(
        'stakeholders_byactivities_all_public',
        '/stakeholders/byactivities/public/{output}')
    config.add_route(
        'stakeholders_byactivities',
        '/stakeholders/byactivities/{output}/{uids}')
    config.add_route(
        'stakeholders_byactivities_public',
        '/stakeholders/byactivities/public/{output}/{uids}')

    # Read many
    config.add_route('stakeholders_read_many', '/stakeholders/{output}')
    config.add_route(
        'stakeholders_read_many_public', '/stakeholders/public/{output}')

    # Read one
    config.add_route('stakeholders_read_one', '/stakeholders/{output}/{uid}')

    # Read one history
    config.add_route(
        'stakeholders_read_one_history',
        '/stakeholders/history/{output}/{uid}')

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

    """
    Files
    """
    # Embedded form to upload a file
    config.add_route('file_upload_form_embedded', '/files/form')
    config.add_route(
        'file_upload_json_response', '/files/form/json', request_method='POST')
    # Show or download a file
    config.add_route('file_view', '/files/{action}/{identifier}')

    """
    Download
    """
    config.add_route('download', '/download')

    """
    Translation
    """
    # A controller that returns the translation needed in the ExtJS user
    # interface
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
    config.add_route(
        'extractDatabaseTranslation', '/translation/extract/{type}')

    config.add_route('context_layers', '/app/view/layers.js')
    # Return a json with all available profiles from disk
    config.add_route('profile_store', '/profiles/all')

    # An user profile page (maybe not needed anymore?)
    # [inserted ../profile/.. to link, otherwise could be conflicting with
    # some usernames ('update', 'json')]
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

    config.add_route('form_clear_session', '/form/clearsession/{item}/{attr}')

    # A WMS proxy
    config.add_route('wms_proxy', '/geoserver/lo/wms', request_method='GET')
    config.add_route('simple_proxy', '/proxy', request_method='GET')

    # Changeset protocol, query the changeset
    config.add_route('changesets_read', '/changesets')

    # Show a list of latest changesets
    config.add_route('changesets_read_latest', '/changesets/latest/{output}')
    # Show a list of changesets by a user
    config.add_route(
        'changesets_read_byuser', '/changesets/{username}/{output}')

    # A route to the sitemap.xml
    config.add_route('sitemap', '/sitemap.xml')

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
    Reads the init settings at application start up and sets or add the
    admin user with the set password.
    The necessary setting keys are "lmkp.admin_password" and
    "lmkp.admin_email".
    """

    try:
        pw = settings['lmkp.admin_password']
        email = settings['lmkp.admin_email']
    except KeyError:
        raise Exception(
            '"lmkp.admin_password" or "lmkp.admin_email" setting are missing '
            'in configuration file.')

    # Try to get the admin user from the database
    admin_user = Session.query(User).filter(User.username == 'admin').first()

    if admin_user == None:

        admin_group = Session.query(Group).filter(
            Group.name == 'administrators').first()
        admin_user = User(username='admin', password=pw, email=email)
        admin_user.groups.append(admin_group)
        Session.add(admin_user)

    else:
        admin_user.password = pw
        admin_user.email = email

    transaction.commit()
