Ext.define('Lmkp.controller.public.Filter', {
    extend: 'Ext.app.Controller',

    requires: [
        'Lmkp.view.public.FilterActivityWindow',
        'Lmkp.view.public.FilterStakeholderWindow'
    ],

    stores: [
        'ActivityConfig',
        'ActivityGrid',
        'StakeholderConfig',
        'StakeholderGrid'
    ],

    views: [
        'items.FilterPanel'
    ],

    init: function() {
        this.control({
            'lo_filteractivitywindow button[name=addAttributeFilter]': {
                click: this.onAddActivityAttributeFilterButtonClick
            },
            'lo_filteractivitywindow button[name=addTimeFilter]': {
//                TODO
            },
            'lo_filterstakeholderwindow button[name=addAttributeFilter]': {
                click: this.onAddStakeholderAttributeFilterButtonClick
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
            'lo_filteractivitywindow datefield[name=dateField]': {
                change: this.resetActivateButton
            },
            'button[name=deleteButton]': {
                click: this.deleteFilter
            },
            'combobox[name=logicalOperator]': {
                select: this.applyFilter
            }
        });
    },

    onAddStakeholderAttributeFilterButtonClick: function(button) {
        var form = button.up('lo_editorstakeholderfilterpanel');
        var store = this.getStakeholderConfigStore();

        this.addSingleFilterPanel(form, store);
    },

    onAddActivityAttributeFilterButtonClick: function(button) {
        var form = button.up('lo_editoractivityfilterpanel');
        var store = this.getActivityConfigStore();

        this.addSingleFilterPanel(form, store);
    },

    addSingleFilterPanel: function(form, store) {
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
        this.resetActivateButton(combobox);
    },

    getOperator: function(xType) {
        // prepare values of the store depending on selected xType
        switch (xType) {
            case "combobox": // possibilities: like | nlike
                var data = [
                {
                    'queryOperator': '__like',
                    'displayOperator': Lmkp.ts.msg('filter-operator_is')
                }, {
                    'queryOperator': '__nlike',
                    'displayOperator': Lmkp.ts.msg('filter-operator_is-not')
                }
                ];
                break;
            case "textfield": // possibilities: like | ilike | nlike | nilike
                var data = [
                {
                    'queryOperator': '__like',
                    'displayOperator':
                    Lmkp.ts.msg('filter-operator_contains-case-sensitive')
                }, {
                    'queryOperator': '__ilike',
                    'displayOperator':
                    Lmkp.ts.msg('filter-operator_contains-case-insensitive')
                }, {
                    'queryOperator': '__nlike',
                    'displayOperator':
                    Lmkp.ts.msg('filter-operator_contains-not-case-sensitive')
                }, {
                    'queryOperator': '__nilike',
                    'displayOperator':
                    Lmkp.ts.msg('filter-operator_contains-not-case-insensitive')
                }
                ];
                break;
            default: // default is also used for numberfield
                var data = [
                {
                    'queryOperator': '__eq',
                    'displayOperator': Lmkp.ts.msg('filter-operator_equals')
                }, {
                    'queryOperator': '__lt',
                    'displayOperator': Lmkp.ts.msg('filter-operator_less-than')
                }, {
                    'queryOperator': '__lte',
                    'displayOperator': Lmkp.ts.msg('filter-operator_less-than-or-equal')
                }, {
                    'queryOperator': '__gte',
                    'displayOperator': Lmkp.ts.msg('filter-operator_greater-than-or-equal')
                }, {
                    'queryOperator': '__gt',
                    'displayOperator': Lmkp.ts.msg('filter-operator_greater-than')
                }, {
                    'queryOperator': '__ne',
                    'displayOperator': Lmkp.ts.msg('filter-operator_not-equals')
                }
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
                editable: true,
                forceSelection: true,
                value: selectionValues[0][0],
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
     * If input is not a button, it is assumed that it is a filterpanel.
     */
    applyFilter: function(input) {

        // Get filter panels
        var afpq = Ext.ComponentQuery.query('lo_editoractivityfilterpanel');
        var activityFilterPanel = afpq.length > 0 ? afpq[0]: null;
        var sfpq = Ext.ComponentQuery.query('lo_editorstakeholderfilterpanel');
        var stakeholderFilterPanel = sfpq.length > 0 ? sfpq[0] : null;

        // Get stores
        var store = this.getActivityGridStore();
        var otherstore = this.getStakeholderGridStore();

        // Reset proxy
        store.setInitialProxy();

        // Get existing extraParams
        var extraParams = store.getProxy().extraParams;

        // Collect filters on Activities
        if (activityFilterPanel) {
            extraParams = this._appendFilterParams(
                extraParams,
                activityFilterPanel.getFilterItems(),
                'activity'
            );
            if (activityFilterPanel.getFilterItems().length > 1) {
                // Apply logical operator if selected
                extraParams["logical_op"] =
                    activityFilterPanel.getLogicalOperator();
            }
        }

        // Also collect filters on Stakeholders
        if (stakeholderFilterPanel) {
            extraParams = this._appendFilterParams(
                extraParams,
                stakeholderFilterPanel.getFilterItems(),
                'stakeholder');
            if (stakeholderFilterPanel.getFilterItems().length > 1) {
                // Apply logical operator if selected
                extraParams["logical_op"] =
                    stakeholderFilterPanel.getLogicalOperator();
            }
        }

        // Reload store
        store.getProxy().extraParams = extraParams;
        store.loadPage(1, {
            callback: function() {
                // Also reload other store
                otherstore.syncWithOther(store.getProxy().extraParams);
            }
        });
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

    _appendFilterParams: function(params, filters, type) {
        var prefix = null;
        if (type == 'activity') prefix = 'a__';
        else if (type == 'stakeholder') prefix = 'sh__';

        if (params && filters && prefix) {
            var queryable = [];
            for (var i in filters) {
                if (filters[i] && filters[i].attr) {
                    // queryable
                    // only add attribute to queryable if not already there
                    if (!this._isInArray(queryable, filters[i].attr)) {
                        queryable.push(filters[i].attr);
                    }
                    // Parameters. Multiple must be possible (eg.
                    // a__Country__like=Abc&a__Country__like=Xyz)
                    var p = prefix + filters[i].attr + filters[i].op;
                    if (!params[p]) {
                        params[p] = filters[i].value;
                    } else {
                        // Add same multiple times: use array
                        var queries = params[p];
                        if (queries instanceof Array != true) {
                            // Create a new Array
                            queries = [queries];
                        }
                        queries.push(filters[i].value);
                        params[p] = queries;
                    }
                } else if (filters[i] && filters[i].date) {
                    params['timestamp'] = filters[i].date;
                }
            }
            if (queryable.length > 0) {
                params[prefix + 'queryable'] = queryable.join(',');
            }
        }
        return params;
    },

    _isInArray: function(arr, obj) { // http://stackoverflow.com/questions/143847/best-way-to-find-an-item-in-a-javascript-array
        for(var i=0; i<arr.length; i++) {
            if (arr[i] == obj) return true;
        }
    }
});