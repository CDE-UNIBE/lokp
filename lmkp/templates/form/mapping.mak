<fieldset class="deformMappingFieldset" 
          i18n:domain="deform">

    <!-- mapping -->

    % if field.title:
        <legend>${field.title}</legend>
    % endif

    <ul>
        % if field.errormsg:
            <li class="errorLi">
                <h3 class="errorMsgLbl"
                    i18n:translate=""
                >There was a problem with this section</h3>
                <p class="errorMsg">${field.errormsg}</p>
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