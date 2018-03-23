from geoalchemy2 import functions as geofunctions
from pyramid.httpexceptions import HTTPNotFound
from pyramid.renderers import render_to_response
from pyramid.testing import DummyRequest
from pyramid.view import view_config
from sqlalchemy import cast, Float, func, distinct, select
from webob.multidict import MultiDict

from lokp.config.customization import get_customized_template_path
from lokp.models import Stakeholder, SH_Tag_Group, SH_Tag, SH_Key, SH_Value, \
    DBSession, Activity, A_Tag_Group, A_Tag, A_Key, A_Value, Language, \
    Profile, Involvement
from lokp.protocols.activity_protocol import ActivityProtocol
from lokp.protocols.stakeholder_protocol import StakeholderProtocol
from lokp.utils.views import validate_item_type, get_current_locale, \
    get_current_profile
from lokp.views.base import BaseView
from lokp.views.translation import get_profiles, get_translated_db_keys


class ChartsView(BaseView):

    @view_config(route_name='charts_overview')
    def charts_overview(self):

        return render_to_response(
            get_customized_template_path(self.request, 'charts_view.mak'),
            self.get_base_template_values(), self.request)

    @view_config(route_name='charts')
    @view_config(route_name='charts_no_slash')
    def charts(self):

        template_values = self.template_values

        chart_type = self.request.matchdict.get('type', 'bars')
        if chart_type == 'bars':
            params = self.request.matchdict.get('params')
            if params == ('sh',):
                template = 'barchart_sh'
            else:
                template = 'barchart_a'
        elif chart_type == 'stackedbars':
            template = 'stackedbarchart'
        elif chart_type == 'map':
            template = 'mapchart'
            profiles = sorted(get_profiles(), key=lambda profile: profile[0])
            profiles.append(('global', 'global'))
            template_values.update({
                'profiles': profiles
            })
        else:
            return HTTPNotFound()

        attr = self.request.params.get('attr', 0)

        template_values.update({
            'attr': attr
        })

        return render_to_response(
            get_customized_template_path(
                self.request, 'charts/%s.mak' % template),
            template_values, self.request)


class EvaluationView(BaseView):

    @view_config(route_name='evaluation', renderer='json')
    def evaluation(self, data=None):

        ret = {'success': False}

        json_data = self.request.json_body if data is None else data
        if json_data is None:
            ret['msg'] = 'No data provided'
            return ret

        if validate_item_type(json_data.get('item', 'a')) == 'sh':
            self.db_item = Stakeholder
            self.db_taggroup = SH_Tag_Group
            self.db_tag = SH_Tag
            self.db_key = SH_Key
            self.db_value = SH_Value
            self.protocol = StakeholderProtocol(DBSession)
        else:
            self.db_item = Activity
            self.db_taggroup = A_Tag_Group
            self.db_tag = A_Tag
            self.db_key = A_Key
            self.db_value = A_Value
            self.protocol = ActivityProtocol(DBSession)

        # Make sure the json is valid
        if 'group_by' not in json_data:
            ret['msg'] = "Missing parameter 'group by': At least one column "
            "needs to be specified."
            return ret
        if not isinstance(json_data['group_by'], list):
            ret['msg'] = "Parameter 'group by' needs to be an array."
            return ret
        if 'attributes' not in json_data:
            ret['msg'] = "Missing attributes: No attributes were specified."
            return ret
        for attr in json_data['attributes']:
            test, msg = self._check_function(
                json_data['attributes'][attr], attr)
            if test is not True:
                ret['msg'] = msg
                return ret
        if 'locales' in json_data and not isinstance(
                json_data['locales'], list):
            ret['msg'] = "Parameter 'locales' needs to be an array."
            return ret
        translate_keys = json_data.get('translate', {}).get('keys', [])
        if translate_keys and not isinstance(translate_keys, list):
            ret['msg'] = "Parameter 'translate[\'keys\']' needs to be an "
            "array."
            return ret
            # for k in translate_keys:
            #     if not isinstance(k, list):
            #         ret['msg'] = "Value of 'translate[\'keys\']' needs to be "
            #         "an array of arrays."
            #         return ret
        a_ids = json_data.get('a_ids', [])
        if not isinstance(a_ids, list):
            ret['msg'] = "Parameter 'a_ids' needs to be an array."
            return ret
            # for i in a_ids:
            #     if not isinstance(i, str):
            #         ret['msg'] = "Entries of parameter 'a_ids' need to be "
            #         "strings (the UUIDs of Activities)"
            #         return ret
        sh_ids = json_data.get('sh_ids', [])
        if not isinstance(sh_ids, list):
            ret['msg'] = "Parameter 'sh_ids' needs to be an array."
            return ret
            # for i in sh_ids:
            #     if not isinstance(i, str):
            #         ret['msg'] = "Entries of parameter 'sh_ids' need to be "
            #         "strings (the UUIDs of Stakeholders)"
            #         return ret
        if self.db_item == Activity:
            this_id_filter = a_ids
            other_id_filter = sh_ids
        else:
            this_id_filter = sh_ids
            other_id_filter = a_ids

        this_filter = []
        other_filter = []
        if 'filter' in json_data:
            params = []
            for filters in json_data.get('filter', '').split('&'):
                try:
                    f = filters.split('=')
                    if len(f) == 2:
                        params.append((f[0], f[1]))
                except:
                    pass
            # Simulate a request to send the filters
            req = DummyRequest()
            req.params = MultiDict(params)
            a_tag_filter, __, sh_tag_filter, __ = self.protocol._filter(req)
            if self.db_item == Activity:
                this_filter = a_tag_filter
                other_filter = sh_tag_filter
            else:
                this_filter = sh_tag_filter
                other_filter = a_tag_filter

        isInvolvementRequired = (
                self.db_item == Stakeholder
                or len(other_filter) + len(other_id_filter) > 0)

        # Collect all keys to be translated (values are translated in the
        # query)
        locales = ['default']
        langs = []
        locales.extend(json_data.get('locales', []))
        translated_keys = {}
        exclude_from_translation = ['Activity', 'Stakeholder']
        keys = []
        for key, __ in json_data.get('attributes', {}).items():
            if key not in exclude_from_translation and key not in keys:
                keys.append(key)
        for key in json_data.get('group_by', []):
            if key not in exclude_from_translation and key not in keys:
                keys.append(key)
        for key in translate_keys:
            for k in key:
                if k not in keys:
                    keys.append(k)
        for l in locales:
            locale = l
            if l == 'default':
                locale = get_current_locale(self.request)
            db_lang = DBSession.query(Language).filter(
                Language.locale == locale).first()
            langs.append((l, db_lang))
            translated_keys[l] = get_translated_db_keys(
                self.db_key, keys, db_lang)

        # Get groups
        groups_subqueries, groups_columns = self._get_group_by(
            json_data['group_by'], langs)

        # Get functions
        functions_subqueries, functions_columns = \
            self._get_attribute_functions(json_data['attributes'])

        # Prepare basic query
        q = DBSession.query(*groups_columns + functions_columns). \
            join(self.db_taggroup). \
            join(self.db_item)

        # Join with further groups
        for g_sq in groups_subqueries[1:]:
            q = q.outerjoin(g_sq, g_sq.c.item_id == self.db_item.id)

        # Join with functions
        for f_sq in functions_subqueries:
            q = q.outerjoin(f_sq, f_sq.c.item_id == self.db_item.id)

        # Apply status filter (fix: active)
        q = q.filter(self.db_item.fk_status == 2)

        if (this_id_filter):
            q = q.filter(self.db_item.identifier.in_(this_id_filter))

        # Apply filters
        filter_subqueries = self.protocol.Session.query(
            self.db_item.id.label('a_filter_id')
        )
        for x in this_filter:
            # Collect the IDs for each filter
            taggroups_sq = x.subquery()
            single_subquery = self.protocol.Session.query(
                self.db_item.id.label('a_filter_id')
            ). \
                join(self.db_taggroup). \
                join(taggroups_sq,
                     taggroups_sq.c.a_filter_tg_id == self.db_taggroup.id). \
                subquery()
            # Join each found ID with previously found IDs
            filter_subqueries = filter_subqueries. \
                join(single_subquery,
                     single_subquery.c.a_filter_id == self.db_item.id)
        filter_subqueries = filter_subqueries.subquery()
        q = q.join(
            filter_subqueries,
            filter_subqueries.c.a_filter_id == self.db_item.id)

        # Apply profile boundary filter
        if self.db_item == Activity:
            p = json_data.get('profile', get_current_profile(self.request))
            profile = DBSession.query(Profile). \
                filter(Profile.code == p). \
                first()
            if profile is not None:
                q = q.filter(geofunctions.ST_Intersects(
                    self.db_item.point, profile.geometry))

        # Apply grouping and ordering
        q = q.group_by(*groups_columns). \
            order_by(groups_columns[0])

        if isInvolvementRequired:
            if self.db_item == Stakeholder:
                inv_subquery = DBSession.query(
                    Involvement.fk_stakeholder.label('id')
                ). \
                    join(Activity). \
                    filter(Activity.fk_status == 2)
                p = json_data.get('profile', get_current_profile(self.request))
                profile = DBSession.query(Profile). \
                    filter(Profile.code == p). \
                    first()
                if profile is not None:
                    inv_subquery = inv_subquery.filter(geofunctions.ST_Intersects(
                        Activity.point, profile.geometry))
                other_db_item = Activity
                other_db_taggroup = A_Tag_Group
            else:
                inv_subquery = DBSession.query(
                    Involvement.fk_activity.label('id')
                ). \
                    join(Stakeholder). \
                    filter(Stakeholder.fk_status == 2)
                other_db_item = Stakeholder
                other_db_taggroup = SH_Tag_Group

            if (other_id_filter):
                inv_subquery = inv_subquery.filter(
                    other_db_item.identifier.in_(other_id_filter))

            # Apply filters
            filter_subqueries = self.protocol.Session.query(
                other_db_item.id.label('a_filter_id')
            )

            for x in other_filter:
                # Collect the IDs for each filter
                taggroups_sq = x.subquery()
                try:
                    single_subquery = self.protocol.Session.query(
                        other_db_item.id.label('a_filter_id')
                    ). \
                        join(other_db_taggroup). \
                        join(taggroups_sq,
                             taggroups_sq.c.a_filter_tg_id == other_db_taggroup.id). \
                        subquery()
                except AttributeError:
                    single_subquery = self.protocol.Session.query(
                        other_db_item.id.label('a_filter_id')
                    ). \
                        join(other_db_taggroup). \
                        join(taggroups_sq,
                             taggroups_sq.c.sh_filter_tg_id == other_db_taggroup.id). \
                        subquery()
                # Join each found ID with previously found IDs
                filter_subqueries = filter_subqueries. \
                    join(single_subquery,
                         single_subquery.c.a_filter_id == other_db_item.id)

            filter_subqueries = filter_subqueries.subquery()
            inv_subquery = inv_subquery.join(
                filter_subqueries,
                filter_subqueries.c.a_filter_id == other_db_item.id)

            inv_subquery = inv_subquery.subquery()
            q = q.filter(self.db_item.id.in_(
                select([inv_subquery.c.id])
            ))

        data = []
        for res in q.all():
            data = _handle_single_line(
                data, res, json_data.get('group_by'),
                json_data.get('attributes'), translated_keys)

        # Do a translation of groupable if available
        groupable_translated = []
        for key in translate_keys:
            translations = []
            for k in key:
                t = {
                    'key': k,
                    'default': k
                }
                for locale, key_translations in translated_keys.items():
                    translation = (
                        None if k not in exclude_from_translation else k)
                    for k_t in key_translations:
                        if len(k_t) >= 2 and k_t[0] == k:
                            translation = k_t[1]
                    t[locale] = translation
                translations.append(t)
            groupable_translated.append(translations)
        if len(groupable_translated):
            ret.update({
                'translate': {'keys': groupable_translated}
            })

        ret.update({
            'success': True,
            'data': data
        })

        return ret

    def _get_group_by(self, group_by, langs):
        """
        Returns
        - an array with SubQueries
        - an array with Columns to select from
        """
        subqueries = []
        columns = []
        for i, group_key in enumerate(group_by):
            # first one different
            if i == 0:
                subquery = DBSession.query(
                    self.db_value.value.label('v'),
                    self.db_tag.fk_tag_group.label('tg_id')
                ). \
                    join(
                    self.db_tag,
                    self.db_tag.fk_value == self.db_value.id). \
                    join(self.db_key, self.db_key.id == self.db_tag.fk_key). \
                    filter(self.db_key.key == group_key). \
                    filter(self.db_key.fk_language == None)
            else:
                subquery = DBSession.query(
                    self.db_item.id.label('item_id'),
                    self.db_value.value.label('v'),
                ). \
                    join(
                    self.db_taggroup,
                    self.db_taggroup.fk_item == self.db_item.id). \
                    join(
                    self.db_tag,
                    self.db_taggroup.id == self.db_tag.fk_tag_group). \
                    join(
                    self.db_value,
                    self.db_value.id == self.db_tag.fk_value). \
                    join(self.db_key, self.db_key.id == self.db_tag.fk_key). \
                    filter(self.db_key.key == group_key). \
                    filter(self.db_key.fk_language == None)
            for l in langs:
                __, value_translation = self.protocol._get_translatedKV(
                    l[1], self.db_key, self.db_value)
                subquery = subquery.add_columns(
                    value_translation.c.value_translated.label(l[0]))
                subquery = subquery. \
                    outerjoin(
                    value_translation,
                    value_translation.c.value_original_id ==
                    self.db_value.id)
            subquery = subquery.subquery()

            subqueries.append(subquery)

            columns.append(subquery.c.v)
            for l in langs:
                columns.append(subquery.c[l[0]])

        return subqueries, columns

    def _get_attribute_functions(self, attributes):
        """
        Returns
        - an array with SubQueries
        - an array with Columns to select from
        """
        subqueries = []
        columns = []
        for attr in attributes:
            function = attributes[attr]
            if function == 'sum':
                sq = DBSession.query(
                    self.db_item.id.label('item_id'),
                    cast(self.db_value.value, Float).label('v')
                ). \
                    join(self.db_taggroup). \
                    join(
                    self.db_tag,
                    self.db_taggroup.id == self.db_tag.fk_tag_group). \
                    join(
                    self.db_value,
                    self.db_value.id == self.db_tag.fk_value). \
                    join(self.db_key, self.db_key.id == self.db_tag.fk_key). \
                    filter(self.db_key.key == attr). \
                    subquery()
                subqueries.append(sq)
                columns.append(func.sum(sq.c.v))
            elif function == 'count' or function == 'count distinct':
                if attr == 'Activity' or attr == 'Stakeholder':
                    columns.append(func.count())
                else:
                    sq = DBSession.query(
                        self.db_item.id.label('item_id'),
                        self.db_value.value.label('v')
                    ). \
                        join(self.db_taggroup). \
                        join(
                        self.db_tag,
                        self.db_taggroup.id == self.db_tag.fk_tag_group). \
                        join(self.db_value). \
                        join(self.db_key). \
                        filter(self.db_key.key == attr). \
                        subquery()
                    subqueries.append(sq)
                    if (function == 'count distinct'):
                        columns.append(func.count(distinct(sq.c.v)))
                    else:
                        columns.append(func.count(sq.c.v))
        return subqueries, columns

    def _check_function(self, function, attr):
        """
        Returns True if a function is predefined and if targeted
        attribute is of valid type (where needed)
        """
        if function == 'sum':
            if self._cast_to_number(attr):
                return True, ''
            else:
                return False, "Invalid type for function '%s': '%s' should "
                "contain only number values." % (function, attr)
        if function == 'count':
            return True, ''
        if function == 'count distinct':
            return True, ''
        else:
            return False,
            "Unknown function: '%s' is not a predefined function." % function

    def _cast_to_number(self, key):
        """
        Returns True if the given key has number values
        """
        q = DBSession.query(cast(self.db_value.value, Float)). \
            join(self.db_tag). \
            join(self.db_key). \
            filter(self.db_key.key == key)
        try:
            q.all()
            return True
        except:
            return False


def _handle_single_line(
        data, res_total, group_by, attributes, translated_keys):

    group_by_res = res_total[:len(group_by) * (len(translated_keys) + 1)]
    attributes_res = res_total[len(group_by) * (len(translated_keys) + 1):]

    entry = None

    for e in data:
        if e.get('group', {}).get('value', {}).get('value') == group_by_res[0]:
            entry = e

    if entry is None:

        default = group_by[0]
        for k in translated_keys.get('default', []):
            if len(k) >= 2 and k[0] == group_by[0]:
                default = k[1]
        entry = {
            'group': {
                'key': {
                    'key': group_by[0],
                    'default': default
                },
                'value': {
                    'value': group_by_res[0],
                    'default': (
                        group_by_res[1] if group_by_res[1] is not None
                        else group_by_res[0])
                }
            }
        }

        i = 0
        for locale, key_translations in translated_keys.items():
            # Key
            if locale == 'default':
                continue
            t = None
            for k in key_translations:
                if len(k) >= 2 and k[0] == group_by[0]:
                    t = k[1]
            entry.get('group', {}).get('key', {})[locale] = t
            # Value
            entry.get('group', {}).get('value', {})[locale] = (
                group_by_res[i + 2])
            i += 1

        data.append(entry)

    rest_res = res_total[2:]
    rest_group_by = group_by[1:]
    if len(rest_res) > len(attributes_res) and len(rest_group_by):
        entry_data = entry.get('children', [])
        entry['children'] = _handle_single_line(
            entry_data, rest_res, rest_group_by, attributes, translated_keys)
    else:
        entry_attributes = []
        for i, attr in enumerate(attributes):
            key = {
                'key': attr,
                'default': attr
            }
            for locale, key_translations in translated_keys.items():
                t = None if attr not in ['Activity', 'Stakeholder'] else attr
                for k in key_translations:
                    if len(k) >= 2 and k[0] == attr:
                        t = k[1]
                key[locale] = t
            entry_attributes.append({
                'key': key,
                'value': attributes_res[i],
                'function': attributes[attr]
            })
        entry['values'] = entry_attributes

    return data
