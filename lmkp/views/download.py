from lmkp.models.database_objects import *
from lmkp.models.meta import DBSession as Session
from lmkp.views.activity_protocol3 import ActivityProtocol3
from lmkp.views.comments import comments_sitekey
from lmkp.views.config import get_mandatory_keys
from lmkp.config import check_valid_uuid
from lmkp.config import getTemplatePath
import logging
import urllib
from pyramid.httpexceptions import HTTPBadRequest
from pyramid.httpexceptions import HTTPForbidden
from pyramid.httpexceptions import HTTPFound
from pyramid.httpexceptions import HTTPNotFound
from pyramid.httpexceptions import HTTPUnauthorized
from pyramid.httpexceptions import HTTPInternalServerError
from pyramid.i18n import get_localizer
from pyramid.i18n import TranslationStringFactory
from pyramid.renderers import render_to_response
from pyramid.response import Response
from pyramid.security import ACLAllowed
from pyramid.security import authenticated_userid
from pyramid.security import has_permission
from pyramid.view import view_config
import yaml
import json

from lmkp.views.activity_review import ActivityReview
from lmkp.renderers.renderers import translate_key
from lmkp.views.form import renderForm
from lmkp.views.form import renderReadonlyForm
from lmkp.views.form import renderReadonlyCompareForm
from lmkp.views.form import checkValidItemjson
from lmkp.views.form_config import getCategoryList
from lmkp.views.profile import get_current_profile
from lmkp.views.profile import get_current_locale
from lmkp.views.profile import get_spatial_accuracy_map
from lmkp.views.views import BaseView
from lmkp.authentication import checkUserPrivileges
from lmkp.views.translation import get_translated_status
from lmkp.views.translation import get_translated_db_keys

log = logging.getLogger(__name__)

_ = TranslationStringFactory('lmkp')

activity_protocol3 = ActivityProtocol3(Session)

HEADER = []
ACTIVITY_VALUES = ["id", "version", "timestamp"]

@view_config(route_name='download_all', renderer='csv')
def downloadAll(request):
    """
    Read many, returns also pending Activities by currently logged in user and
    all pending Activities if logged in as moderator.
    Default output format: JSON
    """
    # Handle the parameters (locale, profile)
    bv = BaseView(request)
    bv._handle_parameters()

    a_keys = activity_protocol3.read_all_keys(request)["data"]
    activities = activity_protocol3.read_many(request, public=False)
    rows = []
    value, year = None, None
    for a in activities.get("data", []):
        activity = []
        for key in ACTIVITY_VALUES:
            activity.append(a.get(key, None))
        for a_key in a_keys:
            for tg in a.get("taggroups", []):
                value, year = None, None
                for t in tg.get("tags", []):
                    if t.get("key") == "Year":
                        year = t.get("value")
                    elif t.get("key") == a_key:
                        value = t.get("value", None)
                if value and year:
                    activity.append("%s %s" %  (value, year))
                    break;
                elif value:
                    activity.append("%s" %  value)
                    break;
            if not value:
                activity.append(None)
        rows.append(activity)
    HEADER = ACTIVITY_VALUES + a_keys
    result = {
        "header": HEADER,
        "rows": rows,
    }
    return result

