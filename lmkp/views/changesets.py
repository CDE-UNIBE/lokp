from lmkp.config import getTemplatePath
from lmkp.models.meta import DBSession as Session
from lmkp.views.changeset_protocol import ChangesetProtocol
import logging
from pyramid.httpexceptions import HTTPNotFound
from pyramid.renderers import render_to_response
from pyramid.view import view_config

log = logging.getLogger(__name__)

changeset_protocol = ChangesetProtocol(Session)

@view_config(route_name='changesets_read', renderer='json')
def read(request):
    return changeset_protocol.read(request)

@view_config(route_name='changesets_read_latest')
def read_latest(request):

    try:
        output_format = request.matchdict['output']
    except KeyError:
        output_format = 'rss'

    if output_format == 'rss':
        template = 'changesets/latest_rss.mak'
    else:
        raise HTTPNotFound("Requested output format is not supported.")

    templateValues = changeset_protocol.read_many_latest(request)

    return render_to_response(getTemplatePath(request, template),
                              templateValues, request)