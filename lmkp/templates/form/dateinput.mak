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
        <input type="text"
               class="input-style"
               name="${field.name}"
               value="${cstruct}"
               id="${field.oid}"
        />

        % if helptext:
            <span class="form_helptext">${helptext}</span>
        % endif
    </div>
</div>

<script type="text/javascript">
    $('#${field.oid}').datepicker(${options});
</script>