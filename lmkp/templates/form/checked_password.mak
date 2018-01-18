<div class="row">
    <div class="input-field col s12">
        ${field.start_mapping()}
        <label for="${field.oid}">${request.translate('Password')}
            % if field.required:
                <span class="required-form-field"></span>
            % elif desired:
                <span class="desired-form-field"></span>
            % endif
        </label>
        <input
            class="input-style span12"
            type="password"
            name="${field.name}"
            % if field.required:
               required=""
            % endif
            value="${cstruct}"
            id="${field.oid}" />
    </div>
</div>
<div class="row">
    <div class="input-field col s12">
        <label for="${field.oid}-confirm">${request.translate('Confirm Password')}
            % if field.required:
                <span class="required-form-field"></span>
            % elif desired:
                <span class="desired-form-field"></span>
            % endif
        </label>
        <input
            class="input-style span12"
            type="password"
            name="${field.name}-confirm"
            % if field.required:
                required=""
                aria-required="true"
            % endif
            value="${confirm}"
            id="${field.oid}-confirm" />
        ${field.end_mapping()}
    </div>
</div>


