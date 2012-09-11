Ext.define('Lmkp.model.Evaluation5', {
    extend: 'Ext.data.Model',

    fields: [{
        name: 'year',
        type: 'int'
    },{
        name: 'agriculture',
        type: 'float'
    },{
        name: 'forestry',
        type: 'float'
    }]
});