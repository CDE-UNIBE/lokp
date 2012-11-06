Ext.define('Lmkp.view.stakeholders.StakeholderFieldContainer', {
    extend: 'Ext.form.FieldContainer',

    alias: ['widget.lo_stakeholderfieldcontainer'],

    config: {
        parentContainer: {},
        involvement: null
    },

    layout: 'hbox',


    initComponent: function(){

        this.items = [];

        if(this.involvement){

            var name = this.involvement.stakeholder.getTagValues(
                Lmkp.ts.msg('stakeholder_db-key-name')
            ).join(", ");
            if (!name) {
                name = Lmkp.ts.msg('gui_unknown');
            }

            this.items.push({
                flex: 1,
                name: 'stakeholder.name',
                value: name,
                xtype: 'displayfield'
            }, {
            	xtype: 'button',
            	name: 'stakeholderRemoveButton',
            	text: '-',
            	tooltip: Lmkp.ts.msg('tooltip_remove-stakeholder')
            });
        }

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
        return this.involvement.stakeholder.get('id');
    },

    getStakeholderVersion: function(){
        return this.involvement.stakeholder.get('version');
    },

    getStakeholderRoleId: function(){
        return this.involvement.role_id;
    }

});