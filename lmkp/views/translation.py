import logging
from pyramid.i18n import TranslationStringFactory
from pyramid.i18n import get_localizer
from pyramid.view import view_config
import simplejson as json

log = logging.getLogger(__name__)

_ = TranslationStringFactory('lmkp')

@view_config(route_name='ui_translation', renderer='string')
def ui_messages(request):

    # A dictionary that contains all messages that need to be tranlated in the
    # user interface.
    # Add new messages to this dict!
    uiMap = {
    'zoom-button': _('zoom-button', default='Zoom'),
    'pan-button': _('pan-button', default='Pan'),
    'file-menu': _('file-menu', default='File'),
    'view-menu': _('view-menu', default='View'),
    }

    # Get the localizer
    localizer = get_localizer(request)

    # Translate the user interface messages
    for i in uiMap:
        uiMap[i] = localizer.translate(uiMap[i])

    # Write the JavaScript and instantiate the global variable Lmkp.ts
    str = "Ext.namespace('Lmkp');\n"
    str += "Lmkp.ts = Ext.create('Ext.util.MixedCollection');\n" #,{\n"

    # Add a new method that returns the requested key instead of undefined
    # if a key does not exist. Use this method in the ExtJS views.
    str += "Lmkp.ts.msg = function(key) {\n"
    str += "\treturn this.containsKey(key) ? this.get(key) : key;\n"
    str += "}\n"

    # Add all translated keys and values to this MixedCollection
    str += "Lmkp.ts.addAll("
    json_ustr = json.dumps(uiMap, ensure_ascii=False, indent=8, sort_keys=True)
    str += json_ustr.encode('utf-8')
    str += ");\n"

    # Make sure to set the correct mime type
    if request is not None:
        response = request.response
        response.content_type = 'application/javascript'

    return str