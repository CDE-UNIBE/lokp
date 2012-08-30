import logging
from pyramid.httpexceptions import HTTPForbidden
from pyramid.httpexceptions import HTTPNotFound
from pyramid.security import unauthenticated_userid
from pyramid.view import view_config
from urllib import urlencode
from urllib2 import HTTPError
from urllib2 import URLError
from urllib2 import urlopen

log = logging.getLogger(__name__)

def wms_proxy(request):
    """
    This is a blind proxy that we use to get around browser
    restrictions that prevent the Javascript from loading pages not on the
    same server as the Javascript.  This has several problems: it's less
    efficient, it might break some sites, and it's a security risk because
    people can use this proxy to browse the web and possibly do bad stuff
    with it.  It only loads pages via http and https, but it can load any
    content type. It supports GET and POST requests.
    Copied from http://trac.osgeo.org/openlayers/browser/trunk/openlayers/examples/proxy.cgi
    """

    allowedHosts = ['localhost:8080']

    url = request.params['url']
    host = url.split("/")[2]

    if request.method != 'GET':
        return HTTPForbidden("%s method is not allowed on this proxy." % (request.method, ))

    if host not in allowedHosts:
        return HTTPForbidden("This proxy does not allow you to access that location (%s)." % (host, ))

    f = urllib2.urlopen(url)
    
    request.response.content_type = 'text/xml'
    return f.read()

@view_config(route_name='wms_proxy', renderer='string')
def wms(request):

    if request.method != 'GET':
        raise HTTPForbidden("%s method is not allowed on this proxy." % (request.method, ))

    # Get the base WMS url from the .ini settings file
    geoserver_url = request.registry.settings['lmkp.base_wms']

    params = {}

    # Make sure all keys are in upper case
    for item in request.params.iteritems():
        params[item[0].upper()] = item[1]

    # Overwrite the CQL filter
    current_user = unauthenticated_userid(request)
    if current_user != None:
        params['CQL_FILTER'] = "(name='active') OR (username='%s' AND name='pending')" % current_user
    else:
        params['CQL_FILTER'] = "(name='active')"

    try:
        f = urlopen(geoserver_url, urlencode(params))
    except HTTPError:
        raise HTTPNotFound()
    # URLError is raised in case of network outage
    except URLError:
        raise HTTPNotFound()

    # Set the correct response type:
    if params['REQUEST'] == 'GetMap':
        request.response.content_type = 'image/png'
    elif params['REQUEST'] == 'GetFeatureInfo':
        request.response.content_type = 'text/xml'
    
    return f.read()


