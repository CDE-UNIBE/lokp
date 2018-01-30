${field.start_sequence()}

<div class="row">
  <div class="col s3">
    <label for="${field.oid}">
      % if field.title:
        ${field.title}
      % elif field.name:
        ${field.name}
      % endif
    </label>
    % if field.required:
      <span class="required-form-field"></span>
    % elif desired:
      <span class="desired-form-field"></span>
    % endif
  </div>
  <div class="col s9">
    % for index, choice in enumerate(values):
      <div class="row-fluid">
          <input id="${field.oid}-${index}"
                     class="input-top"
                     type="checkbox"
                     name="checkbox"
                     value="${choice[0]}"
                     % if choice[0] in cstruct:
                      checked
                     % endif
                     />
              <label for="${field.oid}-${index}">${choice[1]}</label>
        <!--<ul class="select-list">
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
          <li class="select-list-label">
            <p>${choice[1]}</p>
          </li>
        </ul>-->
      </div>
    % endfor
  </div>
</div>

% if helptext:
  <span class="form_helptext form_checkbox">${helptext}</span>
% endif

${field.end_sequence()}
