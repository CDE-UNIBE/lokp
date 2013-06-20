<div class="row-fluid">
    <div class="span4">
        <p>${field.name}</p>
    </div>
    <div class="span6">
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

<%doc>
<script type="text/javascript">
    deform.addCallback(
        '${field.oid}',
        function(oid) {
            $('#' + oid).spinner(${options});
        }
    );
</script>
</%doc>
