from lmkp.models.database_objects import Group
from lmkp.models.database_objects import User
from lmkp.models.meta import DBSession as Session
from pyramid.httpexceptions import HTTPBadRequest
from pyramid.httpexceptions import HTTPForbidden
from pyramid.renderers import render_to_response
from pyramid.security import ACLAllowed
from pyramid.security import authenticated_userid
from pyramid.security import has_permission
from pyramid.view import view_config
from sqlalchemy.orm.exc import NoResultFound
from lmkp.views.translation import usergroupMap

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
    This function updates user information and sends back a JSON with 'success' (true/false) and 'msg'
    User must be logged in, information can only be changed by the user himself.
    """
    ret = {'success': False}
    
    username = request.POST['username'] if 'username' in request.POST else None
    email = request.POST['email']  if 'email' in request.POST else None
    new_password = request.POST['new_password1'] if 'new_password1' in request.POST else None
    old_password = request.POST['old_password'] if 'old_password' in request.POST else None
    
    if username and (email or (new_password and old_password)):
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
        request.response.status= 400
        return {"success": False, "msg": "User exists."}

def _user_exists(filterColumn, filterAttr):
    if Session.query(User).filter(filterColumn == filterAttr).count() > 0:
        return True

    return False