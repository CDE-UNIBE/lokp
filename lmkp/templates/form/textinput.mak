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
        <input 
            class="input-style"
            type="text"
            name="${field.name}"
            value="${cstruct}"
            id="${field.oid}"
            placeholder="" />
        % if helptext:
            <div class="input-description">${helptext}</div>
        % endif
    </div>
</div>

% if field.widget.mask:
    <script type="text/javascript">
        deform.addCallback(
            '${field.oid}',
	    function (oid) {
                $("#" + oid).mask("${field.widget.mask}",
                {placeholder:"${field.widget.mask_placeholder}"});
            }
        );
    </script>
% endif
