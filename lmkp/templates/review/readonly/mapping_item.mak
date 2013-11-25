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
            cls = 'accordion-heading category'
            clsBody = 'row-fluid accordion-body collapse'
            chevronClass = 'icon-chevron-down'
            if change:
                cls += ' change'
                clsBody += ' in'
                chevronClass = 'icon-chevron-up'
        %>
        
        <div class="row-fluid accordion accordion-group">
            <div class="${cls}">
                <div class="span6">
                    % if change:
                        <i class="icon-exclamation-sign"></i>
                    % endif
                    % if not hasOnlyNullValues:
                    <a class="accordion-toggle" data-toggle="collapse" href="#collapse-${field.name}">
                        ${field.title}
                        <i class="${chevronClass}"></i>
                    </a>
                    % else:
                    <span class="emptyCategory">
                        ${field.title}
                    </span>
                    % endif
                </div>
                <div class="span6">
                    % if not hasOnlyNullValues:
                    <a class="accordion-toggle" data-toggle="collapse" href="#collapse-${field.name}">
                        ${field.title}
                        <i class="${chevronClass}"></i>
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
        </div>

    % elif depth == 2 and not hasOnlyNullValues:
        ## Thematic Group
        
        <%
            change = 'change' in cstruct and cstruct['change'] != colander.null
            cls = 'span6 grid-area'
            if change:
                cls += ' change'
        %>
        
        <div class="row-fluid accordion-group">
            <div class="accordion-heading">
                <div class="${cls}">
                    <a class="accordion-toggle disableClick">
                        <h5 class="green">
                            ${field.title}
                        </h5>
                    </a>
                </div>
                <div class="${cls}">
                    <a class="accordion-toggle disableClick">
                        <h5 class="green">
                            ${field.title}
                        </h5>
                    </a>
                </div>
            </div>
            <div id="collapse-${field.name}" class="row-fluid accordion-body collapse in">
                <div class="accordion inner">
                    ${field.serialize(cstruct, readonly=True)}
                </div>
            </div>
        </div>

    % elif depth == 1 and not hasOnlyNullValues:
        ## Taggroup
    
        <%
            change = 'change' in cstruct and cstruct['change'] != colander.null
            cls = 'span6 taggroup-content deal-moderate-col'
            if change:
                cls += ' change'
        %>
    
        % if field.name.startswith('ref_'):
        <div class="row-fluid deal-moderate-col-wrap">
            % if not isinstance(cstruct, list):
                <div class="${cls}">
                    ${field.serialize(cstruct, readonly=True)}
                </div>
            % else:
                ${field.serialize(cstruct, readonly=True)}
            % endif
        % else:
            % if not isinstance(cstruct, list) and len(cstruct) > 1:
                <div class="${cls}">
                    ${field.serialize(cstruct, readonly=True)}
                </div>
            % else:
                ${field.serialize(cstruct, readonly=True)}
            % endif
        </div>
        % endif

    % elif field.name not in ['tg_id', 'id', 'category', 'version', 'itemType', 'change'] and not hasOnlyNullValues:
        ## Single tag
        <div class="row-fluid">
            <div class="span5">
                ${field.title}
            </div>
            <div class="span2 inactive"></div>
            <div class="span4">
                <p class="deal-detail">
                    ${field.serialize(cstruct, readonly=True)}
                </p>
            </div>
        </div>
    % endif