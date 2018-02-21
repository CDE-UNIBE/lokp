<%doc>
    This is the template for the filter area.
</%doc>

<%
    from lokp.views.filter import getFilterKeys
    from lokp.views.filter import getActiveFilters

    aFilterKeys, shFilterKeys = getFilterKeys(request)
    activeFilters = getActiveFilters(request)
%>

## JS Translations
<script type="text/javascript">
    var tForValue = "${_('Value')}";
</script>

<ul class="collapsible" data-collapsible="accordion">
    <!-- Active Filters -->
    <li>
        <div class="collapsible-header" style="height: 50px; line-height: 50px;">
            <i class="material-icons">filter_list</i>
            ${_('Active Filters')}
            <span class="badge" style="background-color: teal; color: white;">${len(activeFilters)}</span>
        </div>
        <div class="collapsible-body">
            <ul class="collection">
                % for i, a in enumerate(activeFilters):
                    <li class="collection-item">
                        <div style="line-height: 50px; padding-left:80px;">
                            ${a[1]}
                            <input id="active-filter-${i+1}" type="hidden" value="${a[0]}"/>
                            <a onclick="javascript:deleteFilter(${i+1});" class="secondary-content" style="line-height: 50px; cursor: pointer;">
                                <i class="material-icons" style="line-height: 50px; color: teal;">delete</i>
                            </a>
                        </div>
                    </li>
                % endfor
            </ul>
        </div>
    </li>


    <!-- New Filter -->
    <li>
        <div class="collapsible-header"><i class="material-icons">playlist_add</i>${_('New Filter')}</div>
        <div class="collapsible-body">
            <div class="control-group new-filter" style="padding-left: 50px; padding-top: 30px;">
                <div class="controls">
                    ## Key
                    <a id="new-filter-key" class='dropdown-button btn' href='#' data-activates='dropdown_categories' style="width: 80%;">${_('Key')}<i class="material-icons right">arrow_drop_down</i></a>
                    <input id="new-filter-key-internal" type="hidden" value=""/>

                    <input id="new-filter-itemtype" type="hidden" value="a"/>

                    <ul class="dropdown-content" id="dropdown_categories">
                        <li class="disabled filterCategory">${_('Deals')}</li>
                        % for k in aFilterKeys:
                        <% escaped_k = k[0].replace("'", "\\'") %>
                            <li><a href="#" style="line-height: 50px; height: 50px;" onClick="javascript:selectKey('${escaped_k}', '${k[1]}', '${k[2]}', 'a')">${k[0]}</a></li>
                        % endfor
                        <li class="disabled filterCategory">${_('Investors')}</li>
                        % for k in shFilterKeys:
                        <% escaped_k = k[0].replace("'", "\\'") %>
                            <li><a href="#" style="line-height: 50px; height: 50px;" onClick="javascript:selectKey('${escaped_k}', '${k[1]}', '${k[2]}', 'sh')">${k[0]}</a></li>
                        % endfor
                    </ul>

                    ## Operator
                    <a id="new-filter-operator-display" class='dropdown-button btn' href='#' data-activates='new-filter-operator-dropdown' style="width: 80%;"></a>
                    <ul id="new-filter-operator-dropdown" class="dropdown-content">
                            <!-- Placeholder for the operators -->
                    </ul>
                    <input id="new-filter-operator" type="hidden" />

                    ## Value
                    <div id="new-filter-value-box" class="input-field" action="" style="height: 25px; line-height: 25px; margin: 18px; width: 80%;">
                        <!-- will be replaced -->
                        <input id="new-filter-value-internal"  placeholder="${_('Value')}" type="text" style="height: 20px; line-height: 20px;">
                    </div></br>
                    <a class="waves-effect waves-light btn" onClick="javascript:addNewFilter();" style="width: 80%;">Add<i class="material-icons right">add</i></a>
                </div>
            </div>
        </div>
    </li>

</ul>
