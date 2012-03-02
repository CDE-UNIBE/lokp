Ext.define('Lmkp.controller.Filter', {
    extend: 'Ext.app.Controller',
    
    models: ['Config', 'ActivityTree'],
    stores: ['Config', 'ActivityTree'],
   
    views: [
        'Filter'
    ],
    
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
            }
        });
        var actStore = this.getActivityTreeStore()
        actStore.load();
        console.log(actStore);
    },
    
    onLaunch: function() {
    },
    
    onFilterSubmit: function(button) {
        var formValues = '';
        var filterForm = button.up('form').getForm();
        var filterAttributeCheckbox = filterForm.findField('filterAttributeCheckbox').getValue();
        var filterAttributeAttribute = filterForm.findField('filterAttribute').getValue(); 
        if (filterAttributeCheckbox && filterAttributeAttribute != null && filterForm.findField('filterValue').getValue() != null && filterForm.findField('filterValue').getValue() != '') {
            // add attribute filter to return values
            formValues += filterAttributeAttribute + "=" + filterForm.findField('filterValue').getValue() + '&';
        }
        var filterTimeCheckbox = filterForm.findField('filterTimeCheckbox').getValue();
        if (filterTimeCheckbox) {
            // add time filter to return values
            var sliderValues = filterForm.findField('theslider').getValues();
            formValues += 'startTime=' + sliderValues[0] + '&';
            formValues += 'endTime=' + sliderValues[1] + '&';
        }
        var resultPanel = Ext.ComponentQuery.query('filterPanel panel[id=filterResults]')[0];
        var filterResult;
        Ext.Ajax.request({
            url: 'db_test',
            params: formValues,
            method: "GET",
            callback: function(options, success, response) {
                console.log(response);
                filterResult = response.responseText;
            }
        });
        console.log(filterResult);
        resultPanel.update(filterResult);
        resultPanel.setVisible(true);
    },
        
    onAttributeSelect: function(combo, records) {
        // remove field first if it is already there
        var field = combo.up('form').getForm().findField('filterValue');
        if (field) {
            field.destroy();
        }
        var selectionValues = records[0].get('store');
        if (selectionValues) {      // categories of possible values available
            combo.up('fieldset').insert(1, {
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
            combo.up('fieldset').insert(1, {
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
    }
});
