<input type="number"
       name="${field.name}"
       value="${cstruct}"
       id="${field.oid}"

       % if field.widget.size:
            size="${field.widget.size}"
        % endif

        % if field.widget.css_class:
            class="${field.widget.css_class}"
        % endif

        % if field.widget.style:
            style="${field.widget.style}"
        % endif
/>


<script type="text/javascript">
    deform.addCallback(
        '${field.oid}',
        function(oid) {
            $('#' + oid).spinner(${options});
        }
    );
</script>
