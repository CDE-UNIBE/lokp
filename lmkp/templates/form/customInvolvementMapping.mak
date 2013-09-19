${field.start_mapping()}

% for child in field.children:
    ${child.render_template(field.widget.item_template)}
% endfor

${field.end_mapping()}

<%
    import colander
    import json
    newForm = 'id' in cstruct and cstruct['id'] == colander.null
    _ = request.translate
%>

<p>
    <a
        id="add-stakeholder-${field.oid}"
        href=""
        class="btn btn-small btn-primary add-stakeholder"
        onclick="return addStakeholder(this);"
        % if not newForm:
            style="display:none;"
        % endif
        >
        ${_('Select Stakeholder')}
    </a>

    <a
        id="remove-stakeholder-${field.oid}"
        href=""
        class="btn btn-small btn-warning remove-stakeholder"
        onclick="return removeStakeholder(this);"
        % if newForm:
            style="display:none;"
        % endif
        >
        ${_('Remove Stakeholder')}
    </a>
</p>

<script type="text/javascript">

    /**
     * Function to add (select or create) a new Stakeholder. Shows a modal
     * window where a Stakeholder can be selected or created.
     */
    function addStakeholder(btn) {

        // Set a loading indicator and show the modal window.
        $('#formModal .modal-body').html('<p>' + ${json.dumps(_('Loading ...'))} + '</p>');
        $('#formModal').modal();

        // Remove old indicator and add a new one. This is used to know which
        // Stakeholder we are currently editing.
        $('span#currentlyactiveinstakeholderform').remove();
        var fieldset = $(btn).parent('p').parent('div');
        fieldset.append('<span id="currentlyactiveinstakeholderform"></span>');

        // Query and set the content of the modal window.
        $.ajax({
            url: "${request.route_url('stakeholders_read_many', output='form')}?embedded=True"
        }).done(function(data) {
            $('#formModal .modal-body').html(data);
        });

        return false;
    }

    /**
     * Function to remove a selected Stakeholder.
     */
    function removeStakeholder(btn) {

        // Empty the values of all the readonly fields. Only reset those with an
        // id, others are used by Deform for mapping.
        var fieldset = $(btn).parent('p').parent('div');
        $.each(fieldset.find('input'), function() {
            if (this.id) {
                $(this).val(null);
            }
        });

        // Change the buttons back
        fieldset.find('a.remove-stakeholder').hide();
        fieldset.find('a.add-stakeholder').show();
        
        return false;
    }
</script>
