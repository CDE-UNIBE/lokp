<%doc>
    This is the template to show a pagination bar to be used for a grid.

    The following page arguments are needed:
    {int} totalitems: The total number of items.
    {int} pagesize: The number of items displayed per page.
    {int} currentpage: The page which is currently shown.
    {string} itemsname: The name of the items paginated (used for total number
        of items)
    {int} neighboursize (default = 2): How many pages are shown left and right
        of the current page before using "..." instead of showing pages.
</%doc>

<%page args="
    totalitems,
    currentpage,
    pagesize,
    itemsname,
    neighboursize=2
    " />

<%
    import math
    from lmkp.utils import handle_query_string

    maxpage = int(math.ceil(float(totalitems)/pagesize))
    endleft = 1 if currentpage > neighboursize + 1 else None
    endright = maxpage if (currentpage + neighboursize < maxpage) else None
%>

<div id="pagination" class="col s6 linearize-level-1">
  <ul class="pagination center">
    % if currentpage == 1:
        <li class="disabled"><a href="#!"><i class="material-icons">chevron_left</i></a></li>
    % else:
        <li class="waves-effect">
            <a href="${handle_query_string(request.url, add=[('page', currentpage-1)])}"><i class="material-icons">chevron_left</i></a>
        </li>
    % endif
    % if endleft:
        <li class="waves-effect">
            <a href="${handle_query_string(request.url, add=[('page', endleft)])}">${endleft}</a>
        </li>
    % endif
    % if currentpage > neighboursize + 2:
        <li class="disabled">
            <a>...</a>
        </li>
    % endif


    % for i in range(min(currentpage-neighboursize+1, neighboursize), 0, -1):
        <li class="waves-effect">
            <a href="${handle_query_string(request.url, add=[('page', currentpage-i)])}">
                ${currentpage-i}
            </a>
        </li>
    % endfor

    <li class="active accent-background-color">
        <a href="${handle_query_string(request.url, add=[('page', currentpage)])}">${currentpage}</a>
    </li>

    % for i in range(min(maxpage-currentpage, neighboursize)):
        <li class="waves-effect">
            <a href="${handle_query_string(request.url, add=[('page', currentpage+i+1)])}">
                ${currentpage+i+1}
            </a>
        </li>
    % endfor

    % if currentpage+neighboursize+1 < maxpage:
        <li class="disabled">
            <a>...</a>
        </li>
    % endif

    % if endright:
        <li class="waves-effect">
            <a href="${handle_query_string(request.url, add=[('page', endright)])}">${endright}</a>
        </li>
    % endif

    % if currentpage == maxpage:
        <li class="disabled"><a><i class="material-icons">chevron_right</i></a>
    % else:
        <li class="waves-effect">
            <a href="${handle_query_string(request.url, add=[('page', currentpage+1)])}"><i class="material-icons">chevron_right</i></a>
        </li>
    % endif
  </ul>
</div>

<div class="col s3">

    <div class="dropdown">
        ${itemsname} ${_('per page')}:
        <a id="btn-small" class='dropdown-button btn' data-toggle="dropdown" href='#' data-activates='dropdown1'>
             <i class="material-icons right">arrow_drop_down</i>${pagesize}
        </a>
        <ul id='dropdown1' class='dropdown-content'>
            <li><a href="${handle_query_string(request.url, add=[('pagesize', 10)])}">10</a></li>
            <li><a href="${handle_query_string(request.url, add=[('pagesize', 25)])}">25</a></li>
            <li><a href="${handle_query_string(request.url, add=[('pagesize', 50)])}">50</a></li>
          </ul>
    </div>

    ## Deals per Page
    <div>
        ${_('Total number of')} ${itemsname}: <strong>${totalitems}</strong>
    </div>
</div>
