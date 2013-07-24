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

        <div class="fileList">
            % if cstruct == '':
                <p>No file uploaded yet</p>
            % endif
        </div>

        <a
            id="add-file-${field.oid}"
            href=""
            class="btn btn-small btn-primary"
            onclick="return uploadFile(this);"
            >
            Add File
        </a>
    </div>
</div>

<script type="text/javascript">

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

    var tForLoading = "${_('Loading ...')}";

    /**
     * Function to upload a new file.
     * Opens a modal window with the form to do the upload.
     */
    function uploadFile(btn) {

        // Set a loading indicator and show the modal window.
        $('#formModal .modal-body').html('<p>' + tForLoading + '</p>');
        $('#formModal').modal();

        // Remove old indicator and add a new one. This is used to know for
        // which field we are currently uploading a File.
        $('span#currentlyuploadingfile').remove();
        var fieldset = $(btn).parent('div');
        fieldset.append('<span id="currentlyuploadingfile"></span>');

        // Query and set the content of the modal window.
        $.ajax({
            url: '${request.route_url("file_upload_form_embedded")}'
        }).done(function(data) {
            $('#formModal .modal-body').html(data);
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
        var textfield = $('#currentlyuploadingfile')
            .parent('div')
            .find('input.fileinformations');

        // Add and set the new values.
        var oldValue = textfield.val();
        var newValue = filename + '|' + identifier;
        if (oldValue != '') {
            newValue = [oldValue, newValue].join(',');
        }
        textfield.val(newValue);

        // Call function to do an update of the list with filenames.
        updateExistingFiles(textfield);
    }

    /**
     * Function to update the list with visible filenames.
     * Loop through the internal file information to add a text input for each
     * file available.
     */
    function updateExistingFiles(textfield) {

        // The internal file information.
        var value = textfield.val();
        if (!value || value == '') {
            return false;
        }

        // Find the list of filenames and empty it.
        var fileListContainer = textfield.parent('div').find('div.fileList');
        fileListContainer.empty();

        $.each(value.split(','), function() {
            // For each file, add a text input and some buttons. The identifier
            // of each file needs to be stored as well, use the CSS class for
            // this.
            var v = this.split('|');
            var div = [
                '<div>',
                '<input class="' + v[1] + '" type="text" value="' + v[0] + '" />',
                '<a href="#" class="btn btn-mini"><i class="icon-eye-open"></i></a>',
                '<a href="#" class="btn btn-mini"><i class="icon-trash"></i></a>',
                '</div>'
            ].join('');
            fileListContainer.append(div);
        });

        // Add a listener for each text input to update the internal file
        // information upon change.
        $('div.fileList>div>input').focusout(function() {
            updateFileInformation(textfield, $(this));
        });
    }

    /**
     * Function to update the internal file information upon changing filename.
     * This function is called after a filename was changed. Update the filename
     * in the internal file information list.
     */
    function updateFileInformation(textfield, changed) {

        // Collect the necessary values. The identifier of the changed file is
        // stored in the CSS class of the text input.
        var value = textfield.val();
        var identifier = changed.attr('class');
        var newValue = changed.val();

        // Store the information in a new array.
        var newInfo = [];
        $.each(value.split(','), function() {
            // For each internal value, update the filename if it corresponds to
            // the given identifier.
            var v = this.split('|');
            if (v[1] == identifier) {
                v[0] = newValue;
            }

            // Store information in the new array.
            newInfo.push(v.join('|'));
        });

        // Set the new value.
        textfield.val(newInfo.join(','));

    }

</script>
