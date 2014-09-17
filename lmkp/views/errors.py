from pyramid.security import authenticated_userid
from pyramid.renderers import render_to_response
from pyramid.i18n import TranslationStringFactory

from lmkp.custom import get_customized_template_path

_ = TranslationStringFactory('lmkp')


def forbidden_view(request):

    # user is logged in: show error message
    if authenticated_userid(request):
        request.response.status = 403
        return render_to_response(
            get_customized_template_path(
                request, 'errors/forbidden.mak'), {}, request)

    # user is not logged in: show login form
    else:
        came_from = request.path
        warning = _(u"Please login to access:")
        warning += "<br/>%s" % came_from
        return render_to_response(get_customized_template_path(
            request, 'login_form.mak'), {
                'came_from': came_from,
                'warning': warning
            }, request)


def notfound_view(context, request):
    request.response.status = 404
    return render_to_response(
        get_customized_template_path(request, 'errors/notfound.mak'), {
            'reason': context
        }, request)
