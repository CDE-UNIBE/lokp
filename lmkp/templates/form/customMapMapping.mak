<fieldset class="deformMappingFieldset">

    <!-- mapping -->

    % if field.title:
        <legend>${field.title}</legend>
    % endif

    <span>
        This is where the map could end up. For the form, it may be necessary to
        submit the coordinates using hidden text inputs.
    </span>

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

    <span>
        This is the form/customMapMapping.mak template, add or include some map
        stuff (html and javascript) here.
    </span>

    <!-- /mapping -->

</fieldset>

<script type="text/javascript">
    // TODO
</script>