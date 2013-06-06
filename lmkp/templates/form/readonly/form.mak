<div class="deform"
    % if field.name:
        id="${field.name}"
    % endif
>
    <div class="deformFormFieldset">
        % if field.title:
            <li class="section first">
                <h3>${field.title}</h3>
                % if field.description:
                    <div>${field.description}</div>
                % endif
            </li>
        % endif
    </div>

    % for child in field:
        ${child.render_template(field.widget.readonly_item_template)}
    % endfor
	
</div>