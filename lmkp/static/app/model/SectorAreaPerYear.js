/**
 * A model to store the area (in hectares) per sector per year. Currently only
 * used in the /charts view
 */
Ext.define('Lmkp.model.SectorAreaPerYear', {
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
    },{
        defaultValue: 0.,
        name: 'industry',
        type: 'int'
    },{
        defaultValue: 0.,
        name: 'conservation',
        type: 'int'
    }]
});