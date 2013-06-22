${field.start_mapping()}

% for child in field.children:
    ${child.render_template(field.widget.item_template)}
% endfor

${field.end_mapping()}

<%
    import colander
    newForm = 'id' in cstruct and cstruct['id'] == colander.null
%>

<button
    id="add-stakeholder-${field.oid}"
    class="add-stakeholder"
    onclick="return addStakeholder(this);"
    % if not newForm:
        style="display:none;"
    % endif
>
    <span>Add Investor</span>
</button>

<button
    id="remove-stakeholder-${field.oid}"
    class="remove-stakeholder"
    onclick="return removeStakeholder(this);"
    % if newForm:
        style="display:none;"
    % endif
>
    <span>Remove Investor</span>
</button>

<script type="text/javascript">
    function addStakeholder(btn) {
        var stakeholderform = $('div#stakeholderformcontainer');
        stakeholderform.show();
        stakeholderform.html('Loading ...');
        $('span#currentlyactiveinstakeholderform').remove();
        var fieldset = $(btn).parent('fieldset');
        fieldset.append('<span id="currentlyactiveinstakeholderform"></span>');
        $.ajax({
            url: '/stakeholders/form'
        }).done(function(data) {
            stakeholderform.html(data);
        });
        return false;
    }
    function removeStakeholder(btn) {
        var fieldset = $(btn).parent('fieldset');
        $.each(fieldset.find('input'), function() {
            // Only reset those with an id (others are used for mapping)
            if (this.id) {
                $(this).val(null);
            }
        });
        fieldset.find('button.remove-stakeholder').hide();
        fieldset.find('button.add-stakeholder').show();
        return false;
    }
</script>
