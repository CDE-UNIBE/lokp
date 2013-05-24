<div class="deformMappingFieldset">
    <ul class="readonly">
        % if field.description:
            <li class="section">
                <div>${field.description}</div>
            </li>
        % endif
        % for child in field:
            ${child.render_template(field.widget.readonly_item_template)}
        % endfor
    </ul>
</div>