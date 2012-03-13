Ext.define('Lmkp.controller.Filter', {
    extend: 'Ext.app.Controller',
    
    models: ['Config', 'ActivityGrid'],
    stores: ['Config', 'ActivityGrid'],
   
    views: ['Filter'],

    init: function() {
        this.getConfigStore().load();
        this.control({
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
            'filterPanel button[id=deleteAllFilters]': {
            	click: this.deleteAllFilters
            },
            'filterPanel button[name=activateAttributeButton]': {
            	click: this.applyFilter
            },
            'filterPanel button[name=activateTimeButton]': {
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
            'filterPanel datefield[name=dateField]': {
            	change: this.resetActivateButton
            },
            'filterPanel button[name=deleteButton]': {
            	click: this.deleteFilter
            }
        });
    },
    
    onLaunch: function() {
    	
    },
    
    resetActivateButton: function(element) {
    	var attributePanel = element.up('panel');
    	// try to find attribute button
    	var attrButtonIndex = attributePanel.items.findIndex('name', 'activateAttributeButton');
    	if (attrButtonIndex != -1) {
    		attributePanel.items.getAt(attrButtonIndex).toggle(false);
    	}
    	// try to find time button
    	var timeButtonIndex = attributePanel.items.findIndex('name', 'activateTimeButton');
    	if (timeButtonIndex != -1) {
    		attributePanel.items.getAt(timeButtonIndex).toggle(false);
    	}
    	this.applyFilter();
    },
    
    applyFilter: function(button, e, eOpts) {
    	
    	var queryable = 'queryable=';
    	var queries = '';
    	// attribute filter
    	var attrs = Ext.ComponentQuery.query('combobox[name=attributeCombo]');
    	var values = Ext.ComponentQuery.query('[name=valueField]');
    	var ops = Ext.ComponentQuery.query('combobox[name=filterOperator]');
    	var attrButtons = Ext.ComponentQuery.query('button[name=activateAttributeButton]');
    	if (attrs.length > 0 && values.length > 0) {
    		for (i=0; i<attrs.length; i++) {
    			if (attrButtons[i].pressed) { // only add value if filter is activated
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
    	// time filter (only 1 possible)
    	var date = Ext.ComponentQuery.query('datefield[name=dateField]')[0];
    	var timeButton = Ext.ComponentQuery.query('button[name=activateTimeButton]')[0];
    	if (date) {
    		if (timeButton.pressed) { // only add value if filter is activated
    			queries += 'timestamp=' + date.getValue().toUTCString();
    		}
    	}
    	// reload store by overwriting its proxy url
    	var store = this.getActivityGridStore();
    	store.getProxy().url = 'activities/json?' + queryable + "&" + queries;
    	store.load();
    },
        
    showValueFields: function(combobox, records, eOpts) {
    	// everything specific for current attributePanel
    	var attributePanel = combobox.up('panel');
    	// remove operator field if it is already there
    	var operatorFieldIndex = attributePanel.items.findIndex('name', 'filterOperator');
    	if (operatorFieldIndex != -1) {
    		attributePanel.items.getAt(operatorFieldIndex).destroy();
    	}
    	// remove value field if it is already there
    	var valueFieldIndex = attributePanel.items.findIndex('name', 'valueField');
    	if (valueFieldIndex != -1) {
    		attributePanel.items.getAt(valueFieldIndex).destroy();
    	}
    	var xtype = records[0].get('xtype');
        // determine operator field values and insert it
        var operatorCombobox = this.getOperator(xtype);
        attributePanel.insert(1, operatorCombobox);
        // determine type and categories of possible values of value field
		var valueField = this.getValueField(records[0], xtype);
        attributePanel.insert(2, valueField);
        // reset ActivateButton
        this.resetActivateButton(combobox, records);
    },
    
    addAttributeFilter: function(button, e, eOpts) {
        var form = Ext.ComponentQuery.query('panel[id=filterForm]')[0];
        var insertIndex = form.items.length - 2; // always insert above the 2 buttons
        var cbox = Ext.create('Ext.form.field.ComboBox', {
        	name: 'attributeCombo',
        	store: this.getConfigStore(),
        	valueField: 'fieldLabel',
        	displayField: 'name',
        	queryMode: 'local',
        	typeAhead: true,
        	forceSelection: true,
        	value: this.getConfigStore().getAt('0'),
        	flex: 0,
        	margin: '0 5 5 0'
        });
        form.insert(insertIndex, {
        	xtype: 'panel',
        	name: 'attributePanel',
        	// anchor: '100%',
        	border: 0,
        	layout: {
        		type: 'hbox',
        		flex: 'stretch'
        	},
        	items: [
        		cbox, 
        	{
        		xtype: 'panel', // empty panel for spacing
        		flex: 1,
        		border: 0
        	}, {
        		xtype: 'button',
        		name: 'activateAttributeButton',
        		text: '[&#10003;] Activate',
        		tooltip: 'Click to activate this filter',
        		enableToggle: true,
        		flex: 0,
        		margin: '0 5 0 0'
        	}, {
        		xtype: 'button',
        		name: 'deleteButton',
        		text: '[x] Delete',
        		tooltip: 'Click to delete this filter',
        		enableToggle: false,
        		flex: 0
        	}]
        });
        // show initial filter
        this.showValueFields(cbox, [this.getConfigStore().getAt('0')]);
    },
    
    addTimeFilter: function(button, e, eOpts) {
    	var form = Ext.ComponentQuery.query('panel[id=filterForm]')[0];
        var insertIndex = form.items.length - 2; // always insert above the 2 buttons
        var picker = Ext.create('Ext.form.field.Date', {
        	name: 'dateField',
        	fieldLabel: 'Date',
        	value: new Date() // defaults to today
        });
        form.insert(insertIndex, {
        	xtype: 'panel',
        	name: 'timePanel',
        	border: 0,
        	layout: {
        		type: 'hbox',
        		flex: 'stretch'
        	},
        	items: [
        		picker,
        	{
        		xtype: 'panel', // empty panel for spacing
        		flex: 1,
        		border: 0
        	}, {
        		xtype: 'button',
        		name: 'activateTimeButton',
        		text: '[&#10003;] Activate',
        		tooltip: 'Click to activate this filter',
        		enableToggle: true,
        		flex: 0,
        		margin: '0 5 0 0'
        	}, {
        		xtype: 'button',
        		name: 'deleteButton',
        		text: '[x] Delete',
        		tooltip: 'Click to delete this filter',
        		enableToggle: false,
        		flex: 0
        	}]
        });
        // disable 'add' button
        var button = Ext.ComponentQuery.query('button[name=addTimeFilter]')[0];
        if (button) {
        	button.disable();
        }
    },
    
    deleteFilter: function(button, e, eOpts) {
    	var attributePanel = button.up('panel');
    	var form = Ext.ComponentQuery.query('panel[id=filterForm]')[0];
    	// if time was filtered, re-enable its 'add' button
    	if (attributePanel.name == 'timePanel') {
    		var button = Ext.ComponentQuery.query('button[name=addTimeFilter]')[0];
	        if (button) {
	        	button.enable();
	        }
    	}
    	if (form.items.contains(attributePanel)) {
    		form.remove(attributePanel, true);
    		attributePanel.destroy();
    	}
    	this.applyFilter();
    },
    
	deleteAllFilters: function() {
		var panels = Ext.ComponentQuery.query('panel[name=attributePanel]');
		panels = panels.concat(Ext.ComponentQuery.query('panel[name=timePanel]'));
		if (panels.length > 0) {
			form = Ext.ComponentQuery.query('panel[id=filterForm]')[0];
			for (i=0; i<panels.length; i++) {
				// if time was filtered, re-enable its 'add' button
				if (panels[i].name == 'timePanel') {
		    		var button = Ext.ComponentQuery.query('button[name=addTimeFilter]')[0];
			        if (button) {
			        	button.enable();
			        }
		    	}
				if (form.items.contains(panels[i])) {
					form.remove(panels[i], true);
					panels[i].destroy();
				}
			}
		}
		this.applyFilter();
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
    		width: 50,
    		margin: '0 5 0 0'
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
                value: selectionValues[0],
                margin: '0 5 0 0'
        	});
        } else {                    // no categories available, create field based on xtype
            switch (xtype) {
            	case "numberfield":
            		var valueField = Ext.create('Ext.form.field.Number', {
            			name: fieldName,
            			emptyText: 'Specify number value',
            			margin: '0 5 0 0'
            		});
            		break;
            	default:
            		var valueField = Ext.create('Ext.form.field.Text', {
            			name: fieldName,
            			emptyText: 'Specify value',
            			margin: '0 5 0 0'
            		});
            		break;
            }
        }
        return valueField;
    }
});
