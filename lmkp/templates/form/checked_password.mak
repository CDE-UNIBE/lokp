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
        ${field.start_mapping()}
        <label for="${field.oid}">${request.translate('Password')}</label>
        <input
            class="input-style span12"
            type="password"
            name="${field.name}"
            value="${cstruct}"
            id="${field.oid}" />
        <label for="${field.oid}-confirm">${request.translate('Confirm Password')}</label>
        <input
            class="input-style span12"
            type="password"
            name="${field.name}-confirm"
            value="${confirm}"
            id="${field.oid}-confirm" />
        ${field.end_mapping()}
    </div>
</div>
