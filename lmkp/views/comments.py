from pyramid.view import view_config

from lmkp.models.database_objects import *
from lmkp.models.meta import DBSession as Session

import uuid

@view_config(route_name='comments_all', renderer='json')
def comments_all(request):
    ret = {'success': False}
    
    # collect needed values
    object = request.matchdict.get('object', None)
    uid = request.matchdict.get('uid', None)
    
    # check if needed values are available
    if object is None or uid is None:
        return ret
    
    if object == 'activity':
        # check if parameter 'uid' is a valid UUID
        try:
            uuid.UUID(uid)
        except ValueError:
            ret['message'] = 'Not a valid UUID.'
            return ret
        
        # look for comments
        comments = Session.query(Comment).filter(Comment.fk_activity == uid).all()
        ret['comments'] = []
        for c in comments:
            ret['comments'].append({
                'id': c.id,
                'comment': c.comment,
                'timestamp': str(c.timestamp),
                'userid': c.user.id if c.user is not None else None,
                'username': c.user.username if c.user is not None else None
            })
        ret['total'] = len(comments)
    
    elif object == 'stakeholder':
        ret['message'] = 'Stakeholder comments are not yet implemented.'
        return ret
    
    elif object == 'involvement':
        ret['message'] = 'Involvement comments are not yet implemented.'
        return ret
    
    else:
        ret['message'] = 'Object not found.'
        return ret
    
    # if we've come this far, set success to 'True'
    ret['success'] = True
    
    return ret