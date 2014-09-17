import os
from pyramid.request import Request
from pyramid.testing import DummyRequest


def get_customized_template_path(request, custom_template_path):
    """
    Get the path to the customized templates.

    It is assumed that the templates are situated in a subfolder
    'templates' of the customization folder, eg. inside:
    ``lmkp/customization/{custom}/templates/`` where ``{custom}`` is the
    name of the customization as returned by
    :class:`lmkp.customization.get_customization_name`.

    Args:
        ``request`` (pyramid.request): A :term:`Pyramid` Request object.

        ``custom_template_path`` (str): The relative path to the
        customized template inside the template subfolder of the
        customization folder.

    Returns:
        ``str``. The full path of the customized template which can be
        used by :term:`Pyramid` renderers.
    """
    prefix = get_customization_name(request=request)
    return 'lmkp:customization/%s/templates/%s' % (
        prefix, custom_template_path)


def get_customization_name(request=None, settings=None):
    """
    Return the name of the customization.

    The customization name is defined in the application's ini file as
    the configuration ``lmkp.customization``. A folder with the same
    name needs to exist in ``lmkp/customization/``.

    Kwargs:
        ``request`` (pyramid.request): A :term:`Pyramid` Request object
        which contains a settings dictionary at
        ``request.registry.settings``.
        Either ``request`` or ``settings`` are required.

        ``settings`` (dict): A settings dictionary object.
        Either ``request`` or ``settings`` are required.

    Returns:
        ``str``. The name of the customization.

    Raises:
        ``Exception``. If no customization is specified or if there is
        no folder for the customization.
    """

    if (request and isinstance(request, Request)
            or isinstance(request, DummyRequest)):
        settings = request.registry.settings
    elif not settings or not isinstance(settings, dict):
        raise Exception(
            'You must provide either the request or the settings (dict) '
            'parameters')

    customization = settings.get('lmkp.customization')
    if customization is None:
        raise Exception(
            'No customization specified! There is no customization '
            '(lmkp.customization) specified in the application''s .ini file!')

    # Check if such a folder exists
    if not os.path.exists(os.path.join(
            os.path.dirname(__file__), 'customization', customization)):
        raise Exception(
            'Customization folder not found! The folder for the customization '
            '(%s) is not found. Make sure it is situated at '
            'lmkp/customization/%s.' % (customization, customization))

    return customization
