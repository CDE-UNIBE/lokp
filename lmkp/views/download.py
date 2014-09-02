from pyramid.view import view_config

from lmkp.models.meta import DBSession as Session
from lmkp.views.activities import _handle_spatial_parameters
from lmkp.views.activity_protocol3 import ActivityProtocol3
from lmkp.views.form_config import getCategoryList
from lmkp.views.protocol import (
    get_main_keys_from_item_json,
    get_value_by_key_from_item_json,
)
from lmkp.views.stakeholder_protocol3 import StakeholderProtocol3
from lmkp.views.views import BaseView


activity_protocol = ActivityProtocol3(Session)
stakeholder_protocol = StakeholderProtocol3(Session)


class DownloadView(BaseView):

    @view_config(route_name='download_all', renderer='csv')
    def downloadAll(self):
        """

        """
        header, rows = to_table(self.request)

        return {
            "header": header,
            "rows": rows,
        }


def to_table(request, involvements=True):

    ACTIVITY_HEADER = ['id', 'version', 'timestamp', 'geometry']

    config_taggroups = []
    max_involvements = 0

    # Collect the taggroups based on the form configuration.
    category_list = getCategoryList(request, 'activities')
    for config_taggroup in category_list.getAllTaggroups():
        config_taggroup_entry = {
            'repeat': config_taggroup.getRepeatable(),
            'count': 0,
            'main_key': config_taggroup.getMaintag().getKey().
            getTranslatedName()
        }
        keys = []
        for tag in config_taggroup.getTags():
            keys.append(tag.getKey().getTranslatedName())
        config_taggroup_entry['keys'] = keys[::-1]
        config_taggroups.append(config_taggroup_entry)

    # Apply the spatial filter and query the Activities with the protocol.
    _handle_spatial_parameters(request)
    activities = activity_protocol.read_many(request, public=True)

    # Find out how many times each taggroup appears. This defines how many
    # columns are needed in the table.
    for activity in activities.get('data', []):

        # Taggroups (based on their maintags) of the Activity
        current_main_keys = []
        for main_key in get_main_keys_from_item_json(activity):
            main_key_already_found = next(
                (i for i in current_main_keys if i['key'] == main_key), None)
            if main_key_already_found:
                main_key_already_found['count'] += 1
            else:
                current_main_keys.append({'key': main_key, 'count': 1})

        # Compare it to the previous maximum count
        for activity_main_key in current_main_keys:
            config_main_key = next((
                i for i in config_taggroups if i['main_key']
                == activity_main_key['key']), None)
            if config_main_key is not None:
                config_main_key['count'] = max(
                    config_main_key['count'], activity_main_key['count'])

        # Also count involvements
        if involvements:
            max_involvements = max(max_involvements, len(
                activity.get('involvements', [])))

    # Create the headers
    header = []
    header.extend(ACTIVITY_HEADER)
    for config_taggroup in config_taggroups:
        for i in range(max(config_taggroup.get('count'), 1)):
            for a_key in config_taggroup.get('keys', []):
                if (config_taggroup.get('repeat')
                        or config_taggroup.get('count') > 1):
                    header.append('%s_%s' % (a_key, i + 1))
                else:
                    header.append(a_key)
    if involvements:
        sh_category_list = getCategoryList(request, 'stakeholders')
        sh_keys = [
            i[0] for i in sh_category_list.getInvolvementOverviewKeyNames()]

        involvement_header = sh_keys + ['inv_role', 'inv_id']
        for i in range(max_involvements):
            for inv_header in involvement_header:
                header.append('%s_%s' % (inv_header, i + 1))

    rows = []
    for activity in activities.get('data', []):
        row = []
        for key in ACTIVITY_HEADER:
            if key == 'geometry':
                row.append(",".join(
                    map(str, activity.get(key, {}).get("coordinates", []))))
            else:
                row.append(activity.get(key, None))
        for config_taggroup in config_taggroups:
            taggroups = []
            for taggroup in activity.get('taggroups', []):
                if taggroup['main_tag']['key'] != config_taggroup['main_key']:
                    continue
                for a_key in config_taggroup.get('keys', []):
                    value = None
                    for tag in taggroup.get('tags', []):
                        if tag.get('key', None) == a_key:
                            value = tag.get('value', None)
                    taggroups.append(value)

            # Fill up the rest of the values with None
            length = max(config_taggroup.get('count'), 1) * len(
                config_taggroup.get('keys'))
            taggroups.extend([None] * (length - len(taggroups)))

            row.extend(taggroups)

        if involvements:
            inv_row = []
            for involvement in activity.get('involvements', []):
                inv_data = [None] * len(involvement_header)
                for i, config_sh_key in enumerate(
                        involvement_header[:len(involvement_header) - 2]):
                    inv_data[i] = get_value_by_key_from_item_json(
                        involvement.get('data', {}), config_sh_key)

                inv_data[len(inv_data) - 2] = involvement.get('role', None)
                inv_data[len(inv_data) - 1] = involvement.get('data', {}).get(
                    'id', None)
                inv_row.extend(inv_data)
            # Fill the rest with None
            inv_row.extend([None] * (
                len(involvement_header) * max_involvements - len(inv_row)))
            row.extend(inv_row)

        rows.append(row)

    return header, rows
