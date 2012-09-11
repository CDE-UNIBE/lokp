Ext.define('Lmkp.model.Evaluation5', {
    extend: 'Ext.data.Model',

    fields: [{
        name: 'year',
        type: 'int'
    },{
        defaultValue: 0.,
        name: 'agriculture',
        type: 'int'
    },{
        defaultValue: 0.,
        name: 'forestry',
        type: 'int'
    },{
        defaultValue: 0.,
        name: 'mining',
        type: 'int'
    },{
        defaultValue: 0.,
        name: 'other',
        type: 'int'
    },{
        defaultValue: 0.,
        name: 'renewable_energy',
        type: 'int'
    },{
        defaultValue: 0.,
        name: 'tourism',
        type: 'int'
    }]
});