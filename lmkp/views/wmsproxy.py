from pyramid.httpexceptions import HTTPForbidden
from pyramid.view import view_config
import urllib2

@view_config(route_name='wms_proxy', renderer='string')
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
        return HTTPForbidden("%s method is not allowed on this proxy." % (request.method,))

    if host not in allowedHosts:
        return HTTPForbidden("This proxy does not allow you to access that location (%s)." % (host,))

    f = urllib2.urlopen(url)
    
    request.response.content_type = 'text/xml'
    return f.read()