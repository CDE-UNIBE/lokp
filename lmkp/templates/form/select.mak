% if field.widget.multiple:
    <input type="hidden"
           name="__start__"
           value="${field.name}:sequence"
    />
% endif

<div class="row-fluid">
    <div class="span4">
        <p>
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
        </p>
    </div>
    <div class="span8">
        <select name="${field.name}"
            id="${field.oid}"

            % if field.widget.size:
                size="${field.widget.size}"
            % endif

            % if field.widget.css_class:
                class="${field.widget.css_class}"
            % endif

            % if field.widget.multiple:
                multiple="${field.widget.multiple}"
            % endif
        >
            % for value,description in field.widget.values:
                <option value="${value}"
                    % if field.widget.css_class:
                        class="${field.widget.css_class}"
                    % endif
                    % if cstruct == value:
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