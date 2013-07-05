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

    % if field.error:
        <div class="row-fluid">
            <div class="span12">
                <div class="alert alert-error">
                    <h5>${request.translate("There was a problem with your submission")}</h5>
                    <p>${request.translate("Errors have been highlighted below")}</p>
                </div>
            </div>
        </div>
    % endif

    % for child in field.children:
        ${child.render_template(field.widget.item_template)}
    % endfor

    <ul>
        <li class="buttons unstyled">
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