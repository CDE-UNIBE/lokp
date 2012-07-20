Ext.define('Lmkp.view.stakeholders.StakeholderSelection', {
    extend: 'Ext.window.Window',

    alias: ['widget.lo_stakeholderselection'],

    config: {
      selectedStakeholder: {}
    },

    layout: 'border',

    height: 600,

    width: 400,

    tplMarkup: '<div><ul><li><b>{name}</b></li><li>{id}</li></ul></div>',

    initComponent: function(){

        var store = Ext.create('Lmkp.store.StakeholderGrid',{
            autoLoad: true,
            remoteFilter: true
        });

        console.log(this.items);

        this.detailTpl = Ext.create(Ext.Template, this.tplMarkup);

        this.items = [];
        
        this.items.push({
            tpl: this.detailTpl,
            itemId: 'detailpanel',
            region: 'south',
            height: 100,
            xtype: 'panel'
        });
        
        var gridpanel = Ext.create('Ext.grid.Panel', {
            columns: {
                items: [{
                    flex: 0.4,
                    text: 'Identifier',
                    dataIndex: 'id'
                },{
                    flex: 0.6,
                    itemId: 'stakeholderNameColumn',
                    text: 'Name'
                }]
            },
            region: 'center',
            store: store,
            xtype: 'gridpanel'
        });

        gridpanel.on('selectionchange', this.onRowSelect, this);

        this.items.push(gridpanel);


        this.dockedItems = [];

        this.dockedItems.push({
            dock: 'top',
            label: 'Filter by Name:',
            xtype: 'textfield'
        });

        this.dockedItems.push({
            dock: 'bottom',
            items: [{
                store: store,
                xtype: 'pagingtoolbar'
            },'->',{
                handler: function(button, event) {
                    button.up('window').hide();
                },
                scale: 'medium',
                text: 'Cancel'
            },{
                handler: function(button, event) {

                },
                scale: 'medium',
                text: 'Select'
            }],
            xtype: 'toolbar'
        });
        
        this.callParent(arguments);
    },

    onRowSelect: function(model, selected){
        this.selectedStakeholder = selected[0];

        // Find a name
        var name = Lmkp.ts.msg("unknown");
        for(var i = 0; i < this.selectedStakeholder.taggroups().getCount(); i++){

            var taggroup = this.selectedStakeholder.taggroups().getAt(i);
            for(var j = 0; j < taggroup.tags().getCount(); j++) {
                var tag = taggroup.tags().getAt(j);
                if(tag.get('key') == Lmkp.ts.msg("stakeholder-name")) {
                    name = tag.get('value');
                }
            }
        }

        var detailPanel = this.getComponent('detailpanel');
        this.detailTpl.overwrite(detailPanel.body, {
            name: name,
            id: this.selectedStakeholder.get('id')
            });
    }


});