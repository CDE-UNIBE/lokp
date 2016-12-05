<%
    # Leave out all fields which contain no values! Also find out the depth of
    # the current current mapping item:
    # 0: A single tag
    # 1: A Taggroup
    # 2: A Thematic Group
    # 3: A Category
    from lmkp.views.form import structHasOnlyNullValues
    hasOnlyNullValues, depth = structHasOnlyNullValues(cstruct)
    import colander
%>

    % if field.name == 'map':
        ## The map container was already rendered by the initial form item so it
        ## appears right on top.
    
    % elif depth == 3:
        ## Category
        
        <%
            change = 'change' in cstruct and cstruct['change'] != colander.null
            cls = 'collapsible-header category row'
            clsBody = 'row collapsible-body collapse'
            chevronClass = 'expand_more'
            if change:
                cls += ' change'
                clsBody += ' in'
                chevronClass = 'expand_less'
        %>
        
        <ul class="row accordion comparedetailcontainer collapsible" data-collapsible="accordion">
            <li>
            <div class="${cls}">
                <div class="col s6">
                    <div class="customheaderleft">
                    % if change:
                        <i class="icon-exclamation-sign ttip pointer" data-toggle="tooltip" data-original-title="${_('There are changes in this section')}"></i>
                    % endif
                    % if not hasOnlyNullValues:
                    <a class="accordion-toggle text-accent-color" data-toggle="collapse" href="#collapse-${field.name}">
                        ${field.title}
                        <i class="material-icons text-accent-color right">${chevronClass}</i>
                    </a>
                    % else:
                    <span class="emptyCategory">
                        ${field.title}
                    </span>
                    % endif
                    </div>
                </div>
                <div class=" col s6 customheaderright">
                    % if not hasOnlyNullValues:
                    <a class="accordion-toggle text-accent-color" data-toggle="collapse" href="#collapse-${field.name}">
                        ${field.title}
                        <i class="material-icons text-accent-color right">${chevronClass}</i>
                    </a>
                    % else:
                    <span class="emptyCategory">
                        ${field.title}
                    </span>
                    % endif
                </div>
            </div>

            <div id="collapse-${field.name}" class="${clsBody}">
                <div class="accordion inner">
                    ${field.serialize(cstruct, readonly=True)}
                </div>
            </div>
            </li>
        </ul>

    % elif depth == 2 and not hasOnlyNullValues:
        ## Thematic Group
        
        <%
            change = 'change' in cstruct and cstruct['change'] != colander.null
            cls = 'span6 grid-area'
            if change:
                cls += ' change'
        %>
        
        <div class="row accordion-group">
            <div class="row">
                <div class="col s6 trennstrich">
                    <div class="${cls}"></div>
                </div>
                <div class="col s6 trennstrich">
                    <div class="${cls}"></div>
                </div>
            </div>
            <div id="collapse-${field.name}" class="row accordion-body collapse in">
                <div class="accordion inner">
                    ${field.serialize(cstruct, readonly=True)}
                </div>
            </div>
        </div>

    % elif depth == 1 and not hasOnlyNullValues:
        ## Taggroup
    
        <%
            change = 'change' in cstruct and cstruct['change'] != colander.null
            if isinstance(cstruct, list):
                cls = 'col s6 row taggroup-content'
            else:
                cls = 'col s6 row taggroup-content'
            if change:
                cls += ' change'
        %>
    
        % if field.name.startswith('ref_'):
        <div class="row deal-moderate-col-wrap">
            <div class="${cls}">
                ${field.serialize(cstruct, readonly=True)}
            </div>
        % else:
            <div class="${cls}">
                ${field.serialize(cstruct, readonly=True)}
            </div>
        </div>
        % endif

    % elif field.name not in ['tg_id', 'id', 'category', 'version', 'itemType', 'change'] and not hasOnlyNullValues:
        ## Single tag
        <div class="row compareitem">
            <div class="col s5 versioncomparetitle text-accent-color">
                ${field.title}
            </div>
            <div class="span2 inactive"></div>
            <div class="col s4">
                <p class="deal-detail">
                    ${field.serialize(cstruct, readonly=True)}
                </p>
            </div>
        </div>
    % endif