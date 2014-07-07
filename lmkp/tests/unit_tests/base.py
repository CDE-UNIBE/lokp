CONFIG_FILE = 'unit_tests.ini'
USERNAME = 'admin'
PASSWORD = 'asdf'

def doLogin(testcase):
    res = testcase.testapp.get('/login')
    form = res.form
    form['login'] = USERNAME
    form['password'] = PASSWORD
    form.submit('form.submitted')

