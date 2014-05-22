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
ACTIVITY_HEADER = ["id", "version", "timestamp"]
STAKEHOLDER_HEADER = ["Name", "Country of origin"]
@view_config(route_name='download_all', renderer='csv')
def downloadAll(request):
    """

    """
    # Handle the parameters (locale, profile)
    bv = BaseView(request)
    bv._handle_parameters()

    a_keys = activity_protocol3.read_all_keys(request)["data"]
    activities = activity_protocol3.read_many(request, public=False, offset=0, limit=9999)
    rows = []
    value, year = None, None

    # detect the maximum count of Secondary investors
    max_involvements = max([len(filter(lambda i: i.get("role", "") == "Investor", a.get("involvements", []))) for a in activities.get("data", [])])
    for a in activities.get("data", []):
        activity = []
        for key in ACTIVITY_HEADER:
            activity.append(a.get(key, None))
        # look for all activity values
        for a_key in a_keys:
            for tg in a.get("taggroups", []):
                value, year = None, None
                for t in tg.get("tags", []):
                    if t.get("key") == "Year":
                        year = t.get("value")
                    elif t.get("key") == a_key:
                        value = t.get("value", None)
                if value and year:
                    activity.append(unicode("%s (%s)" %  (value, year)).encode("utf-8"))
                    break
                elif value:
                    activity.append(unicode("%s" %  value).encode("utf-8"))
                    break
            if not value:
                activity.append(None)
        # look for Investor values
        investor_value = None
        for i in filter(lambda i: i.get("role", "") == "Secondary Investor", a.get("involvements", [])):
            for s_key in STAKEHOLDER_HEADER:
                for tg in i.get("data").get("taggroups", []):
                    investor_value = None
                    for t in tg.get("tags", []):
                        if t.get("key") == s_key:
                            investor_value = t.get("value", None)
                    if investor_value:
                        activity.append(unicode("%s" %  investor_value).encode("utf-8"))
                        break
        if not investor_value:
            activity.extend([None, None])
        if a.get("id") == "67c1c192-0b9b-4955-a2a1-4c74d6dbf633":
            import pdb; pdb.set_trace()
        # look for all Secondary Investor values
        secondary_investors = filter(lambda i: i.get("role", "") == "Investor", a.get("involvements", []))
        for i in range(1, max_involvements + 1):
            if i <= len(secondary_investors):
                si = secondary_investors[i-1]
                for s_key in STAKEHOLDER_HEADER:
                    for tg in si.get("data").get("taggroups", []):
                        value = None
                        for t in tg.get("tags", []):
                            if t.get("key") == s_key:
                                value = t.get("value", None)
                        if value:
                            activity.append(unicode("%s" %  value).encode("utf-8"))
                            break
                    if not value:
                        activity.append(None)
            else:
                activity.extend([None, None])


        rows.append(activity)
    HEADER = ACTIVITY_HEADER + a_keys
    HEADER = HEADER + ["Investor: %s" % sv for sv in STAKEHOLDER_HEADER]
    for i in range(1, max_involvements + 1):
        HEADER = HEADER + ["%i. Secondary Investor: %s" % (i, sv) for sv in STAKEHOLDER_HEADER]
    result = {
        "header": HEADER,
        "rows": rows,
    }
    return result

