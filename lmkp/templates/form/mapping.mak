<%
    from lmkp.views.form import structHasOnlyNullValues
    hasOnlyNullValues, depth = structHasOnlyNullValues(cstruct)
%>

% if field.errormsg:
    <div class="alert alert-error">
        <h5>${request.translate("There was a problem with this section")}</h5>
        <p>${request.translate(field.errormsg)}</p>
    </div>
% endif

${field.start_mapping()}

% for i, child in enumerate(field.children):
    % if depth == 2 and i > 0:
        </div>
        <div class="row-fluid">
            <div class="span9">
                <div class="span4"></div>
                ${child.render_template(field.widget.item_template)}
            </div>
    % else:
        ${child.render_template(field.widget.item_template)}
    % endif
% endfor

${field.end_mapping()}
