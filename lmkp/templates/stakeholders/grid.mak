<%inherit file="lmkp:templates/htmlbase.mak" />

<%def name="title()">Grid View - Investors</%def>

<%def name="head_tags()">
    ## TODO: This should be fixed in bootstrap
    <style type="text/css" >
        .desc.active {
            background: url("${request.static_url('lmkp:static/media/img/to-top-black.png')}") no-repeat scroll right top transparent;
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
    from lmkp.views.translation import get_activity_keys
    from lmkp.views.translation import get_stakeholder_keys
    activitykeys = get_activity_keys(request)
    stakeholderkeys = get_stakeholder_keys(request)

    # Decide which keys are relevant for the grid
    keys = stakeholderkeys
%>

## Filter
<%include file="lmkp:templates/parts/filter.mak"
    args="temporary='temporary'"
/>

<!-- content -->
<div class="container">

    <div class="show-investors visible-phone">
        <i class="icon-info-sign"></i>
        <p>Show deals by clicking on a specific row</p>
    </div>

    <div class="content">

        ## Tabs
        <ul class="nav nav-tabs table_tabs">
            <%
                # The entries of the tabs as arrays with
                # - url
                # - name
                tabs = [
                    [request.route_url('activities_read_many', output='html'), 'Deals'],
                    [request.route_url('stakeholders_read_many', output='html'), 'Investors']
                ]
            %>
            % for t in tabs:
                % if t[0] == request.current_route_url():
                    <li class="active">
                % else:
                    <li>
                % endif
                    <a href="${t[0]}">${t[1]}</a>
                </li>
            % endfor
        </ul>

        ## Table
        <div class="table_wrapper">

            % if len(data) == 0:

                ## Empty data
                <p>&nbsp;</p>
                <h5>Nothing found</h5>
                <p>No results were found.</p>
                <p>&nbsp;</p>

            % else:

                ## "Tooltip" when clicking a table row
                <div class="show-investors-wrapper hidden hidden-phone">
                    <div class="show-investors">
                        <a href="#">Show deals of this investor</a>
                    </div>
                </div>

                <table
                    class="table table-hover table-self table-bordered"
                    id="activitygrid">
                    <thead>
                        ## The table headers
                        <tr>
                            <th>ID
                                <div class="desc">_</div>
                                <div class="asc">_</div>
                            </th>

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

                            </tr>
                        % endfor

                    </tbody>
                </table>

            % endif
        </div>

        ## Pagination
        % if len(data) > 0:
            <%include file="lmkp:templates/parts/pagination.mak"
                args="totalitems=total, currentpage=currentpage, pagesize=pagesize"
            />
        % endif

    </div>
</div>

## End of content

<%def name="bottom_tags()">
    <script src="${request.static_url('lmkp:static/v2/grid.js')}" type="text/javascript"></script>
    <script src="${request.static_url('lmkp:static/v2/filters.js')}" type="text/javascript"></script>
</%def>