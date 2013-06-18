<h3>Deal Details</h3>

% if 'id' in cstruct:
    <p class="id">${cstruct['id']}</p>
% endif

% for child in field:
    ${child.render_template(field.widget.readonly_item_template)}
% endfor
