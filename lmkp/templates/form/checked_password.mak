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
        ${field.start_mapping()}
        <label for="${field.oid}">${_('Password')}</label>
        <input
            class="input-style"
            type="password"
            name="${field.name}"
            value="${cstruct}"
            id="${field.oid}" />
        <label for="${field.oid}-confirm">${_('Confirm Password')}</label>
        <input
            class="input-style"
            type="password"
            name="${field.name}-confirm"
            value="${confirm}"
            id="${field.oid}-confirm" />
        ${field.end_mapping()}
    </div>
</div>
