from lmkp.models.meta import DBSession as Session
from lmkp.renderers.renderers import translate_key
from lmkp.views.changeset_protocol import ChangesetProtocol
import logging
from pyramid.i18n import TranslationStringFactory
from pyramid.view import view_config

log = logging.getLogger(__name__)

_ = TranslationStringFactory('lmkp')

changeset_protocol = ChangesetProtocol(Session)

#@view_config(route_name='changesets_read', renderer='lmkp:templates/changeset_table.mak')
@view_config(route_name='changesets_read', renderer='json')
def read(request):
    return changeset_protocol.read(request)