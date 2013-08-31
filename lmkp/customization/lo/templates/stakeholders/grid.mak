<%inherit file="lmkp:customization/lo/templates/base.mak" />

<%def name="title()">${_('Grid View')} - ${_('Investors')}</%def>

<%def name="head_tags()">
    ## TODO: This should be fixed in bootstrap
    <style type="text/css" >
        .desc.active {
            background: url("/custom/img/to-top-black.png") no-repeat scroll right top transparent;
        }
        tr.pending {
            background-color: #fcf8e3;
        }
        .show-investors a {
            text-decoration: none;
            color: white;
        }
    </style>
</%def>

## Start of content

<%
    import urllib
    from lmkp.views.views import getQueryString

    # Get the keys and their translation
    from lmkp.views.translation import get_stakeholder_keys
    keys = get_stakeholder_keys(request)

    a_uids = ','.join(invfilter) if invfilter is not None else ''
%>

## Filter
<%include file="lmkp:templates/parts/filter.mak" />

<!-- content -->
<div class="container">

    <div class="show-investors visible-phone">
        <i class="icon-info-sign"></i>
        <p>${_('Show deals by clicking on a specific row.')}</p>
    </div>

    <div class="content">

        ## Spatial Filter
        <%
            spatialFilterBasedOn = _('Profile')
            spatialFilterExplanation = _('You are seeing all the Investors involved in Deals within the current profile.')
            spatialFilterLink = None

            if spatialfilter == 'mapextentparam' or spatialfilter == 'mapextentcookie':
                spatialFilterBasedOn = _('Map Extent')
                spatialFilterExplanation = _('You are currently only seeing Investors involved in Deals which are visible on the map.')
                spatialFilterLink = _('Show all the Investors involved in Deals of the profile.')
        %>

        % if spatialfilter:
        <div class="alert alert-info">
            <i class="icon-globe"></i>&nbsp;
            <strong>${_('Spatial Filter')}</strong> ${_('based on')}
                % if spatialFilterLink:
                    <strong><a href="${request.route_url('map_view')}">${spatialFilterBasedOn}</a></strong>.
                % else:
                    <strong>${spatialFilterBasedOn}</strong>.
                % endif
            ${spatialFilterExplanation}
            % if spatialFilterLink:
                <br/><a href="${getQueryString(request.url, add=[('bbox', 'profile')])}">${spatialFilterLink}</a>
            % endif
        </div>
        % endif

        ## Involvement Filter
        % if invfilter:
        <div class="alert alert-info">
            <i class="icon-filter"></i>&nbsp;
            <strong>${_('Deal Filter')}</strong>: ${_('You are currently only seeing Investors which are involved in Deal')}
            % for uid in invfilter:
                <a href="${request.route_url('activities_read_one', output='html', uid=uid)}">
                    ${uid[:6]}</a>
            % endfor
            .<br/><a href="${request.route_url('stakeholders_byactivities_all', output='html')}">${_('Remove this filter and show all Investors')}</a>.
        </div>
        % endif

        ## Tabs
        <ul class="nav nav-tabs table_tabs">
            <%
                # The entries of the tabs as arrays with
                # - url
                # - name
                tabs = [
                    [
                        [
                            request.route_url('activities_read_many', output='html')
                        ], _('Deals')
                    ], [
                        [
                            request.route_url('stakeholders_byactivities_all', output='html'),
                            request.route_url('stakeholders_byactivities', output='html', uids=a_uids)
                        ], _('Investors')
                    ]
                ]
            %>
            % for t in tabs:
                % if request.current_route_url() in t[0]:
                    <li class="active">
                % else:
                    <li>
                % endif
                    <a href="${t[0][0]}${getQueryString(request.url, ret='queryString', remove=['order_by', 'dir'])}">${t[1]}</a>
                </li>
            % endfor
        </ul>

        ## Table
        <div class="table_wrapper">

            % if len(data) == 0:

                ## Empty data
                <p>&nbsp;</p>
                <h5>${_('Nothing found')}</h5>
                <p>${_('No results were found.')}</p>
                <p>&nbsp;</p>

            % else:

                ## "Tooltip" when clicking a table row
                <div class="show-investors-wrapper hidden hidden-phone">
                    <div class="show-investors">
                        <a href="#">${_('Show deals of this investor')}</a>
                    </div>
                </div>

                <table
                    class="table table-hover table-self table-bordered"
                    id="activitygrid">
                    <thead>
                        ## The table headers
                        <tr>
                            <th>${_('Investor ID')}</th>
                            % for k in keys:
                                ## Only use the headers which are to be shown
                                % if k[2] is True:
                                    <th>${k[1]}
                                        <a href="${getQueryString(request.url, add=[('order_by', k[0]), ('dir', 'desc')])}">
                                            <div class="desc
                                                 % if 'order_by=%s' % urllib.quote_plus(k[0]) in request.path_qs and 'dir=%s' % urllib.quote_plus('desc') in request.path_qs:
                                                    active
                                                 % endif
                                                 ">&nbsp;</div>
                                        </a>
                                        <a href="${getQueryString(request.url, add=[('order_by', k[0]), ('dir', 'asc')])}">
                                        <div class="asc
                                             % if 'order_by=%s' % urllib.quote_plus(k[0]) in request.path_qs and 'dir=%s' % urllib.quote_plus('asc') in request.path_qs:
                                                active
                                             % endif
                                             ">&nbsp;</div>
                                        </a>
                                    </th>
                                % endif
                            % endfor
                        </tr>
                    <tbody>
                        ## The table body

                        % for d in data:
                            <%
                                # Collect and prepare the necessary values to
                                # show in the grid.

                                pending = False
                                if 'status_id' in d and d['status_id'] == 1:
                                    pending = True

                                id = d['id'] if 'id' in d else 'Unknown id'
                                values = []
                                translatedkeys = []
                                for k in keys:
                                    if k[2] is True:
                                        translatedkeys.append(k[1])
                                        values.append('Unknown')
                                for tg in d['taggroups']:
                                    for t in tg['tags']:
                                        for i, tk in enumerate(translatedkeys):
                                            if t['key'] == tk:
                                                values[i] = t['value']
                            %>

                            % if pending:
                                <tr class="pending">
                            % else:
                                <tr>
                            % endif
                                <td>
                                    <a href="${request.route_url('stakeholders_read_one', output='html', uid=id)}">
                                        ${id[:6]}
                                    </a>
                                </td>
                                % for v in values:
                                    <td>${v}</td>
                                % endfor

                                <td class="identifier hide">${id}</td>
                                <td class="itemType hide">stakeholders</td>

                            </tr>
                        % endfor

                    </tbody>
                </table>

            % endif
        </div>

        ## Pagination
        % if len(data) > 0:
            <%include file="lmkp:templates/parts/pagination.mak"
                args="totalitems=total, currentpage=currentpage, pagesize=pagesize, itemsname=_('Investors')"
            />
        % endif

    </div>
</div>

## End of content

<%def name="bottom_tags()">
    <script src="${request.static_url('lmkp:static/v2/grid.js')}" type="text/javascript"></script>
    <script src="${request.static_url('lmkp:static/v2/filters.js')}" type="text/javascript"></script>
</%def>
