Ext.define('Lmkp.controller.editor.Overview', {
    extend: 'Ext.app.Controller',

    refs: [{
        ref: 'mapPanel',
        selector: 'lo_editormappanel'
    }, {
        ref: 'detailPanel',
        selector: 'lo_editordetailpanel'
    },{
        ref: 'newActivityPanel',
        selector: 'lo_newactivitypanel'
    },{
        ref: 'selectStakeholderFieldSet',
        selector: 'lo_newactivitypanel fieldset[itemId="selectStakeholderFieldSet"]'
    }],

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
    'Profiles'
    ],

    views: [
    'editor.Detail',
    'editor.Map',
    'activities.Details',
    'activities.History',
    'activities.Filter',
    'stakeholders.StakeholderSelection'
    ],

    init: function() {
        // Get the ActivityConfig store and load it
        this.getActivityConfigStore().load();

        this.control({
            'lo_editortablepanel': {
                render: this.onTablePanelRender
            },
            'lo_editormappanel': {
                render: this.onMapPanelRender
            },
            'lo_activitydetailtab': {
                render: this.onActivityDetailTabRender
            },
            // Events concerning the NewActivity panel
            'lo_newactivitypanel': {
                render: this.onNewActivityPanelRender
            },
            'lo_newactivitypanel button[itemId="submitButton"]': {
                click: this.onSubmitButtonClick
            },
            // Events concerning the ActivityTable panel
            'lo_editoractivitytablepanel': {
                render: this.onActivityTablePanelRender
            },
            'lo_editorstakeholdertablepanel': {
                render: this.onStakeholderTablePanelRender
            },
            'lo_editoractivitytablepanel checkbox[itemId="spatialFilterCheckbox"]': {
                change: this.onSpatialFilterCheckboxChange
            },
            'lo_editoractivitytablepanel button[name=addAttributeFilter]': {
                click: this.addAttributeFilter
            },
            'lo_editoractivitytablepanel button[name=addTimeFilter]': {
                click: this.addTimeFilter
            },
            'lo_editoractivitytablepanel tabpanel[id=detailPanel]': {
                tabchange: this.showDetails
            },
            'lo_editoractivitytablepanel button[id=deleteAllFilters]': {
                click: this.deleteAllFilters
            },
            'lo_editoractivitytablepanel button[name=activateAttributeButton]': {
                click: this.applyFilter
            },
            'lo_editoractivitytablepanel button[name=activateTimeButton]': {
                click: this.applyFilter
            },
            'lo_editoractivitytablepanel combobox[name=attributeCombo]': {
                select: this.showValueFields
            },
            'lo_editoractivitytablepanel [name=valueField]': {
                change: this.resetActivateButton
            },
            'lo_editoractivitytablepanel combobox[name=filterOperator]': {
                select: this.resetActivateButton
            },
            'lo_editoractivitytablepanel datefield[name=dateField]': {
                change: this.resetActivateButton
            },
            'lo_editoractivitytablepanel button[name=deleteButton]': {
                click: this.deleteFilter
            },
            'lo_editoractivitytablepanel combobox[name=logicalOperator]': {
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

    addAttributeFilter: function(button, event, eOpts) {

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
        var cbox = Ext.create('Ext.form.field.ComboBox', {
            name: 'attributeCombo',
            store: this.getActivityConfigStore(),
            valueField: 'name',
            displayField: 'fieldLabel',
            queryMode: 'local',
            typeAhead: true,
            forceSelection: true,
            value: this.getActivityConfigStore().getAt('0'),
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

        this.showValueFields(cbox, [this.getActivityConfigStore().getAt('0')]);
    },

    addTimeFilter: function(button, e, eOpts) {
        var form = Ext.ComponentQuery.query('panel[id=activityFilterForm]')[0];
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

    /**
     * Shows the selected model in the details panel
     */
    showDetails: function(model, selected, eOpts) {

        var detailPanel = this.getDetailPanel();
        var d = detailPanel.down('lo_activitydetailtab');
        detailPanel.setActiveTab(d);
        detailPanel.populateDetailsTab(d, selected);

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

    deleteFilter: function(button, e, eOpts) {
        var attributePanel = button.up('panel');
        var form = Ext.ComponentQuery.query('panel[id=activityFilterForm]')[0];
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
            form = Ext.ComponentQuery.query('panel[id=activityFilterForm]')[0];
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

    onMapPanelRender: function(comp, eOpts){
        // Register the getfeatureinfo event to the identify control
        var identifyCtrl = comp.getIdentifyCtrl();
        identifyCtrl.events.register('getfeatureinfo', this, this.onGetFeatureInfo);
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

    onActivityDetailTabRender: function(comp, eOpts){
        var mappanel = this.getMapPanel();

        var tbar = comp.getDockedItems('toolbar[dock="top"]')[0];

        var movePointCtrl = new OpenLayers.Control.ModifyFeature(mappanel.getVectorLayer(), {
            mode: OpenLayers.Control.ModifyFeature.DRAG
        });

        var moveAction = Ext.create('GeoExt.Action', {
            control: movePointCtrl,
            iconCls: 'move-button',
            map: mappanel.getMap(),
            scale: 'medium',
            text: 'Edit location',
            toggleGroup: 'map-controls',
            toggleHandler: function(button, state){
                state ? movePointCtrl.activate() : movePointCtrl.deactivate();
            }
        });
        var moveButton = Ext.create('Ext.button.Button', moveAction);

        tbar.add(moveButton);
    },

    onNewActivityPanelRender: function(comp, eOpts){

        // Get the map from the map panel
        var map = this.getMapPanel().getMap();

        // Get the toolbar
        var tbar = comp.down('form').getDockedItems('toolbar[dock="top"]')[0];

        var createPointCtrl = new OpenLayers.Control.DrawFeature(
            this.getMapPanel().getVectorLayer(),
            OpenLayers.Handler.Point,{
                eventListeners: {
                    'featureadded': function(event){
                        var g = event.feature.geometry;
                        createPointCtrl.deactivate();
                        createButton.toggle(false);
                        this.setActivityGeometry(g);
                    },
                    scope: comp
                }
            });

        map.addControl(createPointCtrl);

        var createAction = Ext.create('GeoExt.Action',{
            control: createPointCtrl,
            iconCls: 'create-button',
            scale: 'medium',
            text: 'Add Location',
            toggleGroup: 'map-controls',
            toggleHandler: function(button, state){
                state ? createPointCtrl.activate() : createPointCtrl.deactivate();
            }
        });
        var createButton = Ext.create('Ext.button.Button', createAction);
        tbar.insert(0, createButton);
    },

    onSubmitButtonClick: function(button, event){
        var formpanel = button.up('form');
        var theform = formpanel.getForm();
        if (theform.isValid()) {

            // The form cannot be submitted 'normally' because ActivityProtocol expects a JSON object.
            // As a solution, the form values are used to create a JSON object which is sent using an
            // AJAX request.
            // http://www.sencha.com/forum/showthread.php?132082-jsonData-in-submit-action-of-form

            // collect values and fill them into TagGroups
            // TODO: it seems that the main tag (first added to dict) always remains in first position, but
            // maybe this should be ensured in a better way ...
            var taggroups = [];
            var stakeholders = [];

            // Get the geometry
            var geometry = null;
            var geojson = new OpenLayers.Format.GeoJSON();
            if(this.getNewActivityPanel().getActivityGeometry()){
                geometry = Ext.decode(geojson.write(this.getNewActivityPanel().getActivityGeometry()));
            }

            var comps = formpanel.query('lo_stakeholderfieldcontainer');
            for(var j = 0; j < comps.length; j++ ) {
                var fieldContainer = comps[j];
                var stakeholder = {}
                stakeholder['id'] = fieldContainer.getStakeholderId();
                //stakeholder['role'] = fieldContainer.getStakeholderRole();
                stakeholder['role'] = 6;
                stakeholder['version'] = fieldContainer.getStakeholderVersion();
                stakeholder['op'] = 'add';
                stakeholders.push(stakeholder);
            }

            for (var i in formpanel.getValues()) {
                if(i.split('.')[0] != 'stakeholder') {
                    var tags = [];
                    var main_tag = {};
                    // first, look only at mandatory fields (no '__val' or '__attr' in name)
                    if (i.indexOf("__attr") == -1 && i.indexOf("__val") == -1) {
                        var tag = {};
                        tag['key'] = i;
                        tag['value'] = formpanel.getValues()[i];
                        tag['op'] = 'add';
                        tags.push(tag);
                        // also add to main_tag
                        main_tag['key'] = i;
                        main_tag['value'] = formpanel.getValues()[i];

                        // look if further attributes to this field were entered
                        var attrs = Ext.ComponentQuery.query('[name=' + i + '__attr]');
                        var vals = Ext.ComponentQuery.query('[name=' + i + '__val]');
                        if (attrs.length > 0 && vals.length > 0 && attrs.length == vals.length) {
                            for (var j=0; j<attrs.length; j++) {
                                var tag = {};
                                tag['key'] = attrs[j].getValue();
                                tag['value'] = vals[j].getValue();
                                tag['op'] = 'add';
                                tags.push(tag);
                            }
                        }
                    }
                    if (tags.length > 0) {
                        taggroups.push({
                            'tags': tags,
                            'main_tag': main_tag
                        });
                    }
                }
            }
            var diffObject = {
                'activities': [{
                    'taggroups': taggroups,
                    'geometry': geometry,
                    'stakeholders': stakeholders
                }]
            };

            // send JSON through AJAX request
            Ext.Ajax.request({
                url: '/activities',
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json;charset=utf-8'
                },
                jsonData: diffObject,
                callback: function(options, success, response) {
                    if(success){
                        Ext.Msg.alert('Success', 'The activity was successfully created. It will be reviewed shortly.');

                        var p = this.getNewActivityPanel();
                        p.setActivityGeometry(null);
                        var formpanel = p.down('form');
                        formpanel.getForm().reset();

                        var fieldContainers = formpanel.query('lo_stakeholderfieldcontainer');
                        for(var i = 0; i < fieldContainers.length; i++){
                            this.getSelectStakeholderFieldSet().remove(fieldContainers[i]);
                        }

                        // Remove also the feature on the map
                        this.getMapPanel().getVectorLayer().removeAllFeatures();
                    } else {
                        Ext.Msg.alert('Failure', 'The activity could not be created.');
                    }

                },
                scope: this
            });
        }
    }

});