Ext.define('Lmkp.view.stakeholders.StakeholderFieldContainer', {
    extend: 'Ext.form.FieldContainer',

    alias: ['widget.lo_stakeholderfieldcontainer'],

    config: {
        parentContainer: {}
    },

    layout: 'hbox',


    initComponent: function(){

        console.log(this);

        var stakeholderStore = Ext.create('Lmkp.store.StakeholderGrid');
        stakeholderStore.load();

        console.log(stakeholderStore);

        this.items = [];
         
        this.items.push({
            /*displayTpl: Ext.create('Ext.XTemplate',
                '<tpl for=".">',
                '{id}',
                '</tpl>'
                ),
            tpl: Ext.create('Ext.XTemplate',
                '<tpl for=".">',
                '<div class="x-boundlist-item">{id}</div>',
                '</tpl>'
                ),*/
            displayField: 'id',
            name: 'stakeholder.id',
            queryMode: 'local',
            margin: '0 0 0 0',
            store: stakeholderStore,
            valueField: 'id',
            xtype: 'combo'
        });
        
        this.items.push({
            displayField: 'name',
            label: 'Role',
            queryMode: 'local',
            margin: '0 0 0 0',
            name: 'stakeholder.role',
            // This store *should* probably move to a separate Python view
            store: {
                fields: ['id', 'name'],
                data : [{
                    "id": 1,
                    "name": "Donor"
                },{
                    "id": 2,
                    "name": "Implementing agency"
                },{
                    "id": 6,
                    "name": "Investor"
                }]
            },
            xtype: 'combo'
        });

        this.items.push({
            margin: '0 0 0 0',
            text: '+',
            xtype: 'button'
        });
        
        this.callParent(arguments);
    },

    getStakeholderId: function(){
        return this.down('combo[name="stakeholder.id"]').getValue();
    },

    getStakeholderRole: function(){
        return this.down('combo[name="stakeholder.role"]').getValue()
    }

});