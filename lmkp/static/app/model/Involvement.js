Ext.define('Lmkp.model.Involvement', {
    extend: 'Ext.data.Model',

    fields: [
        {
            type: 'string', // Either GUID of Stakeholder or Activity
            name: 'id'
        }, {
            type: 'string',
            name: 'role'
        }
    ],

    associations: [
        {
            type: 'belongsTo',
            model: 'Lmkp.model.Activity',
            name: 'activity'
        }, {
            type: 'belongsTo',
            model: 'Lmkp.model.Stakeholder',
            name: 'stakeholder',
            getterName: 'getStakeholder'
        }
    ]
});