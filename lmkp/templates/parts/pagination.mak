<%doc>
    This is the template to show a pagination bar to be used for a grid.

    The following page arguments are needed:
    {int} totalitems: The total number of items.
    {int} pagesize: The number of items displayed per page.
    {int} currentpage: The page which is currently shown.
    {int} neighboursize (default = 2): How many pages are shown left and right
        of the current page before using "..." instead of showing pages.
</%doc>

<%page args="
    totalitems,
    currentpage,
    pagesize,
    neighboursize=2
    " />

<div class="pagination text-center">

    <%
        import math
        from lmkp.views.views import getQueryString

        maxpage = int(math.ceil(float(totalitems)/pagesize))
        endleft = 1 if currentpage > neighboursize + 1 else None
        endright = maxpage if (currentpage + neighboursize < maxpage) else None
    %>

    <ul>
        % if currentpage == 1:
            <li class="disabled"><a>&laquo;</a></li>
        % else:
            <li>
                <a href="${getQueryString(request.url, add=[('page', currentpage-1)])}">&laquo;</a>
            </li>
        % endif
        % if endleft:
            <li>
                <a href="${getQueryString(request.url, add=[('page', endleft)])}">${endleft}</a>
            </li>
        % endif
        % if currentpage > neighboursize + 2:
            <li class="disabled">
                <a>...</a>
            </li>
        % endif
        % for i in range(min(currentpage-neighboursize+1, neighboursize), 0, -1):
            <li>
                <a href="${getQueryString(request.url, add=[('page', currentpage-i)])}">
                    ${currentpage-i}
                </a>
            </li>
        % endfor
        <li class="active">
            <a href="${getQueryString(request.url, add=[('page', currentpage)])}">${currentpage}</a>
        </li>
        % for i in range(min(maxpage-currentpage, neighboursize)):
            <li>
                <a href="${getQueryString(request.url, add=[('page', currentpage+i+1)])}">
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
            <li>
                <a href="${getQueryString(request.url, add=[('page', endright)])}">${endright}</a>
            </li>
        % endif
        % if currentpage == maxpage:
            <li class="disabled"><a>&raquo;</a></li>
        % else:
            <li>
                <a href="${getQueryString(request.url, add=[('page', currentpage+1)])}">&raquo;</a>
            </li>
        % endif

    </ul>
</div>