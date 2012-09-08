Ext.define('Lmkp.model.ShYamlScan', {
    extend: 'Ext.data.Model',

    fields: [{
        name: 'value',
        type: 'string'
    }, {
        name: 'translation',
        type: 'string'
    }, {
        name: 'exists',
        type: 'boolean'
    }, {
        name: 'mandatory',
        type: 'boolean'
    }, {
        name: 'keyvalue',
        type: 'string'
    }, {
        name: 'local',
        type: 'boolean'
    }],

    proxy: {
        type: 'ajax',
        url: '/config/scan/stakeholders',
        reader: {
            type: 'json'
        },
        folderSort: true
    }
});