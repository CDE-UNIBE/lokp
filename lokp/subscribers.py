from pyramid.events import NewRequest, subscriber, BeforeRender
from pyramid.i18n import get_localizer, TranslationStringFactory, \
    TranslationString
from pyramid.security import authenticated_userid

from lokp.models import DBSession
from lokp.config.customization import get_customization_name
from lokp.models import User

tsf = TranslationStringFactory('lokp')
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


@subscriber(NewRequest)
def add_user(event):

    def _get_user(request):
        userid = authenticated_userid(request)
    #    log.debug("Found user: %s" % userid)
        if userid is not None:
            user = DBSession.query(User).filter(User.username == userid).first()
            return user

    request = event.request
    request.set_property(_get_user, 'user', reify=True)
