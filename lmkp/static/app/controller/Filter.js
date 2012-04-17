Ext.define('Lmkp.controller.Filter', {
    extend: 'Ext.app.Controller',
    
    stores: [
    	'Config',
    	'ActivityGrid'
    ],
   
    views: [
    	'Filter',
    	'DetailPanel',
    	'activities.Details',
    	'activities.History'
    ],

    init: function() {
        // get configStore and load it
        this.getConfigStore().load()
        this.control({
            'filterPanel button[name=addAttributeFilter]': {
                click: this.addAttributeFilter
            },
            'filterPanel button[name=addTimeFilter]': {
                click: this.addTimeFilter
            },
            'filterPanel gridpanel[id=filterResults]': {
                selectionchange: this.showActivity
            },
            'filterPanel tabpanel[id=detailPanel]': {
            	tabchange: this.showActivity
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
            },
            'filterPanel combobox[name=logicalOperator]': {
                select: this.applyFilter
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
        var queryable = [];
        var queries = [];
        var queryCount = 0;
        // attribute filter
        var attrs = Ext.ComponentQuery.query('combobox[name=attributeCombo]');
        var values = Ext.ComponentQuery.query('[name=valueField]');
        var ops = Ext.ComponentQuery.query('combobox[name=filterOperator]');
        var attrButtons = Ext.ComponentQuery.query('button[name=activateAttributeButton]');
        if (attrs.length > 0 && values.length > 0) {
            for (var i=0; i<attrs.length; i++) {
                if (attrButtons[i].pressed) { // only add value if filter is activated
                    var currAttr = attrs[i].getValue();
                    var currVal = values[i].getValue();
                    var currOp = ops[i].getValue();
                    if (currAttr && currVal) {
                        // only add attribute to queryable if not already there
                        if (!this._isInArray(queryable, currAttr)) {
                            queryable.push(currAttr);
                        }
                        queries.push(currAttr + currOp + currVal);
                        // add query to count
                        queryCount++;
                    }
                }
            }
        }
        // time filter (only 1 possible)
        var date = Ext.ComponentQuery.query('datefield[name=dateField]')[0];
        var timeButton = Ext.ComponentQuery.query('button[name=activateTimeButton]')[0];
        if (date) {
            if (timeButton.pressed) { // only add value if filter is activated
                queries.push('timestamp=' + Ext.Date.format(date.getValue(), "Y-m-d H:i:s.u"));
                // add query to count
                queryCount++;
            }
        }
        // reload store by overwriting its proxy url
        var query_url = '';
        if (queryable.length > 0) {
            query_url += 'queryable=' + queryable.join(',') + '&';
        }
        if (queries.length > 0) {
            query_url += queries.join('&');
        }
        // logical operator
        var operatorCombo = Ext.ComponentQuery.query('combobox[name=logicalOperator]')[0];
        if (operatorCombo) {
            if (queryCount >= 2) {
                operatorCombo.setVisible(true);
                query_url += '&logical_op=' + operatorCombo.getValue();
            } else {
                operatorCombo.setVisible(false);
            }
        }
        var store = this.getActivityGridStore();
        store.getProxy().url = 'activities/json?' + query_url;
        store.load();
        if (query_url) {
        	// move paging to back to page 1 when filtering (otherwise may show empty page instead of results)
	        Ext.ComponentQuery.query('pagingtoolbar[id=activityGridPagingToolbar]')[0].moveFirst();
        }
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
        // expand form if collapsed
        if (form.collapsed) {
        	form.toggleCollapse();
        }
        var insertIndex = form.items.length - 1; // always insert above the 2 buttons
        var cbox = Ext.create('Ext.form.field.ComboBox', {
            name: 'attributeCombo',
            store: this.getConfigStore(),
            valueField: 'name',
            displayField: 'fieldLabel',
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
            border: 0,
            anchor: '100%',
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
                text: Lmkp.ts.msg("activate-button"),
                tooltip: Lmkp.ts.msg("activate-tooltip"),
                iconCls: 'toolbar-button-accept',
                enableToggle: true,
                flex: 0,
                margin: '0 5 0 0'
            }, {
                xtype: 'button',
                name: 'deleteButton',
                text: Lmkp.ts.msg("delete-button"),
                tooltip: Lmkp.ts.msg("deletefilter-tooltip"),
                iconCls: 'toolbar-button-delete',
                enableToggle: false,
                flex: 0
            }]
        });
        // show initial filter
        this.showValueFields(cbox, [this.getConfigStore().getAt('0')]);
        // re-layout container
        form.ownerCt.layout.layout(); 	// TODO: Figure out why both of ...
        form.forceComponentLayout();	// ... these lines are needed (see also addTimeFilter)
    },
    
    addTimeFilter: function(button, e, eOpts) {
        var form = Ext.ComponentQuery.query('panel[id=filterForm]')[0];
        // expand form if collapsed
        if (form.collapsed) {
        	form.toggleCollapse();
        }
        var insertIndex = form.items.length - 1; // always insert above the 2 buttons
        var picker = Ext.create('Ext.form.field.Date', {
            name: 'dateField',
            fieldLabel: Lmkp.ts.msg("date-label"),
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
                text: Lmkp.ts.msg("activate-button"),
                tooltip: Lmkp.ts.msg("activate-tooltip"),
                iconCls: 'toolbar-button-accept',
                enableToggle: true,
                flex: 0,
                margin: '0 5 5 0'
            }, {
                xtype: 'button',
                name: 'deleteButton',
                text: Lmkp.ts.msg("delete-button"),
                tooltip: Lmkp.ts.msg("deletefilter-tooltip"),
                iconCls: 'toolbar-button-delete',
                enableToggle: false,
                flex: 0
            }]
        });
        // disable 'add' button
        var button = Ext.ComponentQuery.query('button[name=addTimeFilter]')[0];
        if (button) {
            button.disable();
        }
        form.ownerCt.layout.layout(); 	// TODO: Figure out why both of ...
        form.forceComponentLayout();	// ... these lines are needed (see also addAttributeFilter)
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
	        // collapse form if expanded
	        if (!form.collapsed) {
	        	form.toggleCollapse();
	        }
        }
        this.applyFilter();
    },
    
    renderNameColumn: function() {
        col = Ext.ComponentQuery.query('filterPanel gridcolumn[name=namecolumn]')[0];
        col.renderer = function(value, p, record) {
        	if (value) {
            	return Ext.String.format('{0}', value);
        	} else {
        		return Lmkp.ts.msg("unnamed-activity");
        	}
        }
    },
    
    showActivity: function() {
    	var grid = Ext.ComponentQuery.query('filterPanel gridpanel[id=filterResults]')[0];
    	var selectedRecord = grid.getSelectionModel().getSelection();
		var detailPanel = Ext.ComponentQuery.query('filterPanel tabpanel[id=detailPanel]')[0];
		var selectedTab = detailPanel.getActiveTab();
			switch (selectedTab.getXType()) {
				case "activityHistoryTab":
					var uid = (selectedRecord.length > 0) ? selectedRecord[0].raw['activity_identifier'] : null;
					this._populateHistoryTab(selectedTab, uid)
					break;
				default: 	// default is: activityDetailTab
					this._populateDetailsTab(selectedTab, selectedRecord);
					break;
			}
    },
    
    getOperator: function(xType) {
        // prepare values of the store depending on selected xType
        switch (xType) {
            case "combo": // possibilities: == (eq) | != (ne)
                var data = [
                {
                    'queryOperator': '__eq=',
                    'displayOperator': '=='
                },

                {
                    'queryOperator': '__ne=',
                    'displayOperator': '!='
                }
                ];
                break;
            case "textfield": // possibilities: == (like)
                var data = [{
                    'queryOperator': '__like=',
                    'displayOperator': '=='
                }];
                break;
            default: // default is also used for numberfield
                var data = [
                {
                    'queryOperator': '__eq=',
                    'displayOperator': '=='
                },

                {
                    'queryOperator': '__lt=',
                    'displayOperator': '<'
                },

                {
                    'queryOperator': '__lte=',
                    'displayOperator': '<='
                },

                {
                    'queryOperator': '__gte=',
                    'displayOperator': '>='
                },

                {
                    'queryOperator': '__gt=',
                    'displayOperator': '>'
                },

                {
                    'queryOperator': '__ne=',
                    'displayOperator': '!='
                },
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
    },
    
    _populateDetailsTab: function(panel, data) {
    		console.log(data);
    	if (data.length > 0) {
	        var html = '';
	        for (var i in data[0].data) {
	        	// console.log(i + " " + data[0].data[i]);
	            // dont show id
	            if (i != 'id') {
	            	/**
	            	 * The default NULL-value for unspecified number values is 0.
	            	 * Assumption: 0 as a number value (currently for Area and Year of Investment)
	            	 * is not useful and should rather not be displayed.
	            	 */
	            	var val = (data[0].data[i] == 0) ? '' : data[0].data[i]; 
	            	html += Ext.String.format('<b>{0}</b>: {1}<br/>', i, val);
	            }
	        }
	        panel.update(html);
       	}
    },
    
    _populateHistoryTab: function(panel, uid) {
    	if (uid) {
	    	Ext.Ajax.request({
	    		url: '/activities/history/' + uid,
	    		success: function(response, opts) {
	
			    	// remove initial text if still there
			    	if (panel.down('panel[name=history_initial]')) {
			    		panel.remove(panel.down('panel[name=history_initial]'));
			    	}
			    	
			    	// remove old panels
			    	if (panel.down('panel[name=history_active]')) {
			    		panel.remove(panel.down('panel[name=history_active]'));
			    	}
			    	if (panel.down('panel[name=history_deleted]')) {
			    		panel.remove(panel.down('panel[name=history_deleted]'));
			    	}
			    	while (panel.down('panel[name=history_overwritten]')) {
			    		panel.remove(panel.down('panel[name=history_overwritten]'));
			    	}
	
					// get data
	    			var json = Ext.JSON.decode(response.responseText);
			    	// prepare template
			    	var tpl = new Ext.XTemplate(
			    		'<tpl for="attrs">',
			    			'<span class="{cls}"><b>{k}</b>: {v}<br/></span>',
			    		'</tpl>',
			    		'<p>&nbsp;</p>',
			    		'<tpl if="deleted != null">',
			    			'Deleted: <span class="deleted"><b>{deleted}</b></span>',
			    			'<p>&nbsp;</p>',
			    		'</tpl>',
			    		'<p class="version_info">Version {version} created on {timestamp}.<br/>',
			    		'Data provided by {username} [userid: {userid}].<br/>',
			    		'Additional source of information: {source}</p>'
			    	);
			    	
			    	// add panel for current version if there is one
			    	if (json.data.active) {
			    		// prepare data
			    		var o = json.data.active;
			    		var ts = Ext.Date.format(Ext.Date.parse(o.timestamp, "Y-m-d H:i:s.u"), "Y/m/d H:i");
			    		var changes = Ext.JSON.decode(o.changes);
			    		
			    		// first, add general data about activity and changeset
			    		var data = {
			    			username: o.username,
			    			userid: o.userid,
			    			source: o.source,
			    			timestamp: ts,
			    			version: o.version,
			    			id: o.id,
			    			activity_identifier: o.activity_identifier
			    		}
			    		// add all remaining data: the key/value pairs
			    		attrs = []
			    		for (attr in o) {
			    			// do not add general data (again) and do not add 'changes'
			    			if (!data[attr] && attr != 'changes') {
			    				// default class
			    				var cls = 'unchanged';
			    				// check for changes and update class accordingly
			    				if (changes[attr]) {
			    					cls = changes[attr];
			    				}
			    				attrs.push({
			    					k: attr,
			    					v: o[attr],
			    					cls: cls
			    				});
			    			}
			    		}
			    		data["attrs"] = attrs;
			    		// check for deleted attributes
			    		var deleted = []
			    		for (var i in changes) {
			    			if (changes[i] == 'deleted') {
			    				deleted.push(i);
			    			}
			    		}
			    		data["deleted"] = (deleted.length > 0) ? deleted.join(", ") : null;
			    		
			    		// create panel
				        var activePanel = Ext.create('Ext.panel.Panel', {
				        	name: 'history_active',
				        	title: '[Current] Version ' + o.version + ' (' + ts + ')',
				        	collapsible: true,
				        	collapsed: true
				        });
				        // add panel and apply template
				        panel.add(activePanel);
				        tpl.overwrite(activePanel.body, data);
			       	}
			       	
			       	// add panel for deleted version if there is one
			       	if (json.data.deleted) {
			       		// prepare data
			       		var o = json.data.deleted;
			       		var ts = Ext.Date.format(Ext.Date.parse(o.timestamp, "Y-m-d H:i:s.u"), "Y/m/d H:i");
			       		
			       		// first, add general data about activity and changeset
			    		var data = {
			    			username: o.username,
			    			userid: o.userid,
			    			source: o.source,
			    			timestamp: ts,
			    			version: o.version,
			    			id: o.id,
			    			activity_identifier: o.activity_identifier
			    		}
			    		
			    		// special template
			    		var deletedTpl = new Ext.XTemplate(
				    		'<span class="deleted"><b>Deleted</b></span>',
				    		'<p>&nbsp;</p>',
				    		'<p class="version_info">This activity was deleted on {timestamp} by {username} [userid: {userid}].<br/>',
				    		'Additional source of information: {source}</p>'
				    	);
				    	
				    	// create panel
				    	var deletedPanel = Ext.create('Ext.panel.Panel', {
				    		name: 'history_deleted',
				    		title: '[Deleted] (' + ts + ')',
				    		collapsible: true,
				    		collapsed: true
				    	});
				    	
				    	// add panel and apply template
				    	panel.add(deletedPanel);
				    	deletedTpl.overwrite(deletedPanel.body, data);
			       	}
			        
			        // add panels for old versions if there are any
			        if (json.data.overwritten.length > 0) {
			        	for (var i in json.data.overwritten) {
			        		// prepare data
			        		var o = json.data.overwritten[i];
			        		var ts = Ext.Date.format(Ext.Date.parse(o.timestamp, "Y-m-d H:i:s.u"), "Y/m/d H:i");
					        var changes = Ext.JSON.decode(o.changes);
					        // first, add general data about activity and changeset
				    		var data = {
				    			username: o.username,
				    			userid: o.userid,
				    			source: o.source,
				    			timestamp: ts,
				    			version: o.version,
				    			id: o.id,
				    			activity_identifier: o.activity_identifier
				    		};
				    		// add all remaining data: the key/value pairs
				    		attrs = [];
				    		for (attr in o) {
				    			// do not add general data (again) and do not add 'changes'
				    			if (!data[attr] && attr != 'changes') {
				    				// default class
				    				var cls = 'unchanged';
				    				// check for changes and update class accordingly
				    				if (changes[attr]) {
				    					cls = changes[attr];
				    				}
				    				attrs.push({
				    					k: attr,
				    					v: o[attr],
				    					cls: cls
				    				});
				    			}
				    		}
				    		data["attrs"] = attrs;
				    		// check for deleted attributes
				    		var deleted = []
				    		for (var i in changes) {
				    			if (changes[i] == 'deleted') {
				    				deleted.push(i);
				    			}
				    		}
				    		data["deleted"] = (deleted.length > 0) ? deleted.join(", ") : null;
				    		// create panel
				    		var p = Ext.create('Ext.panel.Panel', {
					        	name: 'history_overwritten',
					        	title: 'Version ' + o.version + ' (' + ts + ')',
					        	collapsible: true,
					        	collapsed: true
				    		});
					        panel.add(p);
					        tpl.overwrite(p.body, data);
			        	}
					}
					
					// in case no active and no overwritten activities were found (this should never happen),
					// show at least something.
					// using the initial panel because this will be removed when selected the next activity
					if (!json.data.active && !json.data.deleted && json.data.overwritten.length == 0) {
						panel.add({
							xtype: 'panel',
					    	border: 0,
					    	name: 'history_initial',
					    	html: 'No history found for this activity',
					    	collapsible: false,
					    	collapsed: false
						})
					}
					
					// layout does not seem to work if panel is expanded on start, therefore this is done
					// after everything was added.
					// TODO: find out why ...
					if (activePanel) {
						activePanel.toggleCollapse();
					}
					if (deletedPanel) {
						deletedPanel.toggleCollapse();
					}
	    		}
	    	});
    	}
    },

    _isInArray: function(arr, obj) { // http://stackoverflow.com/questions/143847/best-way-to-find-an-item-in-a-javascript-array
        for(var i=0; i<arr.length; i++) {
            if (arr[i] == obj) return true;
        }
    }
});
