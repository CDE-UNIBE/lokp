${field.start_sequence()}

% for index, choice in enumerate(values):
    % if index == 0:
        <div class="row-fluid">
            <div class="span4">
                <p>
                    % if field.title:
                        ${field.title}
                    % elif field.name:
                        ${field.name}
                    % endif
                </p>
                % if field.required:
                    <span class="required-form-field"></span>
                % elif desired:
                    <span class="desired-form-field"></span>
                % endif
            </div>
            <div class="span8" style="margin-left: 0;">
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
        </div>

    % else:
        <div class="row-fluid">
            <div class="span4"></div>
            <div clsas="span8">
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
        </div>

    % endif
% endfor

% if helptext:
    <span class="form_helptext form_checkbox">${helptext}</span>
% endif

${field.end_sequence()}
