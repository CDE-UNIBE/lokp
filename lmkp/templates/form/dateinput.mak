<div class="row-fluid">
    <div class="span4">
        <p>${field.name}</p>
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