from pyramid.security import authenticated_userid
from pyramid.renderers import render_to_response

def forbidden_view(request):
    
    # user is logged in: show error message
    if authenticated_userid(request):
        return render_to_response('lmkp:templates/errors/forbidden.mak', {}, request)
    
    # user is not logged in: show login form
    else:
        return render_to_response('lmkp:templates/login_form.mak', {'came_from': request.current_route_url()}, request)

def notfound_view(request):
    return render_to_response('lmkp:templates/errors/notfound.mak', {}, request)