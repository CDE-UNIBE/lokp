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

    <!-- /mapping -->

</fieldset>