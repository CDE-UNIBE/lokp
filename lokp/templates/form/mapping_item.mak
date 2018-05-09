${field.serialize(cstruct)}

% if field.error:
  <div class="alert alert-error">
    % for msg in field.error.messages():
      <span id="error-${field.oid}}" class="${field.widget.error_class}">
        ${request.translate(msg)}
      </span>
    % endfor
  </div>
% endif
