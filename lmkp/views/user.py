from datetime import datetime
from datetime import timedelta
import logging
import re
import uuid

import colander
import deform
from lmkp.config import getTemplatePath
from lmkp.models.database_objects import Group
from lmkp.models.database_objects import Profile
from lmkp.models.database_objects import User
from lmkp.models.database_objects import users_groups
from lmkp.models.database_objects import users_profiles
from lmkp.models.meta import DBSession as Session
from lmkp.views.profile import _processProfile
from lmkp.views.profile import get_current_locale
from lmkp.views.profile import get_current_profile
from lmkp.views.views import BaseView
from mako.template import Template
import psycopg2.tz
from pyramid.httpexceptions import HTTPBadRequest
from pyramid.httpexceptions import HTTPForbidden
from pyramid.i18n import TranslationStringFactory
from pyramid.i18n import get_locale_name
from pyramid.path import AssetResolver
from pyramid.renderers import render
from pyramid.renderers import render_to_response
from pyramid.response import Response
from pyramid.security import ACLAllowed
from pyramid.security import authenticated_userid
from pyramid.security import has_permission
from pyramid.threadlocal import get_current_request
from pyramid.view import view_config
from sqlalchemy import and_
from sqlalchemy import func
from sqlalchemy.orm.exc import NoResultFound

log = logging.getLogger(__name__)

_ = TranslationStringFactory('lmkp')

lmkpAssetResolver = AssetResolver('lmkp')

def _is_valid_email(node, value):
    """
    Validates if the user input email address seems to be valid.
    """

    email_pattern = re.compile("[a-zA-Z0-9\.\-]*@[a-zA-Z0-9\-\.]*\.[a-zA-Z0-9]*")

    if email_pattern.search(value) is None:
        raise colander.Invalid(node, "%s is not a valid email address." % value)

    return None

def _user_already_exists(node, value):
    """
    Validates the username input field and makes sure that the username does
    not contain special chars and does not yet exist in the database.
    """

    username_pattern = re.compile("^[a-zA-Z0-9\.\-_]+$")

    if username_pattern.search(value) is None:
        raise colander.Invalid(node, "Username '%s' contains invalid characters." % value)

    if Session.query(User).filter(User.username == value).count() > 0:
        raise colander.Invalid(node, "Username '%s' already exists." % value)

    return None

class UserView(BaseView):

    @view_config(route_name='user_self_registration')
    def register(self):
        """
        Returns and process user self registration form.
        """

        _ = self.request.translate

        # Define a colander Schema for the self registration
        class Schema(colander.Schema):
            profile = colander.SchemaNode(colander.String(),
                                          widget=deform.widget.TextInputWidget(template='hidden'),
                                          name='profile',
                                          title='Profile',
                                          default=get_current_profile(self.request),
                                          missing='global'
                                          )
            username = colander.SchemaNode(colander.String(),
                                           validator=_user_already_exists,
                                           title=_('Username'))
            password = colander.SchemaNode(colander.String(),
                                           validator=colander.Length(min=5),
                                           widget=deform.widget.CheckedPasswordWidget(size=20),
                                           title=_('Password'))
            firstname = colander.SchemaNode(colander.String(),
                                            missing=unicode(u''),
                                            title=_('First Name'))
            lastname = colander.SchemaNode(colander.String(),
                                           missing=unicode(u''),
                                           title=_('Last Name'))
            email = colander.SchemaNode(colander.String(),
                                        default='',
                                        title=_("Valid Email"),
                                        validator=_is_valid_email)
        schema = Schema()
        deform.Form.set_default_renderer(mako_renderer)
        form = deform.Form(schema, buttons=('submit', ))

        def succeed():
            """
            """

            # Request all submitted values
            profile_field = self.request.POST.get("profile")
            username_field = self.request.POST.get("username")
            firstname_field = self.request.POST.get("firstname")
            lastname_field = self.request.POST.get("lastname")
            password_field = self.request.POST.get("password")
            email_field = self.request.POST.get("email")

            # Get the selected profile
            selected_profile = Session.query(Profile).filter(Profile.code == profile_field).first()

            # Get the initial user group
            user_group = Session.query(Group).filter(Group.name == "editors").first()

            # Create an activation uuid
            activation_uuid = uuid.uuid4()

            # Create a new user
            new_user = User(username_field, password_field, email_field,
                            firstname=firstname_field,
                            lastname=lastname_field,
                            activation_uuid=activation_uuid,
                            registration_timestamp=datetime.now())
                    
            # Set the user profile
            new_user.profiles = [selected_profile]
            new_user.groups = [user_group]
            # Commit the new user
            Session.add(new_user)

            activation_dict = {
            "firstname": new_user.firstname,
            "lastname": new_user.lastname,
            "activation_link": "http://%s/users/activate?uuid=%s&username=%s" % (self.request.environ['HTTP_HOST'], activation_uuid, new_user.username)
            }
            email_text = render(getTemplatePath(self.request, 'emails/account_activation.mak'),
                                activation_dict,
                                self.request)

            self._send_email([email_field], _(u"Activate your Account"), email_text)

            return render_to_response(getTemplatePath(self.request, 'users/registration_success.mak'), {
                                      }, self.request)

        ret = self._render_form(form, success=succeed)

        # 'ret' is a Response object if the form was submitted with success. In
        # this case, it is not possible to add any parameters to it.
        if not isinstance(ret, Response):
            self._handle_parameters()
            ret['profile'] = get_current_profile(self.request)
            ret['locale'] = get_current_locale(self.request)

            # Render the return values
            return render_to_response(getTemplatePath(self.request, 'users/registration_form.mak'),
                                      ret,
                                      self.request)

        return ret

    def _render_form(self, form, appstruct=colander.null, submitted='submit', success=None, readonly=False):
        """
        Based on method copied from http://deformdemo.repoze.org/allcode?start=70&end=114#line-70
        """
        captured = None

        if submitted in self.request.POST:
            # the request represents a form submission
            try:
                # try to validate the submitted values
                controls = self.request.POST.items()
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

        if self.request.is_xhr:
            return Response(html)

        reqts = form.get_widget_resources()

        # values passed to template for rendering
        return {
            'form':html,
            'css_links':reqts['css'],
            'js_links':reqts['js'],
            }

    @view_config(route_name='user_activation')
    def activate(self):
        """
        """

        activation_uuid = self.request.params.get("uuid")
        username = self.request.params.get("username")

        # Get the user
        user = Session.query(User).filter(and_(User.activation_uuid == activation_uuid, User.username == username, User.is_active == False)).first()
        # Raise a BadRequest if no user is found
        if user is None:
            raise HTTPBadRequest()

        # A timedelta of 48 hours equals 2 days
        delta = timedelta(hours=48)

        # Create a timezone info
        tz = psycopg2.tz.FixedOffsetTimezone(offset=0, name="UTC")

        # Check if the registration timestamp is not older than 48 hours
        if (datetime.now(tz) - delta) > user.registration_timestamp:
            raise HTTPBadRequest("Activation link has been expired.")

        # Set the user active and set the activation uuid to NULL
        user.is_active = True
        user.activation_uuid = None

        approval_dict = {
        "username": user.username,
        "firstname": user.firstname,
        "lastname": user.lastname,
        "email": user.email,
        "profiles": ",".join([p.code for p in user.profiles]),
        "approval_link": "http://%s/users/approve?user=%s&name=%s" % (self.request.environ['HTTP_HOST'], user.uuid, user.username)
        }

        # Send an email to all moderators of the profile in which the user
        # registered.
        email_text = render(getTemplatePath(self.request, 'emails/account_approval_request.mak'),
                            approval_dict,
                            request=self.request)

        # Determine profile. Each user should only have one profile when 
        # registering!
        profiles = [p.code for p in user.profiles]
        if len(profiles) == 0:
            profile = 'global'
        else:
            profile = profiles[0]

        # Find moderators of this profile
        moderators = Session.query(User).\
            join(users_groups).\
            join(Group).\
            join(users_profiles).\
            join(Profile).\
            filter(Group.name == 'moderators').\
            filter(Profile.code == profile)

        # A list with email addresses the email is sent to
        email_addresses = []
        for m in moderators.all():
            email_addresses.append(m.email)

        if len(email_addresses) == 0:
            # If no moderator, try to contact the administrators
            for admin_user in Session.query(User).join(users_groups).join(Group).filter(func.lower(Group.name) == 'administrators'):
                email_addresses.append(admin_user.email)
            log.debug("No moderator found for profile %s. Approval emails will be sent to administrators: %s" % (profile, email_addresses))

        else:
            log.debug("Approval emails will be sent to moderators of %s profile: %s" % (profile, email_addresses))

        # Send the email
        self._send_email(email_addresses,
                         "The Land Observatory: User %s requests approval" % user.username,
                         email_text)

        return render_to_response(getTemplatePath(self.request, 'users/activation_successful.mak'), {
                                  'username': user.username
                                  }, self.request)

    @view_config(route_name="user_approve", permission="moderate")
    def approve(self):
        """
        User moderation: approve newly activated users.
        """

        # Get the URL parameters
        user_uuid = self.request.params.get("user")
        user_username = self.request.params.get("name")

        # Try to the user, who must not yet be approved
        user = Session.query(User).filter(and_(User.uuid == user_uuid, User.username == user_username, User.is_approved == False)).first()
        # Raise a BadRequest if no user is found
        if user is None:
            raise HTTPBadRequest("User is already approved or does not exist in the database.")

        # Set the is_approved attribute to TRUE
        user.is_approved = True

        conf_dict = {
        "firstname": user.firstname,
        "lastname": user.lastname,
        "host": "http://%s" % self.request.environ['HTTP_HOST']
        }

        email_text = render(getTemplatePath(self.request, 'emails/account_approval_confirmation.mak'),
                            conf_dict,
                            request=self.request)

        # Send the email
        self._send_email([user.email],
                         "The Land Observatory: Account confirmation on %s" % "http://%s" % self.request.environ['HTTP_HOST'],
                         email_text)

        # Return the username to the template
        return render_to_response(getTemplatePath(self.request, 'users/approval_successful.mak'), {
                                  'username': user_username
                                  }, self.request)

    @view_config(route_name='user_account', permission='edit')
    def account(self):
        """
        Shows user account details to registered users.
        """

        _ = self.request.translate

        userid = authenticated_userid(self.request)

        # Define a colander Schema for the self registration
        class Schema(colander.Schema):
            username = colander.SchemaNode(
                                           colander.String(),
                                           missing=None,
                                           widget=deform.widget.TextInputWidget(
                                           readonly=True,
                                           readonly_template='readonly/customTextinputReadonly'
                                           ),
                                           title=_('Username')
                                           )
            password = colander.SchemaNode(
                                           colander.String(),
                                           validator=colander.Length(min=5),
                                           widget=deform.widget.CheckedPasswordWidget(size=20),
                                           title=_('Password')
                                           )
            firstname = colander.SchemaNode(
                                            colander.String(),
                                            missing=None,
                                            title=_('First Name')
                                            )
            lastname = colander.SchemaNode(
                                           colander.String(),
                                           missing=None,
                                           title=_('Last Name')
                                           )
            email = colander.SchemaNode(
                                        colander.String(),
                                        missing=None,
                                        widget=deform.widget.TextInputWidget(
                                        readonly=True,
                                        readonly_template='readonly/customTextinputReadonly'
                                        ),
                                        title=_('Valid Email'),
                                        )

        schema = Schema()
        deform.Form.set_default_renderer(mako_renderer)
        form = deform.Form(schema, buttons=(deform.Button(title=_(u'Update'), css_class='btn btn-primary'), ), use_ajax=True)

        # Get the user data
        user = Session.query(User).filter(User.username == userid).first()

        data = {
            'username': user.username,
            'firstname': user.firstname,
            'lastname': user.lastname,
            'email': user.email
        }

        def succeed():
            # Request all submitted values
            profile_field = self.request.POST.get("profile")
            firstname_field = self.request.POST.get("firstname")
            lastname_field = self.request.POST.get("lastname")
            password_field = self.request.POST.get("password")

            # Get the selected profile
            selected_profile = Session.query(Profile).filter(Profile.code == profile_field).first()

            # Update user fields
            user.firstname = firstname_field
            user.lastname = lastname_field
            if password_field is not None and password_field != '':
                user.password = password_field

            # Set the user profile
            user.profiles = [selected_profile]

            return Response('<div class="alert alert-success">%s</div>' % _('Your user settings were updated.'))

        ret = self._render_form(form, success=succeed, appstruct=data)

        if not isinstance(ret, Response):
            self._handle_parameters()
            ret['profile'] = get_current_profile(self.request)
            ret['locale'] = get_current_locale(self.request)
            ret['username'] = user.username

            return render_to_response(getTemplatePath(self.request, 'users/account_form.mak'),
                                      ret,
                                      self.request
                                      )

        return ret

    def _get_available_profiles(self):
        """
        Returns a list of tuples with available profiles. Each tuple contains
        the profile code and profile name.
        """

        # Get a list of available profiles
        available_profiles = []

        # Query all profiles
        for p in Session.query(Profile).all():
            # Insert "global" profile always on top
            if p.code == 'global':
                profile = _processProfile(self.request, p, True)
                if profile is not None:
                    available_profiles.insert(0, (profile['profile'], profile['name']))
            else:
                profile = _processProfile(self.request, p)
                if profile is not None:
                    available_profiles.append((profile['profile'], profile['name']))

        return available_profiles
        

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
        # Create an activation uuid
        activation_uuid = uuid.uuid4()
        # Create a new user
        new_user = User(username=username,
                        password=password,
                        email=email,
                        activation_uuid=activation_uuid,
                        registration_timestamp=datetime.now())
        new_user.groups = groups
        return {"success": True, "msg": "New user created successfully."}
    else:
        request.response.status = 400
        return {"success": False, "msg": "User exists."}

def _user_exists(filterColumn, filterAttr):
    if Session.query(User).filter(filterColumn == filterAttr).count() > 0:
        return True

    return False

def mako_renderer(tmpl_name, ** kw):
    """
    A helper function to use the mako rendering engine.
    It seems to be necessary to locate the templates by using the asset
    resolver.
    """

    if tmpl_name == 'form':
        tmpl_name = 'form_userregistration'

    resolver = lmkpAssetResolver.resolve('templates/form/%s.mak' % tmpl_name)
    template = Template(filename=resolver.abspath())

    # Add the request to the keywords so it is available in the templates.
    request = get_current_request()
    kw['request'] = request

    return template.render( ** kw)
