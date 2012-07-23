Ext.define('Lmkp.view.stakeholders.StakeholderFieldContainer', {
    extend: 'Ext.form.FieldContainer',

    alias: ['widget.lo_stakeholderfieldcontainer'],

    config: {
        parentContainer: {},
        stakeholder: null
    },

    layout: 'hbox',


    initComponent: function(){

        this.items = [];

        this.items.push({
            editable: false,
            flex: 1,
            name: 'stakeholder.name',
            value: this.stakeholder.getTagValues(Lmkp.ts.msg("stakeholder-name")).join(","),
            xtype: 'textfield'
        });

        /*
        this.items.push({
            allowBlank: false,
            displayField: 'name',
            emptyText: 'Select a Role',
            flex: 0.5,
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
            valueField: 'id',
            xtype: 'combo'
        });
        */
        
        this.callParent(arguments);
    },

    getStakeholderId: function(){
        return this.stakeholder.data.id;
    },

    getStakeholderVersion: function(){
        return this.stakeholder.data.version;
    },

    getStakeholderRole: function(){
        return this.down('combo[name="stakeholder.role"]').getValue()
    }

});