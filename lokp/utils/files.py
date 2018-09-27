import hashlib
import string

from lokp.config.files import valid_mime_extensions


def get_valid_file_extension(request, mimetype):
    """
    Helper function to return the predefined file extension for a mimetype.
    Also used to check valid file types (return None if not supported)
    """
    vme = valid_mime_extensions(request)
    try:
        return vme[mimetype]
    except KeyError:
        return None


def get_file_size(file):
    """
    Return the size of a file.
    """
    file.seek(0, 2)  # Seek to the end of the file
    size = file.tell()  # Get the position of EOF
    file.seek(0)  # Reset the file position to the beginning
    return size


def clean_filename(filename):
    """
    Return a clean filename by removing all invalid characters from the input.
    """
    # Then make sure the filename is valid by removing all invalid characters
    valid_chars = frozenset("-_.() %s%s" % (
        string.ascii_letters, string.digits))
    filename = ''.join(
        c for c in filename if c in valid_chars)
    if filename == '':
        # If all the characters were removed, use a default filename
        filename = 'defaultfilename'
    return filename


def file_buffer(f, chunk_size=10000):
    """
    Helper function to process a file chunkwise
    """
    while True:
        chunk = f.read(chunk_size)
        if not chunk:
            break
        yield chunk


def get_file_hash(filepath):
    """
    Calculate the hash digest of a file.
    """
    hasher = hashlib.md5()
    with open(filepath, 'rb') as afile:
        buf = afile.read()
        hasher.update(buf)
    return hasher.hexdigest()


def get_folders_from_identifier(identifier):
    """
    Return the folder structure based on an identifier.
    Folder 1: the first two digits of the identifier
    Folder 2: the third digit of the identifier
    """
    return identifier[:2], identifier[2:3]
