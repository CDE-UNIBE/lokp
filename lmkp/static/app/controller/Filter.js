Ext.define('Lmkp.controller.Filter', {
    extend: 'Ext.app.Controller',
    
    models: ['Config', 'ActivityGrid'],
    stores: ['Config', 'ActivityGrid'],
   
    views: ['Filter'],

    init: function() {
        this.getConfigStore().load();
        this.control({
            'filterPanel button[id=filterSubmit]': {
                click: this.onFilterSubmit
            },
            'filterPanel combobox[id=filterAttribute]': {
                select: this.onAttributeSelect
            },
            'filterPanel checkbox[name=filterTimeCheckbox]': {
                change: this.onTimeFilterCheck
            },
            'filterPanel checkbox[name=filterAttributeCheckbox]': {
                change: this.onAttributeFilterCheck
            },
            'filterPanel button[id=filterAdd]': {
                click: this.onFilterAdd
            },
            'filterPanel gridpanel[id=filterResults]': {
            	selectionchange: this.displayActivityDetails
            },
            'filterPanel gridcolumn[name=namecolumn]': {
            	afterrender: this.renderNameColumn
            }
        });
    },
    
    onLaunch: function() {
    	
    },
    
    onFilterSubmit: function(button) {
        var queryable = 'queryable=';
        var queries = '';
        var filterForm = button.up('form').getForm();
        var filterAttributeCheckbox = filterForm.findField('filterAttributeCheckbox').getValue();
        var filterAttributeAttribute = filterForm.findField('filterAttribute').getValue(); 
        if (filterAttributeCheckbox && filterAttributeAttribute != null && filterForm.findField('filterValue').getValue() != null && filterForm.findField('filterValue').getValue() != '') {
            // add attribute filter to queryable
            queryable += filterAttributeAttribute + ",";
            // add attribute filter to return values
            queries += filterAttributeAttribute + filterForm.findField('filterOperator').getValue() + filterForm.findField('filterValue').getValue();
            console.log(queries);
        }
        var filterTimeCheckbox = filterForm.findField('filterTimeCheckbox').getValue();
        if (filterTimeCheckbox) {
            // add time filter to return values
            // TODO: add time filter
            /**
            var sliderValues = filterForm.findField('theslider').getValues();
            queries += 'startTime=' + sliderValues[0] + '&';
            queries += 'endTime=' + sliderValues[1] + '&';
            */
           	Ext.MessageBox.alert("Coming soon.", "Time filter function will be implemented soon.");
        }
        var actStore = this.getActivityGridStore();
        // overwrite proxy url to load filtered activities
        actStore.getProxy().url = 'activities/json?' + queryable + '&' + queries;
        actStore.load();
    },
        
    onAttributeSelect: function(combo, records) {
        // remove value field first if it is already there
        var valueField = combo.up('form').getForm().findField('filterValue');
        if (valueField) {
            valueField.destroy();
        }
        // remove operator field first if it is already there
        var operatorField = combo.up('form').getForm().findField('filterOperator');
        if (operatorField) {
        	operatorField.destroy();
        }
        var cboperator = this.getOperator(records[0].get('xtype'));
        combo.up('fieldset').insert(1, cboperator);
        var selectionValues = records[0].get('store');
        if (selectionValues) {      // categories of possible values available
            combo.up('fieldset').insert(2, {
                xtype: 'combobox',
                name: 'filterValue',
                emptyText: 'Specify value',
                store: selectionValues,
                queryMode: 'local',
                editable: false,
                width: 166
            });
        } else {                    // no categories available, define xtype
            var xtype = records[0].get('xtype');
            combo.up('fieldset').insert(2, {
                xtype: xtype,
                name: 'filterValue',
                emptyText: 'Specify value',
                width: 166
            });
        }
        var filterSubmitButton = Ext.ComponentQuery.query('button[id=filterSubmit]')[0];
        filterSubmitButton.enable();
    }, 
    
    onTimeFilterCheck: function(field, newValue, oldValue) {
        var filterAttributeCheckbox = Ext.ComponentQuery.query('checkbox[name=filterAttributeCheckbox]')[0];
        var filterSubmitButton = Ext.ComponentQuery.query('button[id=filterSubmit]')[0];
        if (newValue || filterAttributeCheckbox.checked) {
            filterSubmitButton.enable();
        } else {
            filterSubmitButton.disable();
        }
    },
    
    onAttributeFilterCheck: function(field, newValue, oldValue) {
        var filterTimeCheckbox = Ext.ComponentQuery.query('checkbox[name=filterTimeCheckbox]')[0];
        var filterSubmitButton = Ext.ComponentQuery.query('button[id=filterSubmit]')[0];
        var filterAttribute = field.up('form').getForm().findField('filterAttribute').getValue();
        if (!newValue && !filterTimeCheckbox.checked) {
            filterSubmitButton.disable();
        }
        if (newValue && filterAttribute) {
            filterSubmitButton.enable();
        }
    },
    
    onFilterAdd: function(button) {
        Ext.MessageBox.alert("Coming soon.", "This function will be implemented soon.");
    },
    
    renderNameColumn: function() {
    	col = Ext.ComponentQuery.query('filterPanel gridcolumn[name=namecolumn]')[0];
    	col.renderer = function(value, p, record) {
    		return Ext.String.format(
    			'{0} [Province ABC, District XYZ]',
    			value
    		);
    	}
    },
    
    displayActivityDetails: function(view, selected, eOpts) {
    	if (selected.length) {
	    	var detailPanel = Ext.ComponentQuery.query('filterPanel panel[id=detailPanel]')[0];
	    	detailPanel.tpl.overwrite(detailPanel.body, selected[0].data);
	    }
    },
    
    getOperator: function(xType) {
    	// prepare values of the store depending on selected xType
    	switch (xType) {
    		case "combo": // possibilities: == (eq) | != (ne)
    			var data = [
    				{'queryOperator': '__eq=', 'displayOperator': '=='},
    				{'queryOperator': '__ne=', 'displayOperator': '!='}
    			];
    			break;
    		case "textfield": // possibilities: == (like)
    			var data = [{'queryOperator': '__like=', 'displayOperator': '=='}];
    			break;
    		default: // default is also used for numberfield
    			var data = [
    				{'queryOperator': '__eq=', 'displayOperator': '=='},
    				{'queryOperator': '__lt=', 'displayOperator': '<'},
    				{'queryOperator': '__lte=', 'displayOperator': '<='},
    				{'queryOperator': '__gte=', 'displayOperator': '>='},
    				{'queryOperator': '__gt=', 'displayOperator': '>'},
    				{'queryOperator': '__ne=', 'displayOperator': '!='},
    			];
    			break;
    	}
    	// populate the store
    	var store = Ext.create('Ext.data.Store', {
    		fields: ['queryOperator', 'displayOperator'],
    		data: data
    	});
    	// configure the checkbox
    	var cb = Ext.create('Ext.form.ComboBox', {
    		name: 'filterOperator',
    		store: store,
    		displayField: 'displayOperator',
    		valueField: 'queryOperator',
    		queryMode: 'local',
    		editable: false
    	});
    	// default value: the first item of the store
    	cb.setValue(store.getAt('0').get('queryOperator'));
    	return cb;
    }
});
