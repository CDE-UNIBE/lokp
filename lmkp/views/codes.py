from pyramid.view import view_config
from lmkp.config import codes_directory_path
from lmkp.models.database_objects import A_Value
from lmkp.models.database_objects import Language
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

    dirList=os.listdir(codes_directory_path())
    for filename in dirList:
        try:
            stream = open("%s/%s" % (codes_directory_path(), filename), 'rb')
        except IOError:
            ret['msg'] = 'Unable to open file %s' % filename
            return ret

        csvReader = csv.reader(stream, delimiter=";")
        line = csvReader.next()
        if len(line) >= 3:
            item = {
                'description': line[0],
                'delimiter': line[1],
                'item': line[2],
                'success': True
            }
        else:
            item = {
                'description': 'Unable to parse file information.',
                'success': False
            }
        files.append(item)

    ret['success'] = True
    ret['files'] = files

    return ret

@view_config(route_name='codes_add', renderer='json', permission='administer')
def codes_add(request):
    ret = {'success': False}

    filename = 'country_codes.txt'
    delimiter = ';'
    TableItem = SH_Value
    code_language = Session.query(Language).\
        filter(Language.locale == 'code').\
        first()

    try:
        stream = open("%s/%s" % (codes_directory_path(), filename), 'rb')
    except IOError:
        ret['msg'] = 'File (%s) not found' % filename
        return ret

    errorCount = 0
    insertCount = 0
    msgStack = []

    csvReader = csv.reader(stream, delimiter=delimiter)
    for row in csvReader:
        # Skip the first item
        if csvReader.line_num > 1:
            inserted = _insert_code(row[1], row[0], TableItem, code_language)
            msgStack.append(inserted)
            if inserted['success'] is True:
                insertCount += 1
            elif inserted['success'] is None:
                pass
            else:
                errorCount += 1

    print codes_directory_path()

    if errorCount == 0:
        ret['success'] = True

    ret['insertCount'] = insertCount
    ret['errorCount'] = errorCount
    ret['messages'] = msgStack

    return ret

def _insert_code(value, code, TableItem, code_language):

    # Query the database to find english entry of value
    english_value_q = Session.query(TableItem).\
        filter(TableItem.value == value).\
        filter(TableItem.fk_sh_value == None).\
        filter(TableItem.fk_language == 1)
    try:
        english_value = english_value_q.one()
    except NoResultFound:
        return {'success': False, 'msg': 'No english value found for "%s", code "%s" not inserted.' % (value, code)}
    except MultipleResultsFound:
        # This should not happen (?)
        return {'success': False, 'msg': 'Multiple values found for "%s", code "%s" not inserted.' % (value, code)}

    # Check if code already exists for value
    code_value_q = Session.query(TableItem).\
        filter(TableItem.value == code).\
        filter(TableItem.original == english_value).\
        filter(TableItem.language == code_language)
    code_value = None
    try:
        code_value = code_value_q.one()
    except NoResultFound:
        # Code does not yet exist, insert it
        new_code = TableItem(code)
        new_code.language = code_language
        new_code.original = english_value
        Session.add(new_code)
        return {'success': True, 'msg': 'Code "%s" inserted for value "%s".' % (code, value)}
    except MultipleResultsFound:
        # This should not happen
        pass

    if code_value is not None:
        return {'success': None, 'msg': 'Code "%s" for value "%s" already exists.' % (code, value)}

    return {'success': False, 'msg': 'Code "%s" for value "%s" not inserted.' % (code, value)}

