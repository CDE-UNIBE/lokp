% if field.widget.multiple:
    <input type="hidden"
           name="__start__"
           value="${field.name}:sequence"
    />
% endif

<div class="row">
    <div class="col s12">
        <label for="${field.oid}">
            % if field.title:
                ${field.title}
            % elif field.name:
                ${field.name}
            % endif
            % if field.required:
                <span class="required-form-field"></span>
            % elif desired:
                <span class="desired-form-field"></span>
            % endif
        </label>
    </div>
    <div class="col s9">
        <select name="${field.name}"
            id="${field.oid}" class="span12">
            % for value,description in field.widget.values:
                <option value="${value}"
                    % if field.widget.css_class:
                        class="${field.widget.css_class}"
                    % endif
                    % if unicode(cstruct) == unicode(value):
                        selected="selected"
                    % endif
                >${description}</option>
            % endfor
        </select>
        % if helptext:
            <span class="form_helptext">${helptext}</span>
        % endif
    </div>
</div>

% if field.widget.multiple:
    <input type="hidden"
           name="__end__"
           value="${field.name}:sequence"
    />
% endif
