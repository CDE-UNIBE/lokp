# Some helper functions for the Stakeholder tests.

def getReadManyStakeholders(testcase, format):
    if format == 'json':
        res = testcase.testapp.get('/stakeholders/json')
        return res.json
    else:
        testcase.fail('Unknown format: %s' % format)

def createStakeholder(testcase, diff):
    return testcase.testapp.post_json('/stakeholders', diff)

def getStakeholderDiff():
    return {
        'stakeholders': [
            {
              'taggroups': [
                {
                  'main_tag': {
                    'value': 123.0, 
                    'key': u'[SH] Numberfield 1'
                  }, 
                  'tags': [
                    {
                      'value': 123.0, 
                      'key': u'[SH] Numberfield 1', 
                      'op': 'add'
                    }
                  ], 
                  'op': 'add'
                }, {
                  'main_tag': {
                    'value': u'asdf', 
                    'key': u'[SH] Textfield 1'
                  },  
                  'tags': [
                    {
                      'value': u'asdf', 
                      'key': u'[SH] Textfield 1', 
                      'op': 'add'
                    }
                  ], 
                  'op': 'add'
                }
              ], 
              'version': 1
            }
        ]
    }