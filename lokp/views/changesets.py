from pyramid.httpexceptions import HTTPNotFound
from pyramid.renderers import render_to_response
from pyramid.view import view_config

from lokp.config.customization import get_customized_template_path
from lokp.models import DBSession
from lokp.protocols.changeset_protocol import ChangesetProtocol

changeset_protocol = ChangesetProtocol(DBSession)


@view_config(route_name='changesets_read_latest')
def read_latest(request):

    try:
        output_format = request.matchdict['output']
    except KeyError:
        output_format = 'rss'

    if output_format == 'rss':
        template = 'changesets/latest_rss.mak'
    elif output_format == 'html':
        template = 'changesets/latest_html.mak'
    else:
        raise HTTPNotFound("Requested output format is not supported.")

    templateValues = changeset_protocol.read_many_latest(request)

    return render_to_response(
        get_customized_template_path(request, template),
        templateValues, request)


@view_config(route_name='changesets_read_byuser')
def read_byuser(request):

    try:
        output_format = request.matchdict['output']
    except KeyError:
        output_format = 'rss'

    if output_format == 'rss':
        template = 'changesets/byuser_rss.mak'
    elif output_format == 'html':
        template = 'changesets/byuser_html.mak'
    else:
        raise HTTPNotFound("Requested output format is not supported.")

    templateValues = changeset_protocol.read_many_byuser(request)

    return render_to_response(
        get_customized_template_path(request, template),
        templateValues, request)
