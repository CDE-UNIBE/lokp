from lmkp.models.database_objects import (
    User
)
from lmkp.models.meta import DBSession as Session
from sqlalchemy.orm.exc import NoResultFound

from pyramid.security import (
    authenticated_userid,
    has_permission,
    ACLAllowed
)
from pyramid.httpexceptions import HTTPForbidden
from pyramid.view import view_config
from pyramid.renderers import render_to_response

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
    
    username = request.POST['username'] or None
    email = request.POST['email'] or None
    
    if username and email:
        # try to find requested user
        try:
            user = Session.query(User).filter(User.username == username).one()
            # check privileges (only current user can update his own information)
            if authenticated_userid(request) == user.username:
                # do the update (so far only email)
                user.email = email
                import transaction
                transaction.commit()
                ret['success'] = True
                ret['msg'] = 'Information successfully updated.'
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
