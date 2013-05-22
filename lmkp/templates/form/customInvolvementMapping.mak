<fieldset class="deformMappingFieldset">

    <!-- mapping -->

    % if field.title:
        <legend>${field.title}</legend>
    % endif

    <ul>
        % if field.errormsg:
            <li class="errorLi">
                <h3 class="errorMsgLbl">
                    ${_("There was a problem with this section")}
                </h3>
                <p class="errorMsg">
                    ${_(field.errormsg)}
                </p>
            </li>
        % endif

        % if field.description:
            <li class="section">
                <div>${field.description}</div>
            </li>
        % endif

        ${field.start_mapping()}

        % for child in field.children:
            ${child.render_template(field.widget.item_template)}
        % endfor

        ${field.end_mapping()}
    </ul>

    <%
        import colander
        newForm = 'id' in cstruct and cstruct['id'] == colander.null
    %>

    <button id="add-investor-${field.oid}"
            class="add-investor"
            % if not newForm:
                style="display:none;"
            % endif
    >
        <span>Add Investor</span>
    </button>

    <button id="edit-investor-${field.oid}"
            class="edit-investor"
            % if newForm:
                style="display:none;"
            % endif
    >
        <span>Edit Investor</span>
    </button>
    <button id="remove-investor-${field.oid}"
            class="remove-investor"
            % if newForm:
                style="display:none;"
            % endif
    >
        <span>Remove Investor</span>
    </button>

    <!-- /mapping -->

</fieldset>

<script type="text/javascript">
    $('button.add-investor').click(function() {
        var stakeholderform = $('div#stakeholderformcontainer');
        stakeholderform.show();
        stakeholderform.html('Loading ...');

        var fieldset = $(this).parent('fieldset');

        $('span#currentlyactiveinstakeholderform').remove();
        fieldset.append('<span id="currentlyactiveinstakeholderform"></span>');

        $.ajax({
            url: '/stakeholders/form'
        }).done(function(data) {
            stakeholderform.html(data);
        });

        return false;
    });

    $('button.edit-investor').click(function() {
        return false;
    });

    $('button.remove-investor').click(function() {
        return false;
    });
</script>
