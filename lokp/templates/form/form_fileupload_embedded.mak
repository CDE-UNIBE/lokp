<%
    _ = request.translate
    from lokp.config.files import getFileUploadValidExtensions, getFileUploadMaximumSize
    fileExtensions = getFileUploadValidExtensions(request)
    maxSize = getFileUploadMaximumSize(request)
%>

<form
    id="${field.formid}"
    action="${field.action}"
    method="${field.method}"
    enctype="multipart/form-data"
    accept-charset="utf-8">

    <input type="hidden"
           name="_charset_"/>
    <input type="hidden"
           name="__formid__"
           value="${field.formid}"/>

    % if field.error:
    <div class="alert alert-error">
        <h5>${request.translate("There was a problem with your submission")}</h5>
        ${request.translate("Errors have been highlighted below")}
    </div>
    % endif
    <div id="fileUploadFormDescription">

        <h3 class="fileUploadTitle">${_('File upload')}</h3>

        <p><em>${_('Important: All the uploaded files will be publicly visible! You should not upload confidential data.')}</em></p>

        <p><em>${_('Please note that the file upload may take a while depending on your Internet connection.')}</em></p>

        <p><strong>${_('Valid files')}</strong>: ${', '.join(fileExtensions)}</p>

        <p><strong>${_('Maximum file size')}</strong>: ${maxSize}</p>

    </div>

    % for child in field.children:
        ${child.render_template(field.widget.item_template)}
    % endfor

    ## Assumption: There is only 1 button which is the submit button
    <div class="deal-editor-menu-bar file-upload-button pull-right">
    % for button in field.buttons:
        <ul>
            % if button.css_class == 'formstepactive':
                <div class="active-wrapper">
            % endif

            <li
                % if button.name == 'submit':
                    style="background-color:teal;"
                % endif
                >
                <button
                    id="${field.formid + button.name}"
                    name="${button.name}"
                    value="${button.value}"
                    class="btnText ${button.css_class} btn-flat"
                    onclick="showLoadingIndicator(this);">
                    ${_('Upload')}
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

        // JS translation
        var tForSuccess = "${_('Success')}";
        var tForError = "${_('Error')}";

        // Hide the loading indicator if it is still there (form re-rendered
        // with errors)
        $('#fileUploadFormLoading').hide();

        /**
         * Function to show that the form is (up)loading.
         * Hides the form and shows a message to the user.
         */
        function showLoadingIndicator(btn) {
            var form = $(btn).closest('form');
            form.hide();
            var loading = $('#fileUploadFormLoading');
            loading.show();
        }

        /**
         * Function called if the file upload was successful.
         * Passes the new file to the list and shows a success message.
         */
        function handleSuccess(filename, identifier, message) {

            // Call function to add the new file to the list.
            addUploadedFile(filename, identifier);

            // Empty the form and add a success message
            var form = $('#fileUploadForm');
            form.empty();
            var successMessage = [
                '<h3 class="text-success fileUploadTitle">' + tForSuccess + '</h3>',
                '<p>' + message + '</p>'
            ].join('');
            form.append(successMessage);
        }

        /**
         * Function called if the file upload failed.
         * Shows an error message.
         */
        function handleFailure(message) {
            // Empty the form and show the error message.
            var form = $('#fileUploadForm');
            form.empty();
            var errorMessage = [
                '<h3 class="text-error fileUploadTitle">' + tForError + '</h3>',
                '<p>' + message + '</p>'
            ].join('');
            form.append(errorMessage);
        }
    </script>

</form>

% if not field.error:
<div id="fileUploadFormLoading" class="hide">
    ${_('The file is being uploaded. Please do not close this window!')}
</div>
% endif
