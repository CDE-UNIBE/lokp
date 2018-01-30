<div class="row">
    <div class="input-field col s12">
        % if helptext:
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
        <input
            class="input-style input-helptext col s9 "
            type="text"
            name="${field.name}"
            value="${cstruct}"
            id="${field.oid}"/>
        <span class="tooltipped" data-position="right" data-delay="50" data-tooltip="${helptext}">
            ${helptext}
        </span>

        % else:
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
        <input
            class="input-style col s9"
            type="text"
            name="${field.name}"
            value="${cstruct}"
            % if field.required:
               required=""
                aria-required="true"
            % endif
            id="${field.oid}"/>
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
