 Ext.define('Lmkp.view.stakeholders.StakeholderSelection', {
    extend: 'Ext.panel.Panel',

    alias: ['widget.lo_stakeholderselection'],

    config: {
        selectedStakeholder: null,
        confirmButton: {},
        clearButton: {}
    },

    selectedStakeholder: null,

    title: 'Search Stakeholder',

    initComponent: function(){

        this.clearButton = Ext.create('Ext.button.Button',{
            itemId: 'clearButton',
            scale: 'medium',
            text: 'Clear'
        });

        this.confirmButton = Ext.create('Ext.button.Button',{
            itemId: 'confirmButton',
            scale: 'medium',
            text: 'Select Stakeholder',
            disabled: true
        });

        var store = Ext.create('Ext.data.Store', {
            requires: ['Lmkp.model.Stakeholder',
            'Lmkp.model.TagGroup',
            'Lmkp.model.Tag',
            'Lmkp.model.MainTag',
            'Lmkp.model.Point'
            ], // all are needed to build relation

            model: 'Lmkp.model.Stakeholder',

            pageSize: 10,

            proxy: {
                extraParams: {
                    sh__queryable: Lmkp.ts.msg("stakeholder-name")
                },
                type: 'ajax',
                url: '/stakeholders',
                reader: {
                    root: 'data',
                    type: 'json',
                    totalProperty: 'total'
                },
                startParam: 'offset'
            }
        });

        this.detailTpl = Ext.create(Ext.Template, this.tplMarkup);
        
        var formpanel = Ext.create('Ext.form.Panel', {
            border: 0,
            items: [{
                displayField: 'name',
                fieldLabel: 'Search',
                flex: 1,
                border: 0,
                hideTrigger: true,
                itemId: 'searchTextfield',
                listConfig: {

                    prepareData: function(data, recordIndex, record){
 
                        var name = record.getTagValues(Lmkp.ts.msg('stakeholder-name'));
                        if(name.length == 0){
                            name = ['Unknown'];
                        }
                        
                        // temporarily set 'name' to be able to access it using
                        // displayField
                        record.set('name', name.join(', '));

                        return {
                            'id': record.id,
                            'version': record.version,
                            'name': name.join(', ')
                        }
                    }


                },
                margin: 5,
                minChar: 3,
                queryMode: 'remote',
                queryParam: 'sh__' + Lmkp.ts.msg("stakeholder-name") + '__ilike',
                remoteFilter: true,
                store: store,
                pageSize: 10,
                tpl: Ext.create('Ext.XTemplate',
                    '<tpl for=".">',
                    '<div class="x-boundlist-item">{name}</div>',
                    '</tpl>'
                    ),
                typeAhead: true,
                valueField: 'id',
                xtype: 'combo'
            }],
            layout: 'anchor',
            defaults: {
                anchor: '100%'
            }
        });

        this.items = formpanel;

        this.dockedItems = [];

        this.dockedItems.push({
            dock: 'top',
            items: [
            '->',
            this.clearButton,
            this.confirmButton
            ],
            xtype: 'toolbar'
        });

        this.callParent(arguments);
    }

});