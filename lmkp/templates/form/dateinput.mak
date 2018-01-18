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
        <input type="date"
               class="datepicker"
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
    /*deform.addCallback(
        '${field.oid}',
        function(oid) {
            $('#' + oid).datepicker(${options});
        }
    );*/
</script>
