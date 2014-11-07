from pyramid.renderers import render_to_response
from pyramid.i18n import TranslationStringFactory

from lmkp.authentication import get_user_privileges
from lmkp.custom import get_customized_template_path
from lmkp.views.views import BaseView

_ = TranslationStringFactory('lmkp')


def forbidden_view(request):
    """
    Return the 403 Forbidden page if the user is logged in but has no
    permissions to view the page. The login page is returned if the user
    is not logged in.

    Args:
        ``request`` (pyramid.request): A :term:`Pyramid` Request object

    Returns:
        ``HTTPResponse``. A HTML response.
    """
    view = BaseView(request)

    is_logged_in, __ = get_user_privileges(request)

    # User is already logged in, show error message
    if is_logged_in:

        request.response.status = 403

        return render_to_response(
            get_customized_template_path(request, 'errors/forbidden.mak'),
            view.get_base_template_values(), request)

    # User is not logged in: show login form
    else:
        came_from = request.url
        warning = _(u"Please login to access:")
        warning += "<br/>%s" % came_from
        template_values = view.get_base_template_values()
        template_values.update({
            'came_from': came_from,
            'warning': warning
        })
        return render_to_response(
            get_customized_template_path(request, 'login_form.mak'),
            template_values, request)


def notfound_view(request):
    """
    Return the 404 Not Found page.

    Args:
        ``request`` (pyramid.request): A :term:`Pyramid` Request object

    Returns:
        ``HTTPResponse``. A HTML response.
    """

    def _foo():
        """
        A stub function doing nothing. Used because the template
        requires a function request.current_route_url.
        """
        pass

    request.response.status = 404
    request.current_route_url = _foo

    view = BaseView(request)
    return render_to_response(
        get_customized_template_path(request, 'errors/notfound.mak'),
        view.get_base_template_values(), request)
