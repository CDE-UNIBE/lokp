Ext.define('Lmkp.controller.editor.Table', {
    extend: 'Ext.app.Controller',

    stores: [
    'Config',
    'ActivityGrid'
    ],

    views: [
    'editor.Detail',
    'activities.Details',
    'activities.History'
    ],

    init: function() {
        // Get the Config store and load it
        this.getConfigStore().load();

        this.control({
            'lo_editortablepanel button[name=addAttributeFilter]': {
                click: this.addAttributeFilter
            },
            'lo_editortablepanel button[name=addTimeFilter]': {
                click: this.addTimeFilter
            },
            'lo_editortablepanel tabpanel[id=detailPanel]': {
                tabchange: this.showActivity
            },
            'lo_editortablepanel button[id=deleteAllFilters]': {
                click: this.deleteAllFilters
            },
            'lo_editortablepanel button[name=activateAttributeButton]': {
                click: this.applyFilter
            },
            'lo_editortablepanel button[name=activateTimeButton]': {
                click: this.applyFilter
            },
            'lo_editortablepanel combobox[name=attributeCombo]': {
                select: this.showValueFields
            },
            'lo_editortablepanel [name=valueField]': {
                change: this.resetActivateButton
            },
            'lo_editortablepanel combobox[name=filterOperator]': {
                select: this.resetActivateButton
            },
            'lo_editortablepanel datefield[name=dateField]': {
                change: this.resetActivateButton
            },
            'lo_editortablepanel button[name=deleteButton]': {
                click: this.deleteFilter
            },
            'lo_editortablepanel combobox[name=logicalOperator]': {
                select: this.applyFilter
            },
            'gridpanel[itemId=resultgrid] gridcolumn[name=nameofinvestorcolumn]': {
                afterrender: this.renderNameofinvestorColumn
            },
            'gridpanel[itemId=resultgrid] gridcolumn[name=yearofinvestmentcolumn]': {
                afterrender: this.renderYearofinvestmentColumn
            },
            'gridpanel[itemId=resultgrid]': {
                selectionchange: this.showActivity
            }
        });
    },

    addAttributeFilter: function(button, event, eOpts) {
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

    renderNameofinvestorColumn: function(comp, eOpts) {
        comp.renderer = function(value, p, record) {
            // loop through all tags is needed
            var taggroupStore = record.taggroups();
            var ret = [];
            for (var i=0; i<taggroupStore.count(); i++) {
                var tagStore = taggroupStore.getAt(i).tags();
                for (var j=0; j<tagStore.count(); j++) {
                    if (tagStore.getAt(j).get('key') == Lmkp.ts.msg("activity-nameofinvestor")) {
                        ret.push(Ext.String.format('{0}', tagStore.getAt(j).get('value')));
                    }
                }
            }
            if (ret.length > 0) {
                return ret.join(', ');
            } else {
                return Lmkp.ts.msg("unknown");
            }
        }
    },

    renderYearofinvestmentColumn: function(comp, eOpts) {
        comp.renderer = function(value, p, record) {
            // loop through all tags is needed
            var taggroupStore = record.taggroups();
            for (var i=0; i<taggroupStore.count(); i++) {
                var tagStore = taggroupStore.getAt(i).tags();
                for (var j=0; j<tagStore.count(); j++) {
                    if (tagStore.getAt(j).get('key') == Lmkp.ts.msg("activity-yearofinvestment")) {
                        return Ext.String.format('{0}', tagStore.getAt(j).get('value'));
                    }
                }
            }
            return Lmkp.ts.msg("unknown");
        }
    },

    showActivity: function(model, selected, eOpts) {

        // Unselect all selected features on the map
        //var mapPanel = Ext.ComponentQuery.query('mappanel')[0];
        //var selectControl = mapPanel.getMap().getControlsBy('id', 'selectControl')[0];

        // Get the vector layer from the map panel
        /*var vectorLayer = mapPanel.getVectorLayer();

        // Unregister the featureunselected event and unselect all features
        vectorLayer.events.unregister('featureunselected', this, this.onFeatureUnselected);
        selectControl.unselectAll();
        // Register again the featureunselected event
        vectorLayer.events.register('featureunselected', this, this.onFeatureUnselected);

        // If there are selected records, highlight it on the map
        if(selectedRecord[0]){
            // Get the acitvity identifier
            var id = selectedRecord[0].data.id;

            // Get the feature by its fid
            var feature = vectorLayer.getFeatureByFid(id);

            // Unregister and register again the featureselected event
            vectorLayer.events.unregister('featureselected', this, this.onFeatureSelected);
            // Select the feature
            selectControl.select(feature);
            vectorLayer.events.register('featureselected', this, this.onFeatureSelected);
        }*/

        var detailPanel = Ext.ComponentQuery.query('lo_editortablepanel lo_editordetailpanel')[0];
        var activeTab = detailPanel.getActiveTab();
        switch (activeTab.getXType()) {
            case "activityHistoryTab":
                // var uid = (selectedRecord.length > 0) ? selectedRecord[0].raw['activity_identifier'] : null;
                // detailPanel._populateHistoryTab(selectedTab, uid)
                console.log("coming soon");
                break;
            default: 	// default is: activityDetailTab
                detailPanel.populateDetailsTab(activeTab, selected);
                break;
        }
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
        store.getProxy().url = 'activities?' + query_url;
        store.load();
        if (query_url) {
            // move paging to back to page 1 when filtering (otherwise may show empty page instead of results)
            Ext.ComponentQuery.query('pagingtoolbar[id=activityGridPagingToolbar]')[0].moveFirst();
        }
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

    addTimeFilter: function(btn, e, eOpts) {
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

    _isInArray: function(arr, obj) { // http://stackoverflow.com/questions/143847/best-way-to-find-an-item-in-a-javascript-array
        for(var i=0; i<arr.length; i++) {
            if (arr[i] == obj) return true;
        }
    },

    _formatEmptyNumberValue: function(emptyNumber) {
        /**
         * The default NULL-value for unspecified number values is 0.
         * Assumption: 0 as a number value (currently for Area and Year of Investment)
         * is not useful and should rather not be displayed.
         */
        return (emptyNumber == 0) ? '' : emptyNumber;
    }

});