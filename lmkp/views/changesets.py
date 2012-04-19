from lmkp.models.meta import DBSession as Session
from lmkp.views.changeset_protocol import ChangesetProtocol
import logging
from pyramid.view import view_config

log = logging.getLogger(__name__)

changeset_protocol = ChangesetProtocol(Session)

@view_config(route_name='changesets_read', renderer='json')
def read(request):
    return changeset_protocol.read(request)