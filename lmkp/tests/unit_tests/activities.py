# Some helper functions for the Activity tests.
import random
import decimal


def getReadManyActivities(testcase, format):
    if format == 'json':
        res = testcase.testapp.get('/activities/json')
        return res.json
    elif format == 'html':
        res = testcase.testapp.get('/activities/html')
        res.showbrowser()
        return res
    else:
        testcase.fail('Unknown format: %s' % format)

def createActivity(testcase, diff):
    return testcase.testapp.post_json('/activities', diff)

def getGeometry():
    return {
        'type': 'Point',
        'coordinates': [
          float(102 + decimal.Decimal(str(random.random()))),
          float(19 + decimal.Decimal(str(random.random())))
        ]
    }

def getActivityDiff():
    return {
        'activities': [
            {
              'geometry': getGeometry(),
              'taggroups': [
                {
                  'main_tag': {
                    'value': u'[A] Value A1', 
                    'key': u'[A] Dropdown 1'
                  }, 
                  'tags': [
                    {
                      'value': u'[A] Value A1', 
                      'key': u'[A] Dropdown 1', 
                      'op': 'add'
                    }
                  ], 
                  'op': 'add'
                }, {
                  'main_tag': {
                    'value': 123.45, 
                    'key': u'[A] Numberfield 1'
                  },  
                  'tags': [
                    {
                      'value': 123.45, 
                      'key': u'[A] Numberfield 1',
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