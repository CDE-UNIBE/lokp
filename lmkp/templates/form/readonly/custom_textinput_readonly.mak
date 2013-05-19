<input type="text"
       name="${field.name}"
       value="${cstruct}"
        % if field.widget.size:
            size = ${field.widget.size}
        % endif

	id="${field.oid}"
        class="readonly"
        readonly="readonly"
/>

% if helptext:
    <span class="form_helptext">${helptext}</span>
% endif