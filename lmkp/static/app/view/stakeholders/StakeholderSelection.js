Ext.define('Lmkp.view.stakeholders.StakeholderSelection', {
    extend: 'Ext.window.Window',

    alias: ['widget.lo_stakeholderselection'],

    config: {
        selectedStakeholder: null,
        confirmButton: {},
        clearButton: {},
        southPanel: null
    },

    selectedStakeholder: null,

    modal: true,

    southPanel: null,

    layout: 'border',

    height: 600,

    width: 400,

    initComponent: function(){

        this.clearButton = Ext.create('Ext.button.Button',{
            itemId: 'clearButton',
            scale: 'medium',
            text: 'Clear'
        });

        this.confirmButton = Ext.create('Ext.button.Button',{
            itemId: 'confirmButton',
            scale: 'medium',
            text: 'Add new Stakeholder'
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

        this.items = [];
        
        var formpanel = Ext.create('Ext.form.Panel', {
            items: [{
                displayField: 'id',
                // Template for the content inside text field
                displayTpl: Ext.create('Ext.XTemplate',
                    '<tpl for=".">',
                    '{id}',
                    '</tpl>'
                    ),
                fieldLabel: 'Search',
                hideTrigger: true,
                itemId: 'searchTextfield',
                listConfig: {

                    prepareData: function(data, recordIndex, record){
 
                        var name = record.getTagValues(Lmkp.ts.msg('stakeholder-name'));
                        if(name.length == 0){
                            name = ['Unknown'];
                        }

                        return {
                            'id': record.id,
                            'version': record.version,
                            'name': name.join(',')
                        }
                    }


                },
                minChar: 3,
                queryMode: 'remote',
                queryParam: 'sh__' + Lmkp.ts.msg("stakeholder-name") + '__ilike',
                remoteFilter: true,
                store: store,
                tpl: Ext.create('Ext.XTemplate',
                    '<tpl for=".">',
                    '<div class="x-boundlist-item">{name}</div>',
                    '</tpl>'
                    ),
                typeAhead: true,
                valueField: 'id',
                xtype: 'combo'
            }],
            region: 'center'
        });

        this.items.push(formpanel);

        this.dockedItems = [];

        this.dockedItems.push({
            dock: 'bottom',
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