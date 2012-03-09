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
            'filterPanel checkbox[name=filterTimeCheckbox]': {
                change: this.onTimeFilterCheck
            },
            'filterPanel checkbox[name=filterAttributeCheckbox]': {
                change: this.onAttributeFilterCheck
            },
            'filterPanel button[name=addAttributeFilter]': {
                click: this.addAttributeFilter
            },
            'filterPanel button[name=addTimeFilter]': {
            	click: this.addTimeFilter
            },
            'filterPanel gridpanel[id=filterResults]': {
            	selectionchange: this.displayActivityDetails
            },
            'filterPanel gridcolumn[name=namecolumn]': {
            	afterrender: this.renderNameColumn
            },
            'filterPanel button[id=deleteFilter]': {
            	click: this.deleteFilter
            },
            'filterPanel button[name=activateButton]': {
            	click: this.applyFilter
            },
            'filterPanel combobox[name=attributeCombo]': {
                select: this.showValueFields
            },
            'filterPanel [name=valueField]': {
            	change: this.resetActivateButton
            },
            'filterPanel combobox[name=filterOperator]': {
            	select: this.resetActivateButton
            },
        });
    },
    
    onLaunch: function() {
    	
    },
    
    resetActivateButton: function(element) {
    	var fieldset = element.up('fieldset');
    	var buttonIndex = fieldset.items.findIndex('name', 'activateButton');
    	if (buttonIndex != -1) {
    		fieldset.items.getAt(buttonIndex).toggle(false);
    	}
    },
    
    applyFilter: function(button, e, eOpts) {
    	var queryable = 'queryable=';
    	var queries = '';
    	var attrs = Ext.ComponentQuery.query('combobox[name=attributeCombo]');
    	var values = Ext.ComponentQuery.query('[name=valueField]');
    	var ops = Ext.ComponentQuery.query('combobox[name=filterOperator]');
    	var buttons = Ext.ComponentQuery.query('button[name=activateButton]');
    	if (attrs.length > 0 && values.length > 0) {
    		for (i=0; i<attrs.length; i++) {
    			if (buttons[i].pressed) { // only add value if filter is activated
	    			var currAttr = attrs[i].getValue();
	    			var currVal = values[i].getValue();
	    			var currOp = ops[i].getValue();
	    			if (currAttr && currVal) {
	    				queryable += currAttr + ",";
	    				queries += currAttr + currOp + currVal + "&";
	    			}
    			}
    		}
    	}
    	// reload store by overwriting its proxy url
    	var store = this.getActivityGridStore();
    	store.getProxy().url = 'activities/json?' + queryable + "&" + queries;
    	store.load();
    },
        
    showValueFields: function(combobox, records, eOpts) {
    	// everything specific for current fieldset
    	var fieldset = combobox.up('fieldset');
    	// remove operator field if it is already there
    	var operatorFieldIndex = fieldset.items.findIndex('name', 'filterOperator');
    	if (operatorFieldIndex != -1) {
    		fieldset.items.getAt(operatorFieldIndex).destroy();
    	}
    	// remove value field if it is already there
    	var valueFieldIndex = fieldset.items.findIndex('name', 'valueField');
    	if (valueFieldIndex != -1) {
    		fieldset.items.getAt(valueFieldIndex).destroy();
    	}
    	var xtype = records[0].get('xtype');
        // determine operator field values and insert it
        var operatorCombobox = this.getOperator(xtype);
        fieldset.insert(1, operatorCombobox);
        // determine type and categories of possible values of value field
		var valueField = this.getValueField(records[0], xtype);
		console.log(valueField);
        fieldset.insert(2, valueField);
        // reset ActivateButton
        this.resetActivateButton(combobox, records);
    },
    
    addAttributeFilter: function(button) {
        var form = Ext.ComponentQuery.query('form[id=filterForm]')[0];
        var insertIndex = form.items.length - 2; // always insert above the 2 buttons
        form.insert(insertIndex, {
        	xtype: 'fieldset',
        	name: 'attributeFieldset',
        	title: 'Attribute filter',
        	items: [{
        		xtype: 'combobox',
	        	name: 'attributeCombo',
	        	store: this.getConfigStore(),
	        	valueField: 'fieldLabel',
	        	displayField: 'name',
	        	queryMode: 'local',
	        	typeAhead: true,
	        	forceSelection: true,
	        	emptyText: 'Select attribute'
        	}, {
        		xtype: 'button',
        		name: 'activateButton',
        		text: 'Activate',
        		enableToggle: true
        	}]
        });
    },
    
    addTimeFilter: function(button) {
    	Ext.Msg.alert('Not yet implemented', 'This function will be implemented soon.');
    },
    
	deleteFilter: function() {
		// TODO
    	// // uncheck filter fieldsets
    	// var cbattr = Ext.ComponentQuery.query('checkbox[name=filterAttributeCheckbox]')[0];
    	// cbattr.setValue(false);
    	// var cbtime = Ext.ComponentQuery.query('checkbox[name=filterTimeCheckbox]')[0];
    	// cbtime.setValue(false);
    	// // reset proxy url and reload store
    	// var actStore = this.getActivityGridStore();
        // actStore.getProxy().url = 'activities/json';
        // actStore.load();
//         
//         
        // var t = Ext.ComponentQuery.query('combobox[name=attributeCombo]')[0];
        // t.up('fieldset').insert(1, {
                // xtype: 'combobox',
                // name: 'attributeCombo',
                // emptyText: 'Specify value',
                // store: this.getConfigStore(),
                // queryMode: 'local',
                // editable: false,
                // width: 166
            // });
//             
        // var x = Ext.ComponentQuery.query('combobox[name=attributeCombo]');
      	// var form = t.up('form').getForm();
        // var y = form.findField('attributeCombo');
        // console.log(y);
//         
//         
        // console.log(x);
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
    	var cb = Ext.create('Ext.form.field.ComboBox', {
    		name: 'filterOperator',
    		store: store,
    		displayField: 'displayOperator',
    		valueField: 'queryOperator',
    		queryMode: 'local',
    		editable: false,
    		width: 50
    	});
    	// default value: the first item of the store
    	cb.setValue(store.getAt('0').get('queryOperator'));
    	return cb;
    },
    
    getValueField: function(record, xtype) {
    	var fieldName = 'valueField';
    	// try to find categories
    	var selectionValues = record.get('store');
        if (selectionValues) {      // categories of possible values available, create ComboBox
        	var valueField = Ext.create('Ext.form.field.ComboBox', {
        		name: fieldName,
                store: selectionValues,
                queryMode: 'local',
                editable: false,
                value: selectionValues[0]
        	});
        } else {                    // no categories available, create field based on xtype
            switch (xtype) {
            	case "numberfield":
            		var valueField = Ext.create('Ext.form.field.Number', {
            			name: fieldName,
            			emptyText: 'Specify number value'
            		});
            		break;
            	default:
            		var valueField = Ext.create('Ext.form.field.Text', {
            			name: fieldName,
            			emptyText: 'Specify value'
            		});
            		break;
            }
        }
        return valueField;
    }
});
