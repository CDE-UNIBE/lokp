<%
    from lmkp.views.form import structHasOnlyNullValues
    hasOnlyNullValues, depth = structHasOnlyNullValues(cstruct)
%>

% if depth == 3:
    ## Category
    ${field.serialize(cstruct)}

% elif depth == 2:
    ## Thematic Group
    <div class="row-fluid">
        <div class="span9 grid-area">
            <div class="span4">
                <h5 class="green">${field.title}</h5>
            </div>
            ${field.serialize(cstruct)}
        </div>
    </div>

% elif depth == 1:
    ## Taggroup
    <div class="span8 taggroup">
        ${field.serialize(cstruct)}
    </div>

% elif depth == 0:
    ## Single Tag
    ${field.serialize(cstruct)}

% endif

% if field.error and field.typ.__class__.__name__ != 'Mapping' and len(field.error.messages()) > 0:
    <div class="alert alert-error">
        <%
            errstr = 'error-%s' % field.oid
        %>
        % for msg in field.error.messages():
            ## Special error message for map
            % if field.name == 'lon':
                ${request.translate('The location of the deal is required. Please select a point on the map before continuing.')}
            % else:
                <p
                    % if msg.index==0:
                        id="${errstr}"
                    % else:
                        id="${'%s-%s' % (errstr, msg.index)}"
                    % endif
                    class="${field.widget.error_class}"
                >
                ${request.translate(msg)}
                </p>
            % endif
        % endfor
    </div>
% endif
