<div class="row-fluid">
    <div class="span4">
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
    <div class="span8">
        <textarea
            class="input-style"
            rows="4"
            id="${field.oid}"
            name="${field.name}"></textarea>
        % if helptext:
            <div class="input-description">${helptext}</div>
        % endif
    </div>
</div>
