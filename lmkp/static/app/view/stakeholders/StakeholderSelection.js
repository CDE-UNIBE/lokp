 Ext.define('Lmkp.view.stakeholders.StakeholderSelection', {
    extend: 'Ext.panel.Panel',

    alias: ['widget.lo_stakeholderselection'],

    config: {
        selectedStakeholder: null,
        confirmButton: {},
        clearButton: {}
    },

    selectedStakeholder: null,

    title: Lmkp.ts.msg('stakeholders_search'),

    initComponent: function(){

        this.clearButton = Ext.create('Ext.button.Button',{
            itemId: 'clearButton',
            scale: 'medium',
            text: Lmkp.ts.msg('button_clear')
        });

        this.confirmButton = Ext.create('Ext.button.Button',{
            itemId: 'confirmButton',
            scale: 'medium',
            text: Lmkp.ts.msg('stakeholders_select-stakeholder'),
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
                    sh__queryable: Lmkp.ts.msg('stakeholder_db-key-name-original'),
                    involvements: 'full'
                },
                type: 'ajax',
                url: '/stakeholders/public/json',
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
                fieldLabel: Lmkp.ts.msg('gui_search'),
                flex: 1,
                border: 0,
                hideTrigger: true,
                itemId: 'searchTextfield',
                listConfig: {

                    prepareData: function(data, recordIndex, record){
 
                        var name = record.getTagValues(Lmkp.ts.msg('stakeholder_db-key-name'));
                        if(name.length == 0){
                            name = [Lmkp.ts.msg('gui_unknown')];
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
                queryParam: 'sh__' + Lmkp.ts.msg('stakeholder_db-key-name-original') + '__ilike',
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