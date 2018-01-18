from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.config import Configurator
from pyramid.events import NewRequest, BeforeRender
from pyramid_beaker import session_factory_from_settings
from sqlalchemy import engine_from_config

from lokp.authentication import group_finder, CustomAuthenticationPolicy
from lokp.config.customization import get_customization_name
from lokp.models import DBSession, Base
from lokp.renderers import JavaScriptRenderer, CSVRenderer
from lokp.subscribers import add_localizer, add_renderer_globals, add_user


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine

    # Customization: Determine the name of the customization
    customization = get_customization_name(settings=settings)

    session_factory = session_factory_from_settings(settings)

    config = Configurator(
        settings=settings, root_factory='lokp.authentication.RootFactory',
        session_factory=session_factory)
    config.include('pyramid_mako')

    # Authentication policy
    authn_policy = CustomAuthenticationPolicy(
        settings['lokp.secret'], callback=group_finder,
        hashalg='sha512')
    # Authorization policy
    authz_policy = ACLAuthorizationPolicy()
    config.set_authentication_policy(authn_policy)
    config.set_authorization_policy(authz_policy)

    # Add the directories that include the translations, also include the
    # translation directory for the customization
    config.add_translation_dirs(
        'lokp:locale/',
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

    # Renderers
    config.add_renderer('javascript', JavaScriptRenderer())
    config.add_renderer('csv', CSVRenderer())

    # Static views
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_static_view('formstatic', 'deform:static')
    # Add the static customization folder as view
    if customization is not None:
        config.add_static_view(
            'custom', 'customization/%s/static' % customization,
            cache_max_age=3600)

    """
    Main views
    """
    config.add_route('index', '/')
    config.add_route("map_view", "/map")
    config.add_route("grid_view", "/grid")
    config.add_route('about_view', '/about')
    config.add_route('faq_view', '/faq')
    config.add_route('partners_view', '/partners')

    """
    Login / Logout
    """
    config.add_route('login', '/login', request_method='POST')
    config.add_route('login_json', '/login/json', request_method='POST')
    config.add_route('login_form', '/login', request_method='GET')
    config.add_route('reset', '/reset', request_method='POST')
    config.add_route('reset_form', '/reset', request_method='GET')
    config.add_route('logout', '/logout')

    """
    Profiles
    """
    # Add additional profiles here
    config.add_route('profile_myanmar', '/myanmar')
    config.add_route('profile_global', '/global')

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

    """
    Filter
    """
    # A route for ajax queries to get values for a given key
    config.add_route('filterValues', '/json/filtervalues')

    """
    Configuration
    """
    config.add_route('config_geomtaggroups', '/config/geometrytaggroups')

    """
    Charts
    """
    config.add_route('charts_overview', '/charts/overview')
    config.add_route('charts_no_slash', '/charts/{type}*params')
    config.add_route('charts', '/charts/{type}/*params')
    config.add_route('evaluation', '/evaluation', request_method='POST')

    """
    Map
    """
    config.add_route('context_layers', '/app/view/layers.js')

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
    User management
    """
    config.add_route('user_profile_json', '/users/json/{userid}')
    config.add_route('user_update', '/users/update', request_method='POST')
    config.add_route('add_user', '/users/add', request_method='POST')
    config.add_route('user_self_registration', '/users/register')
    config.add_route('user_activation', '/users/activate')
    config.add_route('user_account', '/users/account')
    config.add_route('user_approve', '/users/approve')

    """
    Changesets
    """
    config.add_route('changesets_read_latest', '/changesets/latest/{output}')
    config.add_route(
        'changesets_read_byuser', '/changesets/{username}/{output}')

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
    config.add_route('activities_read_many', '/activities/{output}')
    config.add_route(
        'activities_public_read_many', '/activities/public/{output}')

    # # Read one
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

    config.scan()
    return config.make_wsgi_app()
