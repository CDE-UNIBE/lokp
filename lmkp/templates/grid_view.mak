<%inherit file="lmkp:templates/htmlbase.mak" />

<%def name="title()">Grid View</%def>

<%def name="head_tags()">
    ## TODO: This should be fixed in bootstrap
    <style type="text/css" >
        .desc.active {
            background: url("${request.static_url('lmkp:static/media/img/to-top-black.png')}") no-repeat scroll right top transparent;
        }
    </style>
</%def>

## Start of content

<%
    import urllib

    # Get the keys and their translation
    from lmkp.views.translation import get_activity_keys
    from lmkp.views.translation import get_stakeholder_keys
    activitykeys = get_activity_keys(request)
    stakeholderkeys = get_stakeholder_keys(request)

    # Decide which keys are relevant for the grid
    if activetab == 'sh':
        keys = stakeholderkeys
    else:
        keys = activitykeys
%>

<!-- Filter-area  -->
<form class="form-horizontal filter_area">
    <div class="container">
        <div class="control-group">
            <label class="control-label">Active filters</label>
            <div class="controls">
                <input type="text" id="filter1" class="filter-variable1" placeholder="A sample variable > 23">
                <span class="icon-remove1">
                    <i class="icon-remove pointer"></i>
                </span>
            </div>
        </div>
        <div class="control-group">
            <div class="controls">
                <input type="text" id="filter2" class="filter-variable2" placeholder="Another sample variable = Cambodia">
                <span class="icon-remove2">
                    <i class="icon-remove pointer"></i>
                </span>
            </div>
        </div>
        <div class="control-group new-filter new-filter">
            <label class="control-label">New Filter</label>
            <div class="controls">
                <div class="btn-group">
                    <button class="btn select_btn_filter">Taggroup</button>
                    <button class="btn select_btn_filter_right dropdown-toggle" data-toggle="dropdown">
                        <span class="caret"></span>
                    </button>
                    <ul class="dropdown-menu">
                        <li><a href="#">1</a></li>
                        <li><a href="#">2</a></li>
                        <li><a href="#">3</a></li>
                        <li><a href="#">4</a></li>
                        <li><a href="#">5</a></li>
                    </ul>
                </div>
                <div class="btn-group">
                    <button class="btn select_btn_operator">&#8804;</button>
                    <button class="btn select_btn_operator_right dropdown-toggle" data-toggle="dropdown">
                        <span class="caret"></span>
                    </button>
                    <ul class="dropdown-menu">
                        <li><a href="#">&#8805;</a></li>
                        <li><a href="#">=</a></li>
                        <li><a href="#">!=</a></li>
                    </ul>
                </div>
                <input type="text" class="filter-value" id="filter2" placeholder="Value">
                <span class="icon-add">
                    <i class="icon-plus pointer"></i>
                </span>
            </div>
        </div>
        <div class="favorite">
            <div class="btn-group favorite">
                <button class="btn btn_favorite">Favorite</button>
                <button class="btn btn_favorite_right dropdown-toggle" data-toggle="dropdown">
                    <span class="caret"></span>
                </button>
                <ul class="dropdown-menu">
                    <li><a href="#">1</a></li>
                    <li><a href="#">2</a></li>
                    <li><a href="#">3</a></li>
                    <li><a href="#">4</a></li>
                    <li><a href="#">5</a></li>
                </ul>
            </div>
        </div>
    </div>
</form>

<div class="filter_area_openclose">
    <i class="icon-double-angle-up pointer"></i>
</div>

<!-- content -->
<div class="container">
    <div class="content">

        <p>Active spatial filter: ${spatialfilter}</p>

        % if len(data) == 0:

            ## Empty data
            <p>Nothing found!</p>

        % else:

            ## Tabs
            <ul class="nav nav-tabs table_tabs">
                <%
                    # The entries of the tabs as arrays with
                    # - "tab id" (a / sh)
                    # - name
                    tabs = [
                        ['a', 'Deals'],
                        ['sh', 'Investors']
                    ]
                %>
                % for t in tabs:
                    % if activetab == t[0]:
                        <li class="active">
                    % else:
                        <li>
                    % endif
                        <a href="#" onclick="updateQueryParams({'tab': '${t[0]}'})">${t[1]}</a>
                    </li>
                % endfor
            </ul>

            ## Table
            <div class="table_wrapper">
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
                                        <div class="desc pointer
                                             % if 'order_by=%s' % urllib.quote_plus(k[0]) in request.path_qs and 'dir=%s' % urllib.quote_plus('desc') in request.path_qs:
                                                active
                                             % endif
                                             " onclick="updateQueryParams({'order_by': '${k[0]}', 'dir': 'desc'})">_</div>
                                        <div class="asc pointer
                                             % if 'order_by=%s' % urllib.quote_plus(k[0]) in request.path_qs and 'dir=%s' % urllib.quote_plus('asc') in request.path_qs:
                                                active
                                             % endif
                                             " onclick="updateQueryParams({'order_by': '${k[0]}', 'dir': 'asc'})">_</div>
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

                            <tr>
                                <td>
                                    % if activetab == 'sh':
                                        <a href="${request.route_url('stakeholders_read_one', output='html', uid=id)}">
                                    % else:
                                        <a href="${request.route_url('activities_read_one', output='html', uid=id)}">
                                    % endif
                                        ${id[:6]}
                                    </a>
                                </td>
                                % for v in values:
                                    <td>${v}</td>
                                % endfor
                            </tr>
                        % endfor

                    </tbody>
                </table>
            </div>

            ## Pagination
            <div class="pagination text-center">

                <%
                    import math
                    maxpage = int(math.ceil(float(total)/pagesize))
                    endleft = 1 if currentpage > paginationneighbours + 1 else None
                    endright = maxpage if (currentpage + paginationneighbours < maxpage) else None
                %>

                <ul>
                    <li
                        % if currentpage == 1:
                            class="disabled"
                        % endif
                        ><a href="#" onclick="updateQueryParams({'page': ${currentpage-1}})">&laquo;</a>
                    </li>
                    % if endleft:
                        <li>
                            <a href="#" onclick="updateQueryParams({'page': ${endleft}})">${endleft}</a>
                        </li>
                    % endif
                    % if currentpage > paginationneighbours + 2:
                        <li class="disabled">
                            <a>...</a>
                        </li>
                    % endif
                    % for i in range(min(currentpage-paginationneighbours+1, paginationneighbours), 0, -1):
                        <li>
                            <a href="#" onclick="updateQueryParams({'page': ${currentpage-i}})">
                                ${currentpage-i}
                            </a>
                        </li>
                    % endfor
                    <li class="active">
                        <a href="#" onclick="updateQueryParams({'page': ${currentpage}})">${currentpage}</a>
                    </li>
                    % for i in range(min(maxpage-currentpage, paginationneighbours)):
                        <li>
                            <a href="#" onclick="updateQueryParams({'page': ${currentpage+i+1}})">
                                ${currentpage+i+1}
                            </a>
                        </li>
                    % endfor
                    % if currentpage+paginationneighbours+1 < maxpage:
                        <li class="disabled">
                            <a>...</a>
                        </li>
                    % endif
                    % if endright:
                        <li>
                            <a href="#" onclick="updateQueryParams({'page': ${endright}})">${endright}</a>
                        </li>
                    % endif
                    <li
                        % if currentpage == maxpage:
                            class="disabled"
                        % endif
                        ><a href="#" onclick="updateQueryParams({'page': ${maxpage}})">&raquo;</a>
                    </li>
                </ul>
            </div>

        % endif

    </div>
</div>

## "Tooltip" when clicking a table row
<div class="show-investors-wrapper hidden">
    <div class="show-investors">
        % if activetab == 'sh':
            <p>Show deals of this investor</p>
        % else:
            <p>Show investors for this deal</p>
        % endif
    </div>
</div>

## End of content

<%def name="bottom_tags()">
    <script src="${request.static_url('lmkp:static/v2/grid.js')}" type="text/javascript"></script>
    <script src="${request.static_url('lmkp:static/v2/filters.js')}" type="text/javascript"></script>
</%def>