Ext.define('Lmkp.model.Involvement', {
    extend: 'Ext.data.Model',

    fields: [
        {
            type: 'string', // Either GUID of Stakeholder or Activity
            name: 'id'
        }, {
            type: 'string',
            name: 'role'
        }, {
            type: 'int',
            name: 'role_id'
        }
    ],

    associations: [
        {
            type: 'belongsTo',
            model: 'Lmkp.model.Activity',
            name: 'activity',
            getterName: 'getActivity'
        }, {
            type: 'belongsTo',
            model: 'Lmkp.model.Stakeholder',
            name: 'stakeholder',
            getterName: 'getStakeholder'
        }
    ]
});