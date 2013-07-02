<form
    id="${field.formid}"
    action="${field.action}"
    method="${field.method}"
    enctype="multipart/form-data"
    accept-charset="utf-8"
    % if field.css_class:
        class=${field.css_class}
    % endif
    >

<fieldset class="deformFormFieldset">

    % if field.title:
        <legend>${field.title}</legend>
    % endif

    <input type="hidden"
           name="_charset_"
    />
    <input type="hidden"
           name="__formid__"
           value="${field.formid}"
    />
    <ul>

        % if field.error:
            <li class="errorLi">
                <h3 class="errorMsgLbl">
                    ${_("There was a problem with your submission")}
                </h3>
                <p class="errorMsg">
                    ${_("Errors have been highlighted below")}
                </p>
                % if field.errormsg:
                    <p class="errorMsg">${_(field.errormsg)}</p>
                % endif
            </li>
        % endif

        % if field.description:
            <li class="section first">${description}</li>
        % endif

        % for child in field.children:
            ${child.render_template(field.widget.item_template)}
        % endfor

        <li class="buttons">
            % for button in field.buttons:
                <button
                    % if button.disabled:
                        disabled=${button.disabled}
                    % endif
                    id="${field.formid + button.name}"
                    name="${button.name}"
                    type="${button.type}"
                    class="btnText submit ${button.css_class}"
                    value="${button.value}"
                >
                    <span>${button.title}</span>
                </button>
            % endfor
        </li>

    </ul>

</fieldset>

% if field.use_ajax:
    <script type="text/javascript">
        deform.addCallback(
            '${field.formid}',
            function(oid) {
                var target = '#' + oid;
                var options = {
                    target: target,
                    replaceTarget: true,
                    success: function() {
                        deform.processCallbacks();
                        deform.focusFirstInput(target);
                    }
               };
               var extra_options = ${field.ajax_options} || {};
               $('#' + oid).ajaxForm($.extend(options, extra_options));
            }
        );
    </script>
% endif

</form>