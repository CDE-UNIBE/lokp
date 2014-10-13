% if field.errormsg:
    <div class="alert alert-error">
        <h5>${request.translate("There was a problem with this section")}</h5>
        <p>${request.translate(field.errormsg)}</p>
    </div>
% endif

${field.start_mapping()}

% for i, child in enumerate(field.children):
    ${child.render_template(field.widget.item_template)}
% endfor

${field.end_mapping()}
