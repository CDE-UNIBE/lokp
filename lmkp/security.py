# To change this template, choose Tools | Templates
# and open the template in the editor.
__author__ = "Adrian Weber, Centre for Development and Environment, University of Bern"
__date__ = "$Jan 20, 2012 10:36:32 AM$"

from lmkp.models.database_objects import Group
from lmkp.models.database_objects import User
from lmkp.models.database_objects import users_groups
from lmkp.models.meta import DBSession as Session
import logging
from sqlalchemy.sql import and_
log = logging.getLogger(__name__)

def check_user(username, password):
    """
    Query the database to check the user credentials
    """
    valid = Session.query(User).filter(and_(User.username == username, User.password == password)).count() == 1
    return valid

def group_finder(username, request):
    """
    Finds and returns a user group for a certain user name.
    This function implies that the usernames are unique! Not sure if this is
    true for the data model
    """
    q = Session.query(Group.name).join(users_groups).join(User).filter(User.username == username).limit(1)
    group = q[0][0]
    log.info("Found group: %s" % group )
    return group