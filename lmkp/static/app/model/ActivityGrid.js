Ext.define('Lmkp.model.ActivityGrid', {
    extend: 'Ext.data.Model',

	// TODO: Extract fields from Config (YAML).
    fields: [{
        name: 'id',
        type: 'int'
    }, {
        name: 'name',
        type: 'string'
    }, {
    	name: 'area',
    	type: 'string'
    }, {
    	name: 'project_use',
    	type: 'string'
    }, {
    	name: 'project_status',
    	type: 'string'
    }, {
    	name: 'year_of_investment',
    	type: 'string'
    }]

});