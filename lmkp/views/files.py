from pyramid.response import Response
from pyramid.view import view_config
import hashlib
import logging
import os
import simplejson as json
import string
import uuid

from lmkp.config import upload_directory_path

log = logging.getLogger(__name__)

@view_config(route_name='file_upload', permission='edit')
def file_upload(request):
    """
    Handle the upload of a new file.
    Note that when uploading a file using a form in Ext, the content-type of the
    server response needs to be in 'text/html', otherwise Ext will throw an
    error when trying to decode the JSON string
    http://stackoverflow.com/a/10388091

    http://code.google.com/p/file-uploader/
    """

    TEMP_DIRECTORY_NAME = 'temp'
    MAX_FILE_SIZE = 5000000 # bytes

    ret = {'success': False}

    filename = None
    filetype = None
    file = None
    try:
        filename = request.POST['file'].filename
        file = request.POST['file'].file
        filetype = request.POST['file'].type
    except:
        ret['msg'] = 'Post values not found'

    if filename is not None and file is not None and filetype is not None:
        validFile = True

        # Check upload directory
        if validFile is True:
            upload_path = upload_directory_path(request)
            if upload_path is None or not os.path.exists(upload_path):
                validFile = False
                ret['msg'] = 'Upload directory not specified or not found.'
            else:
                # Create a temporary directory if it does not yet exist.
                if not os.path.exists('%s/%s' % (upload_path, TEMP_DIRECTORY_NAME)):
                    os.makedirs('%s/%s' % (upload_path, TEMP_DIRECTORY_NAME))

        # Check filetype
        if validFile is True:
            fileextension = get_valid_file_extension(filetype)
            if fileextension is None:
                validFile = False
                ret['msg'] = 'File type is not valid.'

        # Check filesize
        if validFile is True:
            size = get_file_size(file)
            if size > MAX_FILE_SIZE:
                validFile = False
                ret['msg'] = 'File is too big.'

        if validFile is True:
            # Do the actual file processing

            # Strip leading path from file name to avoid directory traversal
            # attacks
            old_filename = os.path.basename(filename)

            # Internet Explorer will attempt to provide full path for filename
            # fix
            old_filename = old_filename.split('\\')[-1]

            # Remove the extension and check the filename
            clean_filename = '.'.join(old_filename.split('.')[:-1])
            clean_filename = _clean_filename(clean_filename)

            # Append the predefined file extension
            clean_filename = '%s.%s' % (clean_filename, fileextension)

            # Use a randomly generated UUID as filename
            file_identifier = uuid.uuid4()
            new_filename = '%s.%s' % (file_identifier, fileextension)

            # If there is already a file with this name, add a number to the
            # filename
#            if os.path.exists('%s/%s/%s' % (upload_path, TEMP_DIRECTORY_NAME, temp_filename)):
#                temp_fn = temp_filename.split('.')
#                filecount = 1
#                while os.path.exists('%s/%s/%s'
#                    % (upload_path, TEMP_DIRECTORY_NAME,
#                        '%s_%s.%s' % (temp_fn[0], filecount, temp_fn[1]))):
#                    filecount += 1
#                temp_filename = '%s_%s.%s' % (temp_fn[0], filecount, temp_fn[1])

            # Use the temporary directory to upload the file to
            new_filepath = '%s/%s/%s' % (upload_path, TEMP_DIRECTORY_NAME, new_filename)

            # Open the new file for writing
            f = open(new_filepath, 'wb', 10000)

            datalength = 0

            # Read the file in chunks
            for chunk in _file_buffer(file):
                f.write(chunk)
                datalength += len(chunk)
            f.close()

            # Open the file again to get the hash
            hash = get_file_hash(new_filepath)

#            # Rename the file
#            new_filename = '%s.%s' % (hash, fileextension)
#            new_filepath = '%s/%s/%s' % (upload_path, TEMP_DIRECTORY_NAME, new_filename)
#            if os.path.exists(new_filepath):
#                # If a file with the new filename exists already, it must be the
#                # same file because the filename is based on the file hash.
#                # Still remove the existing file before renaming the file.
#                log.debug('Replaced an existing file with the same filename (and hash)')
#                os.remove(new_filepath)
#            os.rename(temp_filepath, new_filepath)

            log.debug('The uploaded file (%s) was saved as %s to temporary folder %s'
                % (clean_filename, new_filename, TEMP_DIRECTORY_NAME))

            # Database values
            # TODO: Do the database insert (table 'files')
            print clean_filename
            print file_identifier
            print filetype
            print datalength

            # Return values
            print clean_filename

            ret['filename'] = clean_filename
            
            ret['msg'] = 'File was successfully uploaded'
            ret['success'] = True

    # Send the response with content-type 'text/html'
    return Response(content_type='text/html', body=json.dumps(ret))

def get_file_hash(filepath, hexdigest=True):
    """
    Calculate the hash digest of a file.
    """
    f = open(filepath, 'r', 10000)
    h = hashlib.sha1()
    for chunk in _file_buffer(f):
        h.update(chunk)
    f.close()
    if hexdigest is True:
        return h.hexdigest()
    return h.digest()

def get_file_size(file):
    """
    Return the size of a file.
    """
    file.seek(0, 2) # Seek to the end of the file
    size = file.tell() # Get the position of EOF
    file.seek(0) # Reset the file position to the beginning
    return size

def _file_buffer(f, chunk_size=10000):
    """
    Helper function to process a file chunkwise
    """
    while True:
        chunk = f.read(chunk_size)
        if not chunk: break
        yield chunk

def _clean_filename(filename):
    """
    Return a clean filename by removing all invalid characters from the input.
    """
    # Then make sure the filename is valid by removing all invalid characters
    valid_chars = frozenset("-_.() %s%s"
        % (string.ascii_letters, string.digits))
    filename = ''.join(
        c for c in filename if c in valid_chars)
    if filename == '':
        # If all the characters were removed, use a default filename
        filename = 'defaultfilename'
    return filename

def get_valid_file_extension(mimetype):
    """
    Helper function to return a standard file extension for a given mimetype.
    Also used to check valid file types (return None if not supported)
    Many thanks to Internet Explorer for treating everything a little different
    once again.
    (http://msdn.microsoft.com/en-us/library/ms775147%28v=vs.85%29.aspx#_replace)
    """
    if mimetype == 'image/jpeg' or mimetype == 'image/pjpeg':
        # for .jpeg and .jpg return .jpg
        return 'jpg'
    elif mimetype == 'image/png' or mimetype == 'image/x-png':
        return 'png'
    elif mimetype == 'image/gif':
        return 'gif'
    else:
        return None