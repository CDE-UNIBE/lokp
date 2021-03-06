<%
    # Leave out all fields which contain no values! Also find out the depth of
    # the current current mapping item:
    # 0: A single tag
    # 1: A Taggroup
    # 2: A Thematic Group
    # 3: A Category
    from lokp.utils.form import structHasOnlyNullValues
    hasOnlyNullValues, depth = structHasOnlyNullValues(cstruct)

    repeating_taggroup = isinstance(cstruct, list)
%>

% if not hasOnlyNullValues:

    % if field.name == 'map':
        ## The map container was already rendered by the initial form item so
        ## it appears right on top.

    % elif depth >= 3:
        ## Category
        ${field.serialize(cstruct, readonly=True)}

    % elif depth == 2 and field.title not in ['Tg'] and not repeating_taggroup:
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

    % elif field.name not in ['tg_id', 'id', 'category', 'version', 'itemType', 'statusId', 'taggroup_count', 'geometry']:
        ## Single tag
        <div class="row-fluid">
            % if field.title != 'Tg':
              <div class="span5">
                  <h5 class="dealview_item_titel text-accent-color">${field.title}</h5>
              </div>
            % endif
            <div class="dealview_item_attribute">
                ${field.serialize(cstruct, readonly=True)}
            </div>
        </div>
    % endif

% endif
