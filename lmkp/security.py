# To change this template, choose Tools | Templates
# and open the template in the editor.

__author__ = "Adrian Weber, Centre for Development and Environment, University of Bern"
__date__ = "$Jan 20, 2012 10:36:32 AM$"

USERS = {'editor':'editor',
    'viewer':'viewer'}
GROUPS = {'editor':['group:editors']}

def groupfinder(userid, request):
    if userid in USERS:
        return GROUPS.get(userid, [])