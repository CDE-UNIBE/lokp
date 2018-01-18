from logging import getLogger
from pyramid.events import (
    BeforeRender,
    NewRequest,
    subscriber,
)
from pyramid.i18n import (
    TranslationStringFactory,
    TranslationString,
    get_localizer,
)
from pyramid.security import (
    authenticated_userid,
)

from lmkp.custom import get_customization_name
from lmkp.models.database_objects import User
from lmkp.models.meta import DBSession as Session

log = getLogger(__name__)

tsf = TranslationStringFactory('lmkp')
tsf_deform = TranslationStringFactory('deform')
tsf_colander = TranslationStringFactory('colander')


@subscriber(BeforeRender)
def add_renderer_globals(event):
    """
    Thanks to Alexandre Bourget:
    http://blog.abourget.net/2011/1/13/pyramid-and-mako:-how-to-do-i18n-the-
        pylons-way/
    """
    request = event['request']
    event['_'] = request.translate
    event['localizer'] = request.localizer


@subscriber(NewRequest)
def add_localizer(event):
    """
    Thanks to Alexandre Bourget:
    http://blog.abourget.net/2011/1/13/pyramid-and-mako:-how-to-do-i18n-the-
        pylons-way/
    """
    request = event.request
    localizer = get_localizer(request)

    # Create the customized TranslationFactory
    tsf_custom = TranslationStringFactory(
        get_customization_name(request=request))

    def auto_translate(string):
        # Try to translate the string within the [custom] domain
        translation = localizer.translate(tsf_custom(string))
        if (isinstance(string, TranslationString)
            and translation != string.interpolate()
            or not isinstance(string, TranslationString)
                and translation != string):
            return translation

        # If no translation found, try to translate the string within the
        # 'lmkp' domain.
        translation = localizer.translate(tsf(string))
        if (isinstance(string, TranslationString)
            and translation != string.interpolate()
            or not isinstance(string, TranslationString)
                and translation != string):
            return translation

        # If no translation found, try to translate the string within the
        # 'deform' domain.
        translation = localizer.translate(tsf_deform(string))
        if (isinstance(string, TranslationString)
            and translation != string.interpolate()
            or not isinstance(string, TranslationString)
                and translation != string):
            return translation

        # If no translation found, try to translate the string within the
        # 'colander' domain.
        translation = localizer.translate(tsf_colander(string))
        if (isinstance(string, TranslationString)
            and translation != string.interpolate()
            or not isinstance(string, TranslationString)
                and translation != string):
            return translation

        # If no translation was found, return the string as it is.
        if isinstance(string, TranslationString):
            # If it it is a TranslationString, return it interpolated
            return string.interpolate()
        return string
    request.localizer = localizer
    request.translate = auto_translate


def _get_user(request):
    userid = authenticated_userid(request)
#    log.debug("Found user: %s" % userid)
    if userid is not None:
        user = Session.query(User).filter(User.username == userid).first()
        return user


@subscriber(NewRequest)
def add_user(event):
    request = event.request
    request.set_property(_get_user, 'user', reify=True)
