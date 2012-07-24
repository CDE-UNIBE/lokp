Ext.define('Lmkp.controller.editor.Overview', {
    extend: 'Ext.app.Controller',

    refs: [
        {
            ref: 'mapPanel',
            selector: 'lo_editormappanel'
        }, {
            ref: 'detailPanel',
            selector: 'lo_editordetailpanel'
        }
    ],

    requires: [
    'Lmkp.model.Activity',
    'Lmkp.model.TagGroup',
    'Lmkp.model.Tag',
    'Lmkp.model.MainTag',
    'Lmkp.model.Point'
    ],

    stores: [
    'ActivityGrid',
    'ActivityConfig',
    'StakeholderGrid',
    'StakeholderConfig',
    'Profiles'
    ],

    views: [
    'editor.Detail',
    'editor.Map',
    'activities.Details',
    'activities.History',
    'activities.Filter',
    'stakeholders.StakeholderSelection',
    'items.FilterPanel'
    ],

    init: function() {
        // Get the config stores and load them
        this.getActivityConfigStore().load();
        this.getStakeholderConfigStore().load();

        this.control({
            'lo_editormappanel': {
                render: this.onMapPanelRender
            },
            'lo_editoractivitytablepanel': {
                render: this.onActivityTablePanelRender
            },
            'lo_editorstakeholdertablepanel': {
                render: this.onStakeholderTablePanelRender
            },
            'lo_editoractivitytablepanel checkbox[itemId="spatialFilterCheckbox"]': {
                change: this.onSpatialFilterCheckboxChange
            },
            'button[name=addAttributeFilter]': {
                click: this.addAttributeFilter
            },
            'lo_editoractivityfilterpanel button[name=addTimeFilter]': {
                click: this.addTimeFilter
            },
            'lo_editoractivitytablepanel tabpanel[id=detailPanel]': {
                tabchange: this.showDetails
            },
            'lo_editoractivitytablepanel button[id=deleteAllFilters]': {
                click: this.deleteAllFilters
            },
            'button[name=filterActivateButton]': {
                click: this.applyFilter
            },
            'combobox[name=attributeCombo]': {
                select: this.showValueFields
            },
            '[name=valueField]': {
                change: this.resetActivateButton
            },
            'combobox[name=filterOperator]': {
                select: this.resetActivateButton
            },
            'lo_editoractivitytablepanel datefield[name=dateField]': {
                change: this.resetActivateButton
            },
            'button[name=deleteButton]': {
                click: this.deleteFilter
            },
            'combobox[name=logicalOperator]': {
                select: this.applyFilter
            },
            'gridpanel[itemId=activityGrid] gridcolumn[name=activityCountryColumn]': {
                afterrender: this.renderActivityCountryColumn
            },
            'gridpanel[itemId=activityGrid] gridcolumn[name=yearofinvestmentcolumn]': {
                afterrender: this.renderActivityYearColumn
            },
            'lo_editoractivitytablepanel gridpanel[itemId=activityGrid]': {
                selectionchange: this.showDetails
            },
            'lo_editorstakeholdertablepanel gridpanel[itemId=stakeholderGrid]': {
                selectionchange: this.showDetails
            },
            'gridpanel[itemId=stakeholderGrid] gridcolumn[name=stakeholdernamecolumn]': {
                afterrender: this.renderStakeholderNameColumn
            },
            'gridpanel[itemId=stakeholderGrid] gridcolumn[name=stakeholdercountrycolumn]': {
                afterrender: this.renderStakeholderCountryColumn
            },
            'checkbox[itemId=filterConnect]': {
                change: this.onConnectFilterChange
            }
        });
    },

    /**
     * Adds a beforeload action to the ActivityGridStore to filter the activites
     * according to the current map extent.
     */
    onActivityTablePanelRender: function(comp){

        // Adds a beforeload action
        this.getActivityGridStore().on('beforeload', function(store){

            // Get the spatialFilterCheckbox
            var checkbox = comp.getSpatialFilterCheckbox();
            // Get the store proxy
            var proxy = store.getProxy();
            // Checkbox is checked:
            if(checkbox.getValue()){
                // Get the map view.
                // Actually this is bad coding style! This should be done in a
                // superior controller ...
                var map = this.getMapPanel().getMap();
                // Get the extent if the map is already initialized, else the
                // map extent is still null
                if(map.getExtent()){
                    // Set the bounding box as extra parameter
                    proxy.setExtraParam("bbox", map.getExtent().toBBOX());
                }
            // Else checkbox is not checked:
            } else {
                // If the bounding box parameter is already set, reset it to
                // null
                if(proxy.extraParams.bbox){
                    proxy.setExtraParam("bbox", null);
                // Else cancel the reloading of the store and save a request
                } else {
                    return false;
                }
            }
        }, this)
    },

    onStakeholderTablePanelRender: function() {
        this.getStakeholderGridStore().load();
    },

    /**
     * Reload the ActivityGrid store when the spatialFilterCheckbox is checked
     * or unchecked
     */
    onSpatialFilterCheckboxChange: function(comp){
        this.getActivityGridStore().load();
    },

    addAttributeFilter: function(button) {

        // Activity or Stakeholder?
        var panel_xtype = null;
        var store = null;
        if (button.item_type == 'activity') {
            panel_xtype = 'lo_editoractivityfilterpanel';
            store = this.getActivityConfigStore();
        } else if (button.item_type == 'stakeholder') {
            panel_xtype = 'lo_editorstakeholderfilterpanel';
            store = this.getStakeholderConfigStore();
        }

        var form = button.up(panel_xtype);

        // always insert above the panel with the buttons
        var insertIndex = form.items.length - 1;
        var cbox = Ext.create('Ext.form.field.ComboBox', {
            name: 'attributeCombo',
            store: store,
            valueField: 'name',
            displayField: 'fieldLabel',
            queryMode: 'local',
            typeAhead: true,
            forceSelection: true,
            value: store.getAt('0'),
            flex: 0,
            margin: '0 5 5 0'
        });
        form.insert(insertIndex, {
            xtype: 'lo_itemsfilterpanel',
            name: 'attributePanel',
            filterField: cbox
        });
        // show initial filter
        this.showValueFields(cbox, [store.getAt('0')]);
        // toggle logical operator
        form.toggleLogicalOperator();
    },

    addTimeFilter: function(button) {

        // Activity or Stakeholder?
        var panel_xtype = null;
        if (button.item_type == 'activity') {
            panel_xtype = 'lo_editoractivityfilterpanel';
        } else if (button.item_type == 'stakeholder') {
            panel_xtype = 'lo_editorstakeholderfilterpanel';
        }

        var form = button.up(panel_xtype);

        // always insert above the panel with the buttons
        var insertIndex = form.items.length - 1;
        var picker = Ext.create('Ext.form.field.Date', {
            name: 'dateField',
            fieldLabel: Lmkp.ts.msg("date-label"),
            flex: 0,
            margin: '0 5 5 0',
            value: new Date() // defaults to today
        });
        form.insert(insertIndex, {
            xtype: 'lo_itemsfilterpanel',
            name: 'timePanel',
            filterField: picker
        });
        // disable 'add' button
        button.disable();
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

    renderActivityCountryColumn: function(comp) {
        this._renderColumnMultipleValues(comp, "activity-attr_country");
    },

    renderActivityYearColumn: function(comp) {
        this._renderColumnMultipleValues(comp, "activity-attr_yearofinvestment");
    },
    
    renderStakeholderNameColumn: function(comp) {
        this._renderColumnMultipleValues(comp, "stakeholder-attr_name");
    },
    
    renderStakeholderCountryColumn: function(comp) {
        this._renderColumnMultipleValues(comp, "stakeholder-attr_country");
    },

    showDetails: function(model, selected, eOpts) {

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

        var detailPanel = this.getDetailPanel();
        var activeTab = detailPanel.getActiveTab();
        switch (activeTab.getXType()) {
            case "lo_activityhistorypanel":
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
        var applyFilter = false;
        // try to find attribute button
        var attrButtonIndex = attributePanel.items.findIndex('name', 'filterActivateButton');
        if (attrButtonIndex != -1) {
            var btn = attributePanel.items.getAt(attrButtonIndex);
            if (btn.pressed) {
                applyFilter = true;
            }
            attributePanel.items.getAt(attrButtonIndex).toggle(false);
        }
        if (applyFilter) {
            this.applyFilter(element);
        }
    },

    /**
     * When using the checkbox to combine filters from Activities and
     * Stakeholders, look for the filterpanel to provide it to 'applyFilter()'
     */
    onConnectFilterChange: function(checkbox) {
        var gridpanel = checkbox.up('panel');
        var tablepanel = gridpanel.up('panel');
        var filterpanel = tablepanel.down('panel');
        this.applyFilter(filterpanel);
    },

    /**
     * If input is not a button, it is assumed that it is a filterpanel.
     */
    applyFilter: function(input) {

        if (input.getXType() == 'button' || input.getXType() == 'combobox') {
            // use button to find if new filter request came from Activities or
            // Stakeholders
            var itempanel = input.up('panel');
            var filterpanel = itempanel.up('panel') ? itempanel.up('panel') : null;
        } else {
            var filterpanel = input;
        }

        var store = null;
        var url = '';
        var logical_operator = null;

        if (filterpanel) {
            // Fill needed values based on Activity or Stakeholder
            var prefix = null;
            var other_xtype = null;
            var other_prefix = null;
            var url_prefix = null;
            var paging_id = null
            if (filterpanel.getXType() == 'lo_editoractivityfilterpanel') {
                // Activities
                url_prefix = 'activities?';
                prefix = 'a';
                other_xtype = 'lo_editorstakeholderfilterpanel';
                other_prefix = 'sh';
                store = this.getActivityGridStore();
                paging_id = 'activityGridPagingToolbar';
            } else if (filterpanel.getXType() == 'lo_editorstakeholderfilterpanel') {
                // Stakeholders
                url_prefix = 'stakeholders?';
                prefix = 'sh';
                other_xtype = 'lo_editoractivityfilterpanel';
                other_prefix = 'a';
                store = this.getStakeholderGridStore();
                paging_id = 'stakeholderGridPagingToolbar';
            }

            // Add filters from current panel to url
            var filters = filterpanel.getFilterItems();
            url += this._getFilterUrl(filters, prefix);
            if (filters.length > 1) {
                logical_operator = filterpanel.getLogicalOperator();
            }

            // if checkbox is set, also add filters from other panel to url
            var tablepanel = filterpanel.up('panel');
            if (tablepanel) {
                var combine_checkbox = tablepanel.query('checkbox[itemId=filterConnect]')[0];
                if (combine_checkbox && combine_checkbox.checked) {
                    var other_panel = Ext.ComponentQuery.query(other_xtype)[0];
                    if (other_panel) {
                        var other_filters = other_panel.getFilterItems();
                        url += '&' + this._getFilterUrl(other_filters, other_prefix);
                        if (other_filters.length > 1 && !logical_operator) {
                            logical_operator = other_panel.getLogicalOperator();
                        }
                    }
                }
            }

            // logical operator
            if (logical_operator) {
                url += '&logical_op=' + logical_operator;
            }
        }

        // Set new url and reload store
        url = url_prefix + url;
        store.getProxy().url = url;
        if (url == url_prefix) {
            store.load();
        }

        // move paging to back to page 1 when filtering (otherwise may show
        // empty page instead of results)
        if (url != url_prefix) {
            Ext.ComponentQuery.query('pagingtoolbar[id=' + paging_id + ']')[0].moveFirst();
        }
    },

    toggleLogicalOperator: function(filterpanel, visible) {
        var cb = filterpanel.query('combobox[name=logicalOperator]')[0];
        if (cb) {
            cb.setVisible(visible);
        }
    },

    deleteFilter: function(button) {

        var item_panel = button.up('panel');

        if (item_panel) {
            var filter_panel = item_panel.up('panel');
        }

        if (item_panel && filter_panel) {
            // if time was filtered, re-enable its 'add' button
            if (item_panel.name == 'timePanel') {
                var btn = Ext.ComponentQuery.query('button[name=addTimeFilter]')[0];
                if (btn) {
                    btn.enable();
                }
            }
            // reload store if removed filter was activated (deactivate it first)
            if (item_panel.filterIsActivated()) {
                item_panel.deactivateFilter();
                this.applyFilter(button);
            }
            filter_panel.remove(item_panel);
        }
        // toggle logical operator
        filter_panel.toggleLogicalOperator();
    },

    deleteAllFilters: function() {
        console.log("refactor me and add a button somewhere");
//        var panels = Ext.ComponentQuery.query('panel[name=attributePanel]');
//        panels = panels.concat(Ext.ComponentQuery.query('panel[name=timePanel]'));
//        if (panels.length > 0) {
//            form = Ext.ComponentQuery.query('panel[id=activityFilterForm]')[0];
//            for (i=0; i<panels.length; i++) {
//                // if time was filtered, re-enable its 'add' button
//                if (panels[i].name == 'timePanel') {
//                    var button = Ext.ComponentQuery.query('button[name=addTimeFilter]')[0];
//                    if (button) {
//                        button.enable();
//                    }
//                }
//                if (form.items.contains(panels[i])) {
//                    form.remove(panels[i], true);
//                    panels[i].destroy();
//                }
//            }
//            // collapse form if expanded
//            if (!form.collapsed) {
//                form.toggleCollapse();
//            }
//        }
//        this.applyFilter();
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
    },
    
    _renderColumnMultipleValues: function(comp, dataIndex) {
        /**
         * Helper function to find values inside Tags and TagGroups.
         */
        comp.renderer = function(value, p, record) {
            // loop through all tags is needed
            var taggroupStore = record.taggroups();
            var ret = [];
            for (var i=0; i<taggroupStore.count(); i++) {
                var tagStore = taggroupStore.getAt(i).tags();
                for (var j=0; j<tagStore.count(); j++) {
                    if (tagStore.getAt(j).get('key') == Lmkp.ts.msg(dataIndex)) {
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

    onMapPanelRender: function(comp){

        OpenLayers.ProxyHost = "/wms?url=";

        // Get the toolbar
        var tbar = comp.getDockedItems('toolbar')[0];
        // Get the map
        var map = comp.getMap();

        // Get the vector layer
        var vectorLayer = comp.getVectorLayer();

        // Register the featureselected event
        vectorLayer.events.register('featureselected', this, this.onFeatureSelected);
        vectorLayer.events.register('featureunselected', this, this.onFeatureUnselected);

        // Create the highlight and select control
        var highlightCtrl = new OpenLayers.Control.SelectFeature(vectorLayer, {
            id: 'highlightControl',
            hover: true,
            highlightOnly: true,
            renderIntent: "temporary"
        });

        var selectCtrl = new OpenLayers.Control.SelectFeature(vectorLayer, {
            id: 'selectControl',
            clickout: true
        });

        var identifyCtrl = new OpenLayers.Control.WMSGetFeatureInfo({
            eventListeners: {
                'getfeatureinfo': this.onGetFeatureInfo,
                scope: this
            },
            infoFormat: 'application/vnd.ogc.gml',
            layers: [comp.getActivitiesLayer()],
            title: 'Identify features by clicking',
            url: 'http://localhost:8080/geoserver/lo/wms'
        });

        var createPointCtrl = new OpenLayers.Control.DrawFeature(vectorLayer,
            OpenLayers.Handler.Point,{
                eventListeners: {
                    'featureadded': function(event){
                        var geometry = event.feature.geometry;
                        var win = Ext.create('Lmkp.view.activities.NewActivityWindow',{
                            activityGeometry: geometry.clone().transform(
                                new OpenLayers.Projection("EPSG:900913"), new OpenLayers.Projection("EPSG:4326"))
                        });
                        win.on('hide', function(comp, eOpts){
                            vectorLayer.removeFeatures([event.feature]);
                        }, this);
                        win.show();
                        createPointCtrl.deactivate();
                        panButton.toggle(true);
                    }
                }
            });

        var movePointCtrl = new OpenLayers.Control.ModifyFeature(vectorLayer, {
            mode: OpenLayers.Control.ModifyFeature.DRAG
        })

        // Add the controls to the map and activate them
        //map.addControl(highlightCtrl);
        //map.addControl(selectCtrl);
        map.addControl(identifyCtrl);
        map.addControl(createPointCtrl);

        //highlightCtrl.activate();
        //selectCtrl.activate();

        var panAction = Ext.create('GeoExt.Action',{
            control: new OpenLayers.Control.DragPan({
                id: 'pan'
            }),
            map: map,
            iconCls: 'pan-button',
            pressed: true,
            scale: 'medium',
            toggleGroup: 'map-controls',
            tooltip: 'Pan'
        });
        var panButton = Ext.create('Ext.button.Button', panAction);
        tbar.add(panButton);

        var zoomBoxAction = Ext.create('GeoExt.Action',{
            control: new OpenLayers.Control.ZoomBox({
                id: 'zoombox',
                type: OpenLayers.Control.TYPE_TOGGLE
            }),
            map: map,
            iconCls: 'zoom-in-button',
            scale: 'medium',
            toggleGroup: 'map-controls',
            tooltip: 'Zoom in'
        });
        tbar.add(Ext.create('Ext.button.Button', zoomBoxAction));

        tbar.add(Ext.create('Ext.button.Button', {
            handler: function(button, event, eOpts){
                this.zoomToProfile(map);
            },
            iconCls: 'zoom-region-button',
            scale: 'medium',
            scope: this,
            tooltip: 'Zoom to profile region'
        }));

        var identifyAction = Ext.create('GeoExt.Action',{
            control: identifyCtrl,
            handler: identifyAction,
            iconCls: 'identify-button',
            map: map,
            scale: 'medium',
            toggleGroup: 'map-controls',
            tooltip: "Identify feature"
        });
        tbar.add(Ext.create('Ext.button.Button', identifyAction));

        var createAction = Ext.create('GeoExt.Action',{
            control: createPointCtrl,
            iconCls: 'create-button',
            scale: 'medium',
            text: 'Add new activity',
            toggleGroup: 'map-controls',
            toggleHandler: function(button, state){
                if(state){
                    createPointCtrl.activate();
                } else {
                    createPointCtrl.deactivate();
                }
            }
        });
        tbar.add(Ext.create('Ext.button.Button', createAction));

        var moveAction = Ext.create('GeoExt.Action', {
            control: movePointCtrl,
            iconCls: 'move-button',
            map: map,
            scale: 'medium',
            text: 'Move activity',
            toggleGroup: 'map-controls',
            toggleHandler: function(button, state){
                state ? movePointCtrl.activate() : movePointCtrl.deactivate();
            }
        });
        var moveButton = Ext.create('Ext.button.Button', moveAction);
        tbar.add(moveButton);

        /*tbar.add({
            handler: function(button){
              var win = Ext.create('Lmkp.view.stakeholders.NewStakeholder');
              win.show();
            },
            scale: 'medium',
            text: 'Add Stakeholder',
            xtype: 'button'
        });*/

        /*tbar.add({
            handler: function(button){
              var win = Ext.create('Lmkp.view.stakeholders.StakeholderSelection');
              win.show();
            },
            scale: 'medium',
            text: 'Select Stakeholder',
            xtype: 'button'
        });*/

        // Get the map center and zoom level from the cookies if one is set
        var location = Ext.util.Cookies.get('_LOCATION_');
        if(location){
            var values = location.split('|');
            map.setCenter(new OpenLayers.LonLat(values[0], values[1]));
            map.zoomTo(values[2]);
        }

        // Register the moveend event with the map
        // after setting map center and zoom level
        map.events.register('moveend', this, this.onMoveEnd);
    },

    onMoveEnd: function(event){
        // Store the current map center and zoom level as cookie in the format:
        // longitude|latitude|zoom
        // and set the expiration date in three month
        var map = event.object;
        var center = map.getCenter();
        var zoom = map.getZoom();
        var value = center.lon + "|" + center.lat + "|" + zoom;

        var expirationDate = new Date();
        expirationDate.setMonth(new Date().getMonth() + 3);
        Ext.util.Cookies.set('_LOCATION_', value, expirationDate);

        // Reload the ActivityGrid store
        this.getActivityGridStore().load();
    },

    zoomToProfile: function(map) {

        var store = this.getProfilesStore();
        var activeProfile = store.getAt(store.findExact('active', true));
        if(activeProfile){
            var geoJson = new OpenLayers.Format.GeoJSON();

            var feature = geoJson.read(Ext.encode(activeProfile.get('geometry')))[0];

            var geom = feature.geometry.clone().transform(
                new OpenLayers.Projection("EPSG:4326"),
                new OpenLayers.Projection("EPSG:900913"));

            map.zoomToExtent(geom.getBounds());
        }

    },

    onGetFeatureInfo: function(event){
        var gml = new OpenLayers.Format.GML();
        // Get the first vector
        var vector = gml.read(event.text)[0];
        if(!vector){
            return;
        }
        var identifier = vector.data.activity_identifier;
        Ext.Ajax.request({
            url: '/activities/' + identifier,
            scope: this,
            success: function(response){
                var responseObj = Ext.decode(response.responseText);

                // Create a temporary memory store to properly
                // read the server response
                var store = Ext.create('Ext.data.Store', {
                    autoLoad: true,
                    model: 'Lmkp.model.Activity',
                    data : responseObj,
                    proxy: {
                        type: 'memory',
                        reader: {
                            root: 'data',
                            type: 'json',
                            totalProperty: 'total'
                        }
                    }
                });

                this.showDetails(null, [store.getAt(0)], null);
            }
        });
    },

    _getFilterUrl: function(filters, prefix) {
        if (filters && prefix) {
            // Collect values
            var queryable = [];
            var queries = [];
            for (var i in filters) {
                if (filters[i] && filters[i].attr) {
                    // attribute
                    // only add attribute to queryable if not already there
                    if (!this._isInArray(queryable, filters[i].attr)) {
                        queryable.push(filters[i].attr);
                    }
                    queries.push(prefix + '__' + filters[i].attr + filters[i].op + filters[i].value)
                } else if (filters[i] && filters[i].date) {
                    // date
                    queries.push('timestamp=' + filters[i].date);
                }
            }

            // Put together the url
            var url = '';
            if (queryable.length > 0 && queries.length > 0) {
                // queryable
                url += prefix + '__queryable=' + queryable.join(',') + '&';
                // queries
                url += queries.join('&');
            }
            return url;
        }
    }

});