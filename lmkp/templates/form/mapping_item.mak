<%
    from lmkp.views.form import structHasOnlyNullValues
    hasOnlyNullValues, depth = structHasOnlyNullValues(cstruct)
    _ = request.translate
%>

% if depth == 3:
    ## Category
    ${field.serialize(cstruct)}

% elif depth == 2:
    ## Thematic Group
        <div class="grid-area row-fluid editviewcontainer">
            <div class="span4">
                <h5 class="dealview_titel_investor text-accent-color">${field.title}</h5>
            </div>
            <div class="span8">
                ${field.serialize(cstruct)}
            </div>
        </div>

% elif depth == 1:
    ## Taggroup
    <div class="row-fluid taggroup">
        ${field.serialize(cstruct)}
    </div>

% elif depth == 0:
    ## Single Tag
    ${field.serialize(cstruct)}

% endif

% if field.error and field.typ.__class__.__name__ != 'Mapping' and len(field.error.messages()) > 0:
    <div class="alert alert-error">
        % for msg in field.error.messages():
            ## Special error message for map
            % if field.name == 'lon':
                ${_('The location is required. Please select a point on the map before continuing.')}
            % else:
                <span
                        id="error-${field.oid}}"
                    class="${field.widget.error_class}"
                >
                    ${request.translate(msg)}
                </span>
            % endif
        % endfor
    </div>
% endif
