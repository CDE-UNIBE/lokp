from lmkp.models.database_objects import *
from lmkp.models.meta import DBSession as Session
from lmkp.views.activity_protocol3 import ActivityProtocol3
from lmkp.views.stakeholder_protocol3 import StakeholderProtocol3
from lmkp.views.views import BaseView

import logging
from pyramid.view import view_config


log = logging.getLogger(__name__)


activity_protocol3 = ActivityProtocol3(Session)
stakeholder_protocol3 = StakeholderProtocol3(Session)

HEADER = []
ACTIVITY_HEADER = ["id", "version", "timestamp", "geometry"]
@view_config(route_name='download_all', renderer='csv')
def downloadAll(request):
    """

    """
    # Handle the parameters (locale, profile)
    bv = BaseView(request)
    bv._handle_parameters()

    a_keys = activity_protocol3.read_all_keys(request)["data"]
    sh_keys = stakeholder_protocol3.read_all_keys(request)["data"]
    sh_values_empty = [None]*len(sh_keys)
    activities = activity_protocol3.read_many(request, public=False, offset=0, limit=9999)
    rows = []
    value, year = None, None

    # detect the maximum count of Secondary investors
    max_involvements = max([len(filter(lambda i: i.get("role", "") == "Secondary Investor", a.get("involvements", []))) for a in activities.get("data", [])])
    for a in activities.get("data", []):
        activity = []
        for key in ACTIVITY_HEADER:
            if key == "geometry":
                activity.append(",".join(map(str, a.get(key, {}).get("coordinates", []))))
            else:
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
        # limit Investors to maximum of one
        for i in filter(lambda i: i.get("role", "") == "Investor", a.get("involvements", []))[:1]:
            for s_key in sh_keys:
                for tg in i.get("data").get("taggroups", []):
                    investor_value = None
                    for t in tg.get("tags", []):
                        if t.get("key") == s_key:
                            investor_value = t.get("value", None)
                    if investor_value:
                        activity.append(unicode("%s" %  investor_value).encode("utf-8"))
                        break
                if not investor_value:
                    activity.append(None)
        # look for all Secondary Investor values
        investor_value = None
        secondary_investors = filter(lambda i: i.get("role", "") == "Secondary Investor", a.get("involvements", []))
        for i in range(1, max_involvements + 1):
            if i <= len(secondary_investors):
                si = secondary_investors[i-1]
                for s_key in sh_keys:
                    for tg in si.get("data").get("taggroups", []):
                        investor_value = None
                        for t in tg.get("tags", []):
                            if t.get("key") == s_key:
                                investor_value = t.get("value", None)
                        if investor_value:
                            activity.append(unicode("%s" %  investor_value).encode("utf-8"))
                            break
                    if not investor_value:
                        activity.append(None)
            else:
                activity.extend(sh_values_empty)


        rows.append(activity)
    HEADER = ACTIVITY_HEADER + a_keys
    HEADER = HEADER + ["Investor: %s" % sv for sv in sh_keys]
    for i in range(1, max_involvements + 1):
        HEADER = HEADER + ["%i. Secondary Investor: %s" % (i, sv) for sv in sh_keys]
    result = {
        "header": HEADER,
        "rows": rows,
    }
    return result

