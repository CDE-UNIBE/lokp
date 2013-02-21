import hashlib
import logging
import os
import simplejson as json
import string
import uuid

from lmkp.config import upload_directory_path
from lmkp.config import check_valid_uuid
from lmkp.models.database_objects import File
from lmkp.models.meta import DBSession as Session

from pyramid.httpexceptions import HTTPNotFound
from pyramid.response import Response
from pyramid.view import view_config

from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm.exc import MultipleResultsFound

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
        # Important: The identifier is submitted as '' even if not set
        identifier = (request.POST['identifier']
            if 'identifier' in request.POST else None)
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
                if not os.path.exists(os.path.join(upload_path, TEMP_DIRECTORY_NAME)):
                    os.makedirs(os.path.join(upload_path, TEMP_DIRECTORY_NAME))

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

            if identifier is not None and identifier != '':
                # Use the directory of the item to upload the file to
                if not os.path.exists(os.path.join(upload_path, identifier)):
                    # Create the directory if it does not yet exist
                    os.makedirs(os.path.join(upload_path, identifier))
                folder_name = identifier
            else:
                # No identifier provided, item does not yet exist. Use the
                # temporary directory to upload the file to
                folder_name = TEMP_DIRECTORY_NAME

#            # Make sure there is no file with the same clean_filename in the folder
#            if os.path.exists('%s/%s/%s' % (upload_path, folder_name, new_filename)):
#                temp_filename = new_filename.split('.')[:-1]
#                print "***"
#                print temp_filename
#                filecount = 1
#                while os.path.exists('%s/%s/%s'
#                    % (upload_path, folder_name,
#                        '%s_%s.%s' % (temp_filename[0], filecount, fileextension))):
#                    filecount += 1
#                # Create new filename
#                new_filename = '%s_%s.%s' % (temp_filename[0], filecount, fileextension)

            new_filepath = os.path.join(upload_path, folder_name, new_filename)

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

            # Database values
            db_file = File(
                identifier = file_identifier,
                name = clean_filename,
                mime = filetype,
                size = datalength,
                hash = hash
            )
            Session.add(db_file)

            log.debug('The uploaded file (%s) was saved as %s at %s'
                % (clean_filename, new_filename, new_filepath))

            ret['filename'] = clean_filename
            ret['fileidentifier'] = str(file_identifier)
            
            ret['msg'] = 'File was successfully uploaded'
            ret['success'] = True

    print ret

    # Send the response with content-type 'text/html'
    return Response(content_type='text/html', body=json.dumps(ret))

@view_config(route_name='file_show')
def file_show(request):
    """
    Show an uploaded file.
    .../{action}/{folder}/{identifier}
    """

    try:
        action = request.matchdict['action']
        folder = request.matchdict['folder']
        identifier = request.matchdict['identifier']
    except KeyError:
        raise HTTPNotFound()

    # Check if the identifier is valid
    if check_valid_uuid(identifier) is False:
        raise HTTPNotFound()

    # Try to find necessary information of the file (mime-type)
    db_file_query = Session.query(
            File
        ).\
        filter(File.identifier == identifier)

    try:
        db_file = db_file_query.one()
    except NoResultFound:
        raise HTTPNotFound()
    except MultipleResultsFound:
        # This should actually never happen since we are dealing with UUIDs
        raise HTTPNotFound()

    # Get file extension
    extension = get_valid_file_extension(db_file.mime)
    if extension is None:
        # This should also never happen because files without valid mime type
        # should not have been uploaded in the first place
        raise HTTPNotFound()

    # Put together the filename
    filename = '%s.%s' % (identifier, extension)

    # Try to find the file on disk
    upload_path = upload_directory_path(request)
    filepath = os.path.join(upload_path, folder, filename)

    # Check that the file is on the disk
    if not os.path.exists(filepath):
        raise HTTPNotFound()

    # Open the file
    file = open(filepath, 'rb').read()

    response = Response(
        body=file,
        content_type=str(db_file.mime)
    )

    if action == 'download':
        response.content_disposition='attachment; filename=%s' % db_file.name

    return response

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
