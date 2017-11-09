<%
    # Leave out all fields which contain no values! Also find out the depth of
    # the current current mapping item:
    # 0: A single tag
    # 1: A Taggroup
    # 2: A Thematic Group
    # 3: A Category
    from lmkp.views.form import structHasOnlyNullValues
    hasOnlyNullValues, depth = structHasOnlyNullValues(cstruct)
%>

% if not hasOnlyNullValues:

    % if field.name == 'map':
        ## The map container was already rendered by the initial form item so
        ## it appears right on top.

    % elif depth == 3:
        ## Category
        ${field.serialize(cstruct, readonly=True)}

    % elif depth == 2:
        ## Thematic Group
        % if field.title == '':
            ${field.serialize(cstruct, readonly=True)}
        % else:
            <div class="row-fluid thmg-title">
                <div class="grid-area">
                    <h5>${field.title}</h5>
                </div>
                ${field.serialize(cstruct, readonly=True)}
            </div>
        % endif

    % elif depth == 1:
        ## Taggroup
        <div class="row-fluid">
            <div class="grid-area taggroup-details">
                ${field.serialize(cstruct, readonly=True)}
            </div>
        </div>

    % elif field.name not in ['tg_id', 'id', 'category', 'version', 'itemType', 'statusId', 'taggroup_count']:
        ## Single tag
        <div class="row-fluid">
            <div class="span5">
                <h5 class="dealview_item_titel text-accent-color">${field.title}</h5>
            </div>
            <div class="dealview_item_attribute">
                ${field.serialize(cstruct, readonly=True)}
            </div>
        </div>
    % endif

% endif
