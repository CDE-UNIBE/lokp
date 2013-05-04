${field.start_sequence()}

% if helptext:
    <span class="form_helptext form_checkbox">${helptext}</span>
% endif

<ul class="deformSet">
    % for index, choice in enumerate(values):
        <li class="deformSet-item">
            <input
                % if field.widget.css_class:
                    class="${field.widget.css_class}"
                % endif
                % if choice[0] in cstruct:
                    checked
                % endif
                type="checkbox"
                name="checkbox"
                value="${choice[0]}"
                id="${field.oid}-${index}"
            />
            <label for="${field.oid}-${index}">${choice[1]}</label>
        </li>
    % endfor
</ul>

${field.end_sequence()}
