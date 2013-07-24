<form
    id="${field.formid}"
    action="${field.action}"
    method="${field.method}"
    enctype="multipart/form-data"
    accept-charset="utf-8">

    <input type="hidden"
           name="_charset_"
    />
    <input type="hidden"
           name="__formid__"
           value="${field.formid}"
    />

    % if field.error:
        <div class="alert alert-error">
            <h5>${request.translate("There was a problem with your submission")}</h5>
            ${request.translate("Errors have been highlighted below")}
        </div>
    % endif

    % for child in field.children:
        ${child.render_template(field.widget.item_template)}
    % endfor

    <div class="deal-editor-menu-bar stakeholder-editor-menu-bar-embedded">
    % for button in field.buttons:
        <ul>
            % if button.css_class == 'formstepactive':
                <div class="active-wrapper">
            % endif

            <li
                % if button.name == 'submit':
                    style="background-color:gray;"
                % endif
                >
                <button
                    id="${field.formid + button.name}"
                    name="${button.name}"
                    value="${button.value}"
                    class="btnText ${button.css_class}"
                    onclick="showLoadingIndicator(this);">
                    ${button.title}
                </button>
            </li>

            % if button.css_class == 'formstepactive':
                </div>
            % endif
        </ul>
    % endfor
    </div>

    % if field.use_ajax:
        <script type="text/javascript">
            deform.addCallback(
                '${field.formid}',
                function(oid) {
                    var target = '#' + oid;
                    var options = {
                        target: target,
                        replaceTarget: true,
                        url: '/files/form',
                        success: function() {
                            deform.processCallbacks();
                            deform.focusFirstInput(target);
                            return false;
                        }
                    };
                    var extra_options = ${field.ajax_options} || {};
                    $('#' + oid).ajaxForm($.extend(options, extra_options));
                }
            );
        </script>
    % endif

    <script type="text/javascript">
        function showLoadingIndicator(btn) {
            var form = $(btn).closest('form');
            form.hide();
            var loading = $('#fileUploadFormLoading');
            loading.show();
        }
    </script>

</form>