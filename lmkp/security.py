# To change this template, choose Tools | Templates
# and open the template in the editor.
__author__ = "Adrian Weber, Centre for Development and Environment, University of Bern"
__date__ = "$Jan 20, 2012 10:36:32 AM$"

from lmkp.models.database_objects import Group
from lmkp.models.database_objects import User
from lmkp.models.database_objects import users_groups
from lmkp.models.meta import DBSession as Session
import logging
log = logging.getLogger(__name__)

def group_finder(username, request):
    """
    Finds and returns all user groups for a certain user name.
    """
    if username:
        groupQuery = Session.query(
                Group.name
            ).\
            join(users_groups).\
            join(User).\
            filter(User.username == username)
        return ["group:%s" % group.name for group in groupQuery.all()]
    return []