import colander
import deform
from lmkp.models.database_objects import Group
from lmkp.models.database_objects import Profile
from lmkp.models.database_objects import User
from lmkp.models.meta import DBSession as Session
from lmkp.views.profile import _processProfile
from pyramid.httpexceptions import HTTPBadRequest
from pyramid.httpexceptions import HTTPForbidden
from pyramid.response import Response
from pyramid.security import ACLAllowed
from pyramid.security import authenticated_userid
from pyramid.security import has_permission
from pyramid.view import view_config
import re
from sqlalchemy.orm.exc import NoResultFound

@view_config(route_name='user_self_registration', renderer='lmkp:templates/form.mak')
def user_self_registration(request):


    # Get a list of available profiles
    available_profiles = []

    profiles_db = Session.query(Profile)
    for p in profiles_db.all():

        if p.code == 'global':
            # Always insert global on top
            profile = _processProfile(request, p, True)
            if profile is not None:
                available_profiles.insert(0, (profile['profile'], profile['name']))
        else:
            profile = _processProfile(request, p)
            if profile is not None:
                available_profiles.append((profile['profile'], profile['name']))

    # Define a colander Schema for the self registration
    class Schema(colander.Schema):
        profile = colander.SchemaNode(colander.String(),
                                      widget=deform.widget.SelectWidget(values=available_profiles))
        username = colander.SchemaNode(
                                       colander.String(),
                                       default='',
                                       description='User name')
        firstname = colander.SchemaNode(
                                        colander.String(),
                                        default='',
                                        missing=unicode(u''),
                                        description='First name')
        lastname = colander.SchemaNode(
                                       colander.String(),
                                       default='',
                                       missing=unicode(u''),
                                       description='Last name')
        email = colander.SchemaNode(
                                    colander.String(),
                                    default='',
                                    description="Valid email",
                                    validator=_is_valid_email)
    schema = Schema()
    form = deform.Form(schema, buttons=('submit', ), use_ajax=True)

    def succeed():
        """
        """

        return Response('<div id="thanks">Thanks!</div>')

    return render_form(request, form, success=succeed)

def _is_valid_email(node, value):
    """
    Validates if the user input email address seems to be valid.
    """

    email_pattern = re.compile("[a-zA-Z0-9\.\-]*@[a-zA-Z0-9\-\.]*\.[a-zA-Z0-9]*")

    if email_pattern.search(value) is None:
        raise colander.Invalid(node, "%s is not a valid email address" % value)

    return None


def render_form(request, form, appstruct=colander.null, submitted='submit', success=None, readonly=False):
    captured = None

    if submitted in request.POST:
        # the request represents a form submission
        try:
            # try to validate the submitted values
            controls = request.POST.items()
            captured = form.validate(controls)
            if success:
                response = success()
                if response is not None:
                    return response
            html = form.render(captured)
        except deform.ValidationFailure as e:
            # the submitted values could not be validated
            html = e.render()

    else:
        # the request requires a simple form rendering
        html = form.render(appstruct, readonly=readonly)

    if request.is_xhr:
        return Response(html)

    reqts = form.get_widget_resources()

    # values passed to template for rendering
    return {
        'form':html,
        'css_links':reqts['css'],
        'js_links':reqts['js'],
        }

@view_config(route_name='user_profile_json', renderer='json')
def user_profile_json(request):
    """
    This function returns a JSON with information about a user.
    Depending on the rights of the current user it also contains the email address and 
    information about whether the current user has permission to edit this data or not.
    """
    ret = {'success': True, 'editable': False}
    
    # try to find requested user
    try:
        user = Session.query(User).filter(User.username == request.matchdict['userid']).one()
    except NoResultFound:
        ret['success'] = False
        ret['msg'] = 'There is no user with this username.'
        return ret
    
    # collect very basic information (so far just username and -id)
    ret["data"] = {
        'username': user.username,
        'userid': user.id
    }
    
    # if current user is admin, also show email
    if isinstance(has_permission('administer', request.context, request), ACLAllowed):
        ret['data']['email'] = user.email
    
    # if requested user is also current user, also show email and allow to edit
    if authenticated_userid(request) == user.username:
        ret['data']['email'] = user.email
        ret['editable'] = True
    
    return ret

@view_config(route_name='user_update', renderer='json')
def user_update(request):
    """
    This function updates user information and sends back a JSON with 'success'
    (true/false) and 'msg'
    User must be logged in, information can only be changed by the user himself
    and if application is not running in demo mode and username is in ignored.
    """
    ret = {'success': False}

    # List of usernames which cannot be changed when in demo mode
    ignored_demo_usernames = ['editor', 'moderator']
    mode = None
    if 'lmkp.mode' in request.registry.settings:
        if str(request.registry.settings['lmkp.mode']).lower() == 'demo':
            mode = 'demo'

    username = request.POST['username'] if 'username' in request.POST else None
    email = request.POST['email']  if 'email' in request.POST else None
    new_password = request.POST['new_password1'] if 'new_password1' in request.POST else None
    old_password = request.POST['old_password'] if 'old_password' in request.POST else None
    
    if username and (email or (new_password and old_password)):

        # Return error message if in demo mode and username one of the ignored
        if (mode is not None and mode == 'demo'
            and username in ignored_demo_usernames):
            ret['msg'] = 'You are not allowed to change this user in demo mode.'
            return ret

        # try to find requested user
        try:
            user = Session.query(User).filter(User.username == username).one()
            # check privileges (only current user can update his own information)
            if authenticated_userid(request) == user.username:
                # do the update (so far only email)
                if email:
                    user.email = email
                    import transaction
                    transaction.commit()
                    ret['success'] = True
                    ret['msg'] = 'Information successfully updated.'
                # do password update
                elif new_password and old_password:
                    # check old password first
                    if User.check_password(username, old_password):
                        user.password = new_password
                        import transaction
                        transaction.commit()
                        ret['success'] = True
                        ret['msg'] = 'Password successfully updated.'
                    else:
                        ret['msg'] = 'Wrong password.'
            else:
                ret['msg'] = 'You do not have the right to update this information.'
                return ret
        except NoResultFound:
            ret['msg'] = 'There is no user with this username.'
            return ret
    return ret

# TODO: Find out if this is still needed. If not, also delete template. 
@view_config(route_name='user_profile', renderer='lmkp:templates/user.mak')
def get_user_profile(request):
    username = authenticated_userid(request)
    if username != request.matchdict['userid']:
        raise HTTPForbidden
    return {}

@view_config(route_name='add_user', renderer='json', permission='administer')
def add_user(request):
    if 'groups' in request.params:
        requested_groups = request.POST.getall('groups')
    else:
        raise HTTPBadRequest("Missing group parameter")

    if 'username' in request.params:
        username = request.params['username']
    else:
        raise HTTPBadRequest("Missing username parameter")

    if 'email' in request.params:
        email = request.params['email']
    else:
        raise HTTPBadRequest("Missing email parameter")

    if 'password' in request.params:
        password = request.params['password']
    else:
        raise HTTPBadRequest("Missing password parameter")

    # Check email
    email_query = Session.query(User).filter(User.email == email)
    try:
        email_query.one()
        raise HTTPBadRequest('There already exists a user with this email address')
    except NoResultFound:
        pass

    # Check groups
    groups = Session.query(Group).filter(Group.name.in_(requested_groups)).all()
    if len(groups) == 0:
        raise HTTPBadRequest("Invalid group parameter")

    if not _user_exists(User.username, username):
        new_user = User(username=username, password=password, email=email)
        new_user.groups = groups
        return {"success": True, "msg": "New user created successfully."}
    else:
        request.response.status = 400
        return {"success": False, "msg": "User exists."}

def _user_exists(filterColumn, filterAttr):
    if Session.query(User).filter(filterColumn == filterAttr).count() > 0:
        return True

    return False