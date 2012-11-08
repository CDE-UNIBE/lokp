from pyramid.view import view_config
from lmkp.config import codes_directory_path
from lmkp.models.database_objects import A_Key
from lmkp.models.database_objects import A_Value
from lmkp.models.database_objects import Language
from lmkp.models.database_objects import SH_Key
from lmkp.models.database_objects import SH_Value
from lmkp.models.meta import DBSession as Session
import csv
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm.exc import MultipleResultsFound
import os

@view_config(route_name='codes_files', renderer='json', permission='administer')
def codes_files(request):

    ret = {'success': False}

    files = []

    # Empty file to allow deselecting a file
    files.append({
        'description': '',
        'delimiter': '',
        'item': '',
        'success': True,
        'filename': '-',
        'language': ''
    })

    dirList=os.listdir(codes_directory_path())
    for filename in dirList:
        try:
            stream = open("%s/%s" % (codes_directory_path(), filename), 'rb')
        except IOError:
            ret['msg'] = 'Unable to open file %s' % filename
            return ret

        csvReader = csv.reader(stream, delimiter=";")

        line = None

        try:
            line = csvReader.next()
        except StopIteration:
            # This happens if file is empty
            pass

        if line is None:
            item = {
                'description': 'Empty file',
                'success': False,
                'filename': filename + ' (seems to be empty)'
            }
        elif len(line) >= 3:
            item = {
                'description': line[0],
                'delimiter': line[1],
                'item': line[2],
                'success': True,
                'filename': filename,
                'language': line[3]
            }
        else:
            item = {
                'description': 'Unable to parse file information.',
                'success': False,
                'filename': filename
            }
        files.append(item)

    ret['success'] = True
    ret['files'] = files

    return ret

@view_config(route_name='codes_add', renderer='json', permission='administer')
def codes_add(request):
    ret = {'success': False}

    filename = request.params.get('filename', None)
    delimiter = request.params.get('delimiter', None)
    locale = request.params.get('locale', None)

    if filename is None or delimiter is None or locale is None:
        ret['msg'] = 'Not all needed values provided.'
        return ret

    if len(delimiter) != 1:
        ret['msg'] = 'Delimiter must be a 1-character string'
        return ret

    item_type = request.params.get('item_type', None)
    if item_type == 'A_Value':
        TableItem = A_Value
        isKey = False
    elif item_type == 'A_Key':
        TableItem = A_Key
        isKey = True
    elif item_type == 'SH_Value':
        TableItem = SH_Value
        isKey = False
    elif item_type == 'SH_Key':
        TableItem = SH_Key
        isKey = True
    else:
        ret['msg'] = 'Database item not found.'
        return ret

    if locale == 'en':
        ret['msg'] = 'The language "English" cannot be selected!'
        return ret

    language = Session.query(Language).\
        filter(Language.locale == locale).\
        first()

    try:
        stream = open("%s/%s" % (codes_directory_path(), filename), 'rb')
    except IOError:
        ret['msg'] = 'File (%s) not found' % filename
        return ret

    errorCount = 0
    insertCount = 0
    msgStack = []

    csvReader = csv.reader(stream, delimiter=str(delimiter))
    for row in csvReader:
        # Skip the first item
        if csvReader.line_num > 1:
            try:
                inserted = _insert_code(row[1], row[0], TableItem, isKey,
                language)
            except:
                ret['msg'] = 'Wrong delimiter or wrong value type?'
                return ret
            msgStack.append(inserted)
            if inserted['success'] is True:
                insertCount += 1
            elif inserted['success'] is None:
                pass
            else:
                errorCount += 1

    if errorCount == 0:
        ret['success'] = True

    ret['insertCount'] = insertCount
    ret['errorCount'] = errorCount
    ret['messages'] = msgStack

    return ret

def _insert_code(value, code, TableItem, isKey, code_language):

    # Query the database to find english entry of key or value
    if isKey:
        eng_q = Session.query(TableItem).\
            filter(TableItem.key == value).\
            filter(TableItem.fk_key == None).\
            filter(TableItem.fk_language == 1)
    else:
        eng_q = Session.query(TableItem).\
            filter(TableItem.value == value).\
            filter(TableItem.fk_value == None).\
            filter(TableItem.fk_language == 1)

    eng = eng_q.all()

    if eng is None:
        return {'success': False, 'msg': 'No english value found for "%s", code "%s" not inserted.' % (value, code)}

    for e in eng:
        # Check if code already exists for value
        if isKey:
            code_value_q = Session.query(TableItem).\
                filter(TableItem.key == code).\
                filter(TableItem.original == eng).\
                filter(TableItem.language == code_language)
        else:
            code_value_q = Session.query(TableItem).\
                filter(TableItem.value == code).\
                filter(TableItem.original == e).\
                filter(TableItem.language == code_language)
        code_value = code_value_q.first()
        if code_value is None:
            # Insert it
            new_code = TableItem(code)
            new_code.language = code_language
            new_code.original = e
            Session.add(new_code)

    return {'success': True, 'msg': 'Code "%s" inserted for value "%s".' % (code, value)}

