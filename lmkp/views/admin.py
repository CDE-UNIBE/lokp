from pyramid.view import view_config

@view_config(route_name='admin', renderer='lmkp:templates/index.pt')
def admin(request):
    
    if request is not None and '_LOCALE_' in request.params:
        response = request.response
        response.set_cookie('_LOCALE_', request.params.get('_LOCALE_'))
    
    return {'header': 'Admin View', 'login': True, 'username': 'username', 'script': 'admin'}