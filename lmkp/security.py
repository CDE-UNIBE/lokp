import logging

from lmkp.models.database_objects import (
    Group,
    User,
    users_groups,
)
from lmkp.models.meta import DBSession as Session

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
