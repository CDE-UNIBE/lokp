<%
    _ = request.translate
%>

<div class="row-fluid">
    <div class="span4">
        <label for="${field.oid}">
            % if field.title:
                ${field.title}
            % elif field.name:
                ${field.name}
            % endif
            % if field.required:
                <span class="required-form-field"></span>
            % elif desired:
                <span class="desired-form-field"></span>
            % endif
        </label>
    </div>
    <div class="span8">

        <input
            type="hidden"
            id="${field.oid}"
            class="fileinformations"
            name="${field.name}"
            value="${cstruct}" />

        <div class="fileList"><!-- Placeholder --></div>

        <!--<button
            id="add-file-${field.oid}"
            class="btn btn-small uploadButton"
            onclick="return uploadFile(this);"
            ></button>-->

        <a id="add-file-${field.oid}" class="modal-trigger waves-effect waves-light btn" href="#formModal" onclick="return uploadFile(event, this);" style="margin-bottom: 15px;">${_('Upload a file')}</a>

    </div>
</div>

<script type="text/javascript">

    // JS translation
    var tForLoading = "${_('Loading ...')}";
    var tForViewFile = "${_('View this file')}";
    var tForDeleteFile = "${_('Delete this file')}";
    var tForWarning = "${_('Warning')}";
    var tForSureToDelete = "${_('Are you sure you want to delete this file?')}";
    var tForYes = "${_('Yes')}";
    var tForNo = "${_('No')}";
    var tForNoFileYet = "${_('No file uploaded yet')}";

    /**
     * Add callback to hidden textfield to create the file list on start.
     */
    deform.addCallback(
        '${field.oid}',
        function(oid) {
            var textfield = $('#' + oid);
            updateExistingFiles(textfield);
            textfield.change(function() {
                updateExistingFiles($(this));
            });
        }
    );

    /**
     * Function to upload a new file.
     * Opens a modal window with the form to do the upload.
     */
    function uploadFile(event, btn) {
        event.preventDefault();

        // Set a loading indicator and show the modal window.
        $('#formModal .modal-content').html('<p>' + tForLoading + '</p>');
        $('#formModal').modal({
            backdrop: 'static'
        });

        // Remove old indicator and add a new one. This is used to know for
        // which field we are currently uploading a File.
        $('span#currentlyuploadingfile').remove();
        var tagContainer = $(btn).parent('div');
        tagContainer.append('<span id="currentlyuploadingfile"></span>');

        // Query and set the content of the modal window.
        $.ajax({
            url: '${request.route_url("file_upload_form_embedded")}'
        }).done(function(data) {
            $('#formModal .modal-content').html(data);
            deform.load();
            if (!$('#formModal').hasClass('open')) {
                // Open modal
                $('#formModal').openModal();
            }
        });

        // Do not submit anything.
        return false;
    }

    /**
     * Function to add a newly uploaded file to the list.
     * Adds the values to the internal file information and triggers an update
     * of the visible list with filenames.
     */
    function addUploadedFile(filename, identifier) {

        // Get the textfield with file informations based on the indicator set.
        var hiddenField = $('#currentlyuploadingfile')
            .parent('div')
            .find('input.fileinformations');

        // Add and set the new values.
        var oldValue = hiddenField.val();
        var newValue = filename + '|' + identifier;
        if (oldValue != '') {
            newValue = [oldValue, newValue].join(',');
        }
        hiddenField.val(newValue);

        // Call function to do an update of the list with filenames.
        updateExistingFiles(hiddenField);
    }

    /**
     * Function to update the list with visible filenames.
     * Loop through the internal file information to add a text input for each
     * file available.
     */
    function updateExistingFiles(hiddenField) {

        // The internal file information.
        var value = hiddenField.val();

        // Find the list of filenames and empty it.
        var filelistContainer = hiddenField.parent('div').find('div.fileList');
        filelistContainer.empty();

        $.each(value.split(','), function() {
            if (this == '') return false;
            // For each file, add a text input and some buttons. The identifier
            // of each file needs to be stored as well, use the CSS class for
            // this.
            var v = this.split('|');
            var div = [
                '<div class="fileNameField">',
                '<input class="' + v[1] + '" type="text" value="' + v[0] + '" />',
                '<a href="/files/view/' + v[1] + '" target="_blank" class="btn btn-mini" title="' + tForViewFile + '"><i class="icon-eye-open"></i></a>',
                '<button class="btn btn-mini" onclick="javascript:return deleteFileAsk(this);" title="' + tForDeleteFile + '"><i class="icon-trash"></i></button>',
                '</div>'
            ].join('');
            filelistContainer.append(div);
        });

        if (filelistContainer.is(':empty')) {
            // Add a message if no file was uploaded yet.
            filelistContainer.append('<p>' + tForNoFileYet + '</p>');
        } else {
            // Add a listener for each text input to update the internal file
            // information upon change.
            $('div.fileList>div>input').blur(function() {
                updateFileInformation(hiddenField, $(this));
            });
        }
    }

    /**
     * Function to show a confirm message before actually deleting the file.
     */
    function deleteFileAsk(btn) {
        var fileContainer = $(btn).parent('div');
        var identifier = fileContainer.find('input').attr('class');

        var alert = [
            '<div class="alert alert-error">',
            '<button type="button" class="close" data-dismiss="alert">&times;</button>',
            '<p><strong>' + tForWarning + '</strong>: ' + tForSureToDelete + '</p>',
            '<button type="button" class="confirmButtons btn btn-danger btn-small" onclick="javascript:return deleteFileDo(\'' + identifier + '\', this);">' + tForYes + '</button>',
            '<button type="button" class="confirmButtons btn btn-small" data-dismiss="alert">' + tForNo + '</button>',
            '</div>'
        ].join('');
        fileContainer.append(alert);

        return false;
    }

    /**
     * Function to update the internal file information upon deleting a file.
     * This function is called after a file was deleted. Update the internal
     * list by removing the entry from there.
     */
    function deleteFileDo(identifier, btn) {

        var tagContainer = $(btn).parent('div').parent('div').parent('div').parent('div');
        var hiddenField = tagContainer.find('input.fileinformations');
        var fileInfo = hiddenField.val();

        // Store the information in a new array.
        var newInfo = [];
        $.each(fileInfo.split(','), function() {
            // Copy the information to the new array if it doesn't match the
            // identifier to delete.
            if (this.split('|')[1] != identifier) {
                newInfo.push(this);
            }
        });

        // Set the new information and update the file list.
        hiddenField.val(newInfo.join(','));
        updateExistingFiles(hiddenField);

        return false;
    }

    /**
     * Function to update the internal file information upon changing filename.
     * This function is called after a filename was changed. Update the filename
     * in the internal file information list.
     */
    function updateFileInformation(hiddenField, changedFilelist) {

        // Collect the necessary values. The identifier of the changed file is
        // stored in the CSS class of the text input.
        var fileInfo = hiddenField.val();
        var identifier = changedFilelist.attr('class');
        // Filenames should not contain any "," or "|".
        var newFilename = changedFilelist.val()
            .replace(/,/g, '-')
            .replace(/\|/g, '-');

        // Store the information in a new array.
        var newInfo = [];
        $.each(fileInfo.split(','), function() {
            // For each internal value, update the filename if it corresponds to
            // the given identifier.
            var v = this.split('|');
            if (v[1] == identifier) {
                v[0] = newFilename;
            }

            // Store information in the new array.
            newInfo.push(v.join('|'));
        });

        // Set the new value.
        hiddenField.val(newInfo.join(','));

    }

</script>
