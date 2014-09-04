from lmkp.models.meta import DBSession as Session
from lmkp.utils import validate_item_type
from lmkp.views.activities import _handle_spatial_parameters
from lmkp.views.activity_protocol3 import ActivityProtocol3
from lmkp.views.form_config import getCategoryList
from lmkp.views.protocol import (
    get_main_keys_from_item_json,
    get_value_by_key_from_item_json,
    get_value_by_key_from_taggroup_json,
)
from lmkp.views.stakeholder_protocol3 import StakeholderProtocol3


activity_protocol = ActivityProtocol3(Session)
stakeholder_protocol = StakeholderProtocol3(Session)


def to_flat_table(request, item_type, involvements=True):

    item_type = validate_item_type(item_type)
    if item_type == 'a':
        _handle_spatial_parameters(request)
        protocol = activity_protocol
        other_item_type = validate_item_type('sh')
    else:
        protocol = stakeholder_protocol
        other_item_type = validate_item_type('a')

    META_HEADER = ['id', 'version', 'timestamp']
    if item_type == 'a':
        META_HEADER.append('geometry')

    config_taggroups = []
    max_involvements = 0

    # Collect the taggroups based on the form configuration.
    config_taggroups = []
    for config_taggroup in getCategoryList(
            request, item_type).getAllTaggroups():
        config_taggroup_entry = {
            'count': 0,
            'config': config_taggroup,
            'main_key': config_taggroup.getMaintag().getKey().getName()
        }
        config_taggroups.append(config_taggroup_entry)

    # Query the Items with the protocol.
    # Important: Query the Items with the original database language! This
    # prevents errors when different main keys (eg. "Remark") have the exact
    # same translation. Instead, the translation happens when filling the row
    # with the help of the configs.
    items = protocol.read_many(request, public=True, translate=False)

    # Find out how many times each taggroup occurs. This defines how many
    # columns are needed in the table.
    for item in items.get('data', []):

        # Taggroups: Identified by their main tags.
        current_main_keys = []
        for main_key in get_main_keys_from_item_json(item):
            main_key_already_found = next(
                (i for i in current_main_keys if i['key'] == main_key), None)
            if main_key_already_found:
                main_key_already_found['count'] += 1
            else:
                current_main_keys.append({'key': main_key, 'count': 1})
        for main_key in current_main_keys:
            config_main_key = next((
                i for i in config_taggroups if i['main_key']
                == main_key['key']), None)
            if config_main_key is not None:
                config_main_key['count'] = max(
                    config_main_key['count'], main_key['count'])

        # Involvements
        if involvements:
            max_involvements = max(max_involvements, len(
                item.get('involvements', [])))

    # Create the headers
    header = []
    header.extend(META_HEADER)
    for config_taggroup_entry in config_taggroups:
        config_taggroup = config_taggroup_entry.get('config')
        config_mainkey = config_taggroup.getMaintag().getKey()
        for i in range(max(config_taggroup_entry.get('count'), 1)):
            for config_tag in sorted(
                    config_taggroup.getTags(),
                    key=lambda t: t != config_taggroup.getMaintag()):
                key_name = config_tag.getKey().getTranslatedName()
                # If the taggroup contains multiple tags, add the main key as
                # prefix
                if len(config_taggroup.getTags()) > 1:
                    key_name = '%s_%s' % (
                        config_mainkey.getTranslatedName(), key_name)
                # If the taggroup is repeated, add a number as suffix.
                if (config_taggroup.getRepeatable()
                        or config_mainkey.getType().lower() in
                        ['checkbox', 'inputtoken']):
                    key_name = '%s_%s' % (key_name, i + 1)

                header.append(unicode("%s" % key_name).encode('utf-8'))
    if involvements:
        inv_keys = [
            i[0] for i in getCategoryList(
                request, other_item_type).getInvolvementOverviewKeyNames()]

        involvement_header = inv_keys + ['inv_role', 'inv_id']
        for i in range(max_involvements):
            for inv_header in involvement_header:
                inv_key_name = '%s_%s' % (inv_header, i + 1)
                header.append(unicode("%s" % inv_key_name).encode('utf-8'))

    # Create the rows
    rows = []
    for item in items.get('data', []):
        row = []

        # Metadata
        for key in META_HEADER:
            if key == 'geometry':
                row.append(",".join(
                    map(str, item.get(key, {}).get("coordinates", []))))
            else:
                row.append(item.get(key, None))

        # Taggroups
        for config_taggroup_entry in config_taggroups:
            found_taggroups = []
            config_taggroup = config_taggroup_entry.get('config')
            config_mainkey = config_taggroup.getMaintag().getKey()

            for taggroup in item.get('taggroups', []):

                if taggroup['main_tag']['key'] != config_mainkey.getName():
                    continue

                for config_tag in sorted(
                        config_taggroup.getTags(),
                        key=lambda t: t != config_taggroup.getMaintag()):

                    value = get_value_by_key_from_taggroup_json(
                        taggroup, config_tag.getKey().getName())

                    for config_value in config_tag.getValues():
                        if config_value.getName() == value:
                            value = config_value.getTranslation()

                    if (config_tag.getKey().getType().lower() == 'file'
                            and value):
                        # Uploaded files are displayed with a URL to view the
                        # file
                        files = []
                        try:
                            for v in value.split(','):
                                filename = unicode(
                                    '%s' % v.split('|')[0]).encode('utf-8')
                                url = request.route_url(
                                    'file_view', action='view',
                                    identifier=v.split('|')[1])
                                files.append('%s (%s)' % (filename, url))
                            value = '|'.join(files)
                        except:
                            pass

                    if not value:
                        value = ''

                    found_taggroups.append(
                        unicode("%s" % value).encode("utf-8"))

            # Fill up the rest of the values with None
            taggroup_length = max(config_taggroup_entry.get('count'), 1) * len(
                config_taggroup.getTags())
            found_taggroups.extend(
                [None] * (taggroup_length - len(found_taggroups)))

            row.extend(found_taggroups)

        # Involvements
        if involvements:
            inv_row = []
            for involvement in sorted(item.get('involvements', []),
                                      key=lambda i: i.get('role_id', 0)):
                inv_data = [None] * len(involvement_header)

                # Overview keys
                for i, config_sh_key in enumerate(
                        involvement_header[:len(involvement_header) - 2]):
                    inv_value = get_value_by_key_from_item_json(
                        involvement.get('data', {}), config_sh_key)
                    inv_data[i] = unicode("%s" % inv_value).encode("utf-8")

                # Metadata
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
