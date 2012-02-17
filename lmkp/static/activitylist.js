Ext.define('DyLmkp.model.Activity', {
    'fields': [{
        'type': 'string',
        'name': 'project_use'
    }, {
        'type': 'string',
        'name': 'name'
    }, {
        'type': 'string',
        'name': 'project_status'
    }, {
        'type': 'number',
        'name': 'area'
    }, {
        'type': 'number',
        'name': 'year_of_investment'
    }, {
        'type': 'string',
        'name': 'Spatial uncertainty'
    }, {
        'type': 'string',
        'name': 'id'
    }],
    'proxy': {
        'url': '/activities',
        'type': 'ajax',
        'reader': {
            'root': 'activities',
            'type': 'json'
        }
    },
'extend': 'Ext.data.Model'
});