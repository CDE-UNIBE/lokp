${field.start_sequence()}

% for index, choice in enumerate(values):
    <div class="row-fluid">
        <ul class="select-list">
            <li>
                <p>${choice[1]}</p>
            </li>
            <li class="select-only">
                <div class="checkbox-modified">
                    <input id="${field.oid}-${index}"
                           class="input-top"
                           type="checkbox"
                           name="checkbox"
                           value="${choice[0]}"
                           % if choice[0] in cstruct:
                            checked
                           % endif
                           />
                    <label for="${field.oid}-${index}"></label>
                </div>
            </li>
        </ul>
    </div>
% endfor

% if helptext:
    <span class="form_helptext form_checkbox">${helptext}</span>
% endif

${field.end_sequence()}
