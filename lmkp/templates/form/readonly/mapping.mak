% for child in field:
    ${child.render_template(field.widget.readonly_item_template)}
% endfor
