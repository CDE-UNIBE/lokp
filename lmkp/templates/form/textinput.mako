<input type="text" 
       name="${field.name}"
       value="${cstruct}"
        % if field.widget.size:
            size = ${field.widget.size}
        % endif
    
        % if field.widget.css_class:
            class = ${field.widget.css_class}
	% endif

        % if field.widget.style:
            style = ${field.widget.style}
        % endif

	id="${field.oid}"
/>

% if helptext:
    <span class="form_helptext">${helptext}</span>
% endif
           
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