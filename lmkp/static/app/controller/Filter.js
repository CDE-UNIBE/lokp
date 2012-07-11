Ext.define('Lmkp.controller.Filter', {
    extend: 'Ext.app.Controller',
    
    stores: [
    'Config',
    'ActivityGrid'
    ],
   
    views: [
    'Filter',
    'editor.Detail',
    'activities.Details',
    'activities.History'
    ],

    init: function() {
        // get configStore and load it
        this.getConfigStore().load()
/*
        // Add an event listener to the ActivityGrid store
        this.getActivityGridStore().on('load', function(store, records, successful, operation, eOpts){

            // Get the MapPanel
            var mapPanel = Ext.ComponentQuery.query('lo_editormappanel')[0];
            // and the vector layer
            var vectorLayer = mapPanel.getVectorLayer();
            vectorLayer.removeAllFeatures();

            // Create a GeoJSON format object
            var geojsonFormat = new OpenLayers.Format.GeoJSON();
            // An array of features that is added to the vectorLayer
            var features = [];

            // Loop all records
            for(var i = 0; i < records.length; i++){
                // Parse the GeoJSON geometry
                var geom = geojsonFormat.parseGeometry(records[i].data.geometry);
                // Create a new vector object
                var vector = new OpenLayers.Feature.Vector(geom, {
                    id: records[i].data.id
                });
                // Set the activity identifier as feature id, thus it's easier
                // to find this feature again using the method getFeatureByFid
                vector.fid = records[i].data.id;

                // And add the new object to the features array
                features.push(vector)
            }

            // Finally add all features to the vectorLayer
            vectorLayer.addFeatures(features);
        }, this);
        */

        // Set the bounding box and the epsg code as an extra params to the
        // ActivityGrid store before reloading.
        /*this.getActivityGridStore().on('beforeload', function(store, operation, eOpts){
            // Get the MapPanel
            var mapPanel = Ext.ComponentQuery.query('lo_editormappanel')[0];
            // Get the map
            var map = mapPanel.getMap();
            // Caclulate the current bounds (not sure if necessary)
            map.calculateBounds();
            // Get the current extent of the map
            var extent = map.getExtent();
            // Set the bounding box and the epsg code. The bounding box must be
            // formatted like "left,bottom,right,top"
            store.getProxy().extraParams = {
                bbox: extent.toBBOX(),
                epsg: 900913
            };
        });*/


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
    
    showActivity: function() {

        // Get the selected record from the GridPanel
        var grid = Ext.ComponentQuery.query('filterPanel gridpanel[id=filterResults]')[0];
        var selectedRecord = grid.getSelectionModel().getSelection();

        // Unselect all selected features on the map
        var mapPanel = Ext.ComponentQuery.query('mappanel')[0];
        var selectControl = mapPanel.getMap().getControlsBy('id', 'selectControl')[0];

        // Get the vector layer from the map panel
        var vectorLayer = mapPanel.getVectorLayer();

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
        }
        
        var detailPanel = Ext.ComponentQuery.query('filterPanel detailPanel')[0];
        var selectedTab = detailPanel.getActiveTab();
        switch (selectedTab.getXType()) {
            case "activityHistoryTab":
                // var uid = (selectedRecord.length > 0) ? selectedRecord[0].raw['activity_identifier'] : null;
                // detailPanel._populateHistoryTab(selectedTab, uid)
                console.log("coming soon");
                break;
            default: 	// default is: activityDetailTab
                detailPanel.populateDetailsTab(selectedTab, selectedRecord);
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