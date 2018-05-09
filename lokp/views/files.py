import logging
import shutil

import colander
import deform
import os
import uuid
from mako.template import Template
from pyramid.httpexceptions import HTTPNotFound, HTTPForbidden
from pyramid.i18n import TranslationStringFactory, get_localizer
from pyramid.path import AssetResolver
from pyramid.response import Response
from pyramid.security import effective_principals
from pyramid.threadlocal import get_current_request
from pyramid.view import view_config
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

from lokp.config.files import upload_directory_path, upload_max_file_size
from lokp.models import File, DBSession, Activity, A_Tag_Group, A_Tag, A_Key, \
    A_Value
from lokp.utils.files import get_valid_file_extension, get_file_size, \
    clean_filename, get_file_hash, get_folders_from_identifier
from lokp.utils.views import validate_uuid

lokpAssetResolver = AssetResolver('lokp')
log = logging.getLogger(__name__)
_ = TranslationStringFactory('lokp')

@view_config(
    route_name='file_upload_form_embedded', permission='edit',
    renderer='lokp:templates/form/fileupload_embedded.mak')
def file_upload_form_embedded(request):

    class MemoryTmpStore(dict):
        def preview_url(self, uid):
            return None
    tmpStore = MemoryTmpStore()

    class Schema(colander.Schema):
        file = colander.SchemaNode(
            deform.FileData(),
            widget=deform.widget.FileUploadWidget(tmpStore),
            name='file',
            title='File'
        )

    formid = 'fileupload'

    schema = Schema()
    deform.Form.set_default_renderer(file_upload_renderer)
    form = deform.Form(
        schema, buttons=('submit',), formid=formid, use_ajax=True)

    def succeed(uploadResponse):
        """
        Function called after file upload was handled.
        """

        if uploadResponse['success'] is True:
            # Success
            filename = uploadResponse['filename']
            identifier = uploadResponse['fileidentifier']
            message = uploadResponse['msg']

            return '<script type="text/javascript">handleSuccess("%s", "%s", "\
                %s");</script>' % (filename, identifier, message)

        else:
            # Failure
            message = uploadResponse['msg']

            return '<script type="text/javascript">handleFailure("\
                %s");</script>' % message

    reqts = form.get_widget_resources()

    return {
        'form': _get_rendered_form(request, form, success=succeed), ## saves uploaded form in upload folder
        'js_links': reqts['js'],
        'css_links': reqts['css']
    }


@view_config(
    route_name='file_upload_json_response', permission='edit', renderer='json')
def file_upload_json_response(request):
    """
    A file upload through direct POST of the form data. Returns a JSON response.

    Args:
        request:

    Returns:
        JSON
    """
    class MemoryTmpStore(dict):
        def preview_url(self, uid):
            return None

    tmpStore = MemoryTmpStore()

    class Schema(colander.Schema):
        file = colander.SchemaNode(
            deform.FileData(),
            widget=deform.widget.FileUploadWidget(tmpStore),
            name='file',
            title='File'
        )

    formid = 'fileupload'

    schema = Schema()
    deform.Form.set_default_renderer(file_upload_renderer)
    form = deform.Form(
        schema, buttons=('submit',), formid=formid)

    if 'submit' in request.POST:
        try:
            controls = request.POST.items()
            captured = form.validate(controls)
            return handle_upload(request, captured['file'])

        except deform.ValidationFailure as e:
            # the submitted values could not be validated
            return {
                'msg': e.render(),
                'success': False,
            }

    else:
        return {
            'msg': 'No file submitted',
            'success': False
        }

def _get_rendered_form(
        request, form, appstruct=colander.null, submitted='submit',
        success=None, readonly=False):
    """
    Based on method copied from
    http://deformdemo.repoze.org/allcode?start=70&end=114#line-70
    """
    captured = None

    if submitted in request.POST:
        # the request represents a form submission
        try:
            # try to validate the submitted values
            controls = request.POST.items()
            captured = form.validate(controls)

            uploadResponse = handle_upload(request, captured['file'])

            if success:
                response = success(uploadResponse)
                if response is not None:
                    return response
            html = form.render(captured)
        except deform.ValidationFailure as e:
            # the submitted values could not be validated
            html = e.render()

    else:
        # the request requires a simple form rendering
        html = form.render(appstruct, readonly=readonly)

    return html


def file_upload_renderer(tmpl_name, **kw):
    """
    A helper function to use the mako rendering engine.
    It seems to be necessary to locate the templates by using the asset
    resolver.
    """

    if tmpl_name == 'form':
        tmpl_name = 'form_fileupload_embedded'

    resolver = lokpAssetResolver.resolve('templates/form/%s.mak' % tmpl_name)
    template = Template(filename=resolver.abspath())

    # Add the request to the keywords so it is available in the templates.
    request = get_current_request()
    kw['request'] = request

    return template.render(**kw)

# TODO: pass boolean parameter for file upload
def handle_upload(request, filedict):
    """
    Handle the upload of a new file.
    http://code.google.com/p/file-uploader/
    """
    TEMP_FOLDER_NAME = 'temp'

    ret = {
        'success': False,
        'msg': ''
    }

    filename = None
    filetype = None
    file = None

    try:
        filename = filedict['filename']
        file = filedict['fp']
        filetype = filedict['mimetype']
    except:
        ret['msg'] = _('Not all necessary values were provided.')
        valid = False

    if filename is None or file is None or filetype is None:
        ret['msg'] = 'Uploaded file not found.'

    # Check upload directory
    upload_path = upload_directory_path(request)
    if upload_path is None or not os.path.exists(upload_path):
        ret['msg'] = _('Upload directory not specified or not found.')
        return ret

    # Check filetype
    fileextension = get_valid_file_extension(request, filetype)
    if fileextension is None:
        ret['msg'] = _('File type is not valid.')
        return ret

    # Check filesize
    size = get_file_size(file)
    if size > upload_max_file_size(request):
        ret['msg'] = _('File is too big.')
        return ret

    # Do the actual file processing

    # Strip leading path from file name to avoid directory traversal
    # attacks
    old_filename = os.path.basename(filename)

    # Internet Explorer will attempt to provide full path for filename
    # fix
    old_filename = old_filename.split('\\')[-1]

    # Remove the extension and check the filename
    cleaned_filename = '.'.join(old_filename.split('.')[:-1])
    cleaned_filename = clean_filename(cleaned_filename)

    # Make sure the filename is not too long
    if len(cleaned_filename) > 500:
        cleaned_filename = cleaned_filename[:500]

    # Append the predefined file extension
    cleaned_filename = '%s%s' % (cleaned_filename, fileextension)

    # Use a randomly generated UUID as filename
    file_identifier = str(uuid.uuid4())
    new_filename = '%s%s' % (file_identifier, fileextension)

    # Check if the directories already exist. If not, create them.
    if not os.path.exists(os.path.join(upload_path, TEMP_FOLDER_NAME)):
        os.makedirs(os.path.join(upload_path, TEMP_FOLDER_NAME))

    new_filepath = os.path.join(
        upload_path, TEMP_FOLDER_NAME, new_filename
    )

    temp_file_path = new_filepath + '~'
    file.seek(0)
    with open(temp_file_path, 'wb') as output_file:
        shutil.copyfileobj(file, output_file)
    os.rename(temp_file_path, new_filepath)

    # Open the file again to get the hash
    hash = get_file_hash(new_filepath)

    # Database values
    db_file = File(
        identifier=file_identifier, name=cleaned_filename, mime=filetype,
        size=size, hash=hash)
    DBSession.add(db_file)

    log.debug(
        'The uploaded file (%s) was saved as %s at %s'
        % (cleaned_filename, new_filename, new_filepath))

    ret['filename'] = cleaned_filename
    ret['fileidentifier'] = str(file_identifier)

    ret['msg'] = _('File was successfully uploaded')
    ret['success'] = True

    localizer = get_localizer(request)
    ret['msg'] = localizer.translate(ret['msg'])

    return ret


def check_file_location_name(request, filevaluestring):
    """
    Check if the files in a filevaluestring of the format
      cleanfilename|fileidentifier,cleanfilename|fileidentifier
    are still in the temporary upload directory (meaning that they were
    just recently uploaded). If so, move them to their proper directory
    (create it if necessary).
    (Also check if the file was renamed. In this case, update the
    database entry.) - see comments below
    """

    TEMP_FOLDER_NAME = 'temp'

    # A database query is needed to find out the mime-type (for the file
    # extension) and the name of the file.

    fileidentifiers = []
    filenames = []

    fileobjects = filevaluestring.split(',')
    for file in fileobjects:
        # Collect all fileidentifiers to query the database only once
        f = file.split('|')
        if len(f) != 2:
            # Something is wrong with the filevaluestring: skip it
            continue
        fileidentifiers.append(f[1])
        filenames.append(f[0])

    files_query = DBSession.query(File). \
        filter(File.identifier.in_(fileidentifiers)). \
        all()

    for i, fileidentifier in enumerate(fileidentifiers):
        # Loop all the file identifiers
        for f_db in files_query:
            # For each file identifier, try to find it in the database query
            if str(f_db.identifier) != fileidentifier:
                continue

            # Check if the file needs to be moved. This is the case if the file
            # is found in the temporary upload directory.

            extension = get_valid_file_extension(request, f_db.mime)
            if extension is None:
                # This should also never happen because files without valid
                # mime type should not have been uploaded in the first place
                continue

            # Put together the filename
            filename = '%s%s' % (fileidentifier, extension)

            # Try to find the file in the temporary directory
            upload_path = upload_directory_path(request)
            filepath = os.path.join(upload_path, TEMP_FOLDER_NAME, filename)

            if os.path.exists(filepath):
                # If the file is still in the temporary directory, move it
                folder1, folder2 = get_folders_from_identifier(fileidentifier)
                new_location = os.path.join(upload_path, folder1, folder2)

                # If the directory does not yet exist, create it
                if not os.path.exists(new_location):
                    os.makedirs(new_location)

                # Rename works to move the file
                os.rename(filepath, os.path.join(new_location, filename))

                log.debug(
                    'Moved file %s from temporary folder to new location at \
                    %s.'
                    % (f_db.name, new_location))

    # Return the file information, use only the valid ones
    rets = []
    for i, fileidentifier in enumerate(fileidentifiers):
        rets.append('%s|%s' % (filenames[i], fileidentifier))

    return ','.join(rets)


@view_config(route_name='file_view')
def file_view(request):
    """
    Show an uploaded file.
    .../{action}/{identifier}
    """

    TEMP_FOLDER_NAME = 'temp'

    try:
        action = request.matchdict['action']
        identifier = request.matchdict['identifier']
    except KeyError:
        raise HTTPNotFound()

    # Check if the action is valid
    if not (action == 'view' or action == 'download'):
        raise HTTPNotFound()

    # Check if the identifier is valid
    if validate_uuid(identifier) is False:
        raise HTTPNotFound()

    # Try to find necessary information of the file (mime-type)
    db_file_query = DBSession.query(File). \
        filter(File.identifier == identifier)

    try:
        db_file = db_file_query.one()
    except NoResultFound:
        raise HTTPNotFound()
    except MultipleResultsFound:
        # This should actually never happen since we are dealing with UUIDs
        raise HTTPNotFound()

    # Get file extension
    extension = get_valid_file_extension(request, db_file.mime)
    if extension is None:
        # This should also never happen because files without valid mime type
        # should not have been uploaded in the first place
        raise HTTPNotFound()

    # Put together the filename
    filename = '%s%s' % (identifier, extension)

    # Try to find the file on disk
    upload_path = upload_directory_path(request)
    folder1, folder2 = get_folders_from_identifier(str(identifier))
    filepath = os.path.join(upload_path, folder1, folder2, filename)

    # Check that the file is on the disk
    temporaryFile = False
    if not os.path.exists(filepath):
        # If the file was not found in its proper directory, try to find it in
        # the temporary upload directory. This means the Activity was not (yet)
        # submitted and the file is only visible for logged in users.
        filepath = os.path.join(upload_path, TEMP_FOLDER_NAME, filename)
        if not os.path.exists(filepath):
            # If it is still not found, raise error
            raise HTTPNotFound()

        # TODO: Authentication: Handle it properly
        if 'system.Authenticated' not in effective_principals(request):
            raise HTTPForbidden()

        temporaryFile = True

    # If the file is not in the temporary folder, find its Activity versions by
    # searching for its A_Value (filename|UID).
    if temporaryFile is False:
        a_value = '|%s' % db_file.identifier
        a_db_query = DBSession.query(Activity). \
            join(A_Tag_Group, A_Tag_Group.fk_activity == Activity.id). \
            join(A_Tag, A_Tag.fk_tag_group == A_Tag_Group.id). \
            join(A_Key, A_Tag.fk_key == A_Key.id). \
            join(A_Value, A_Tag.fk_value == A_Value.id). \
            filter(A_Key.type.ilike('File')). \
            filter(A_Value.value.contains(a_value))

        # Files for Activities are always visible if there is an active version
        # having the file attached.
        # Files for pending versions of Activities are only visible if the
        # current user is moderator or edited at least one pending version.
        showFile = False
        for a in a_db_query.all():
            if a.fk_status == 2:
                # Active: There is an active version with the file, show it
                showFile = True
                break
            if a.fk_status == 1 and request.user is not None:
                # Pending: Check if user is moderator or created the version.
                if 'group:moderators' in effective_principals(request):
                    # Moderator
                    showFile = True
                    break
                if a.changeset.user == request.user:
                    # Editor of a version
                    showFile = True
                    break

        if showFile is False:
            raise HTTPForbidden()

    # Open the file
    file = open(filepath, 'rb').read()

    response = Response(
        body=file,
        content_type=str(db_file.mime)
    )

    if action == 'download':
        response.content_disposition = 'attachment; filename=%s' % db_file.name

    return response
