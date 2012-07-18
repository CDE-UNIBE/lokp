Ext.define('Lmkp.view.activities.InvolvementPanel', {
    extend: 'Ext.form.Panel',
    alias: ['widget.lo_involvementpanel'],

    bodyPadding: 5,
    layout: 'anchor',
    defaults: {
        anchor: '100%',
        margin: 0
    },
    defaultType: 'displayfield',
    title: 'Involvement',

    initComponent: function() {

        console.log(this);
        console.log(this.involvement);
//        console.log(this.involvement.stakeholder());
        console.log(this.involvement.get('id'));
        console.log(this.involvement.getAssociatedData());
//        console.log(this.involvement.getStakeholder());


        if (this.involvement.raw.data) {
            // Simulate a Store to create a Model instance which allows to access
            // its TagGroups and Tags
            var x = Ext.create('Ext.data.Store', {
                model: 'Lmkp.model.Stakeholder',
                data: this.involvement.raw,
                proxy: {
                    type: 'memory',
                    reader: {
                        type: 'json'
                    }
                }
            });
            x.load();
            console.log(x);
        }



        if (this.involvement) {

            this.items = []

//            this.items = [
//                {
//                    fieldLabel: 'ID',
//                    value: this.involvement.get('id') // if involvements=full, this is empty
//                }, {
//                    fieldLabel: 'Role',
//                    value: this.involvement.get('role')
//                }
//            ]
            // For full involvements, ID is empty
            if (this.involvement.get('id')) {
                this.items.push({
                    fieldLabel: 'ID',
                    value: this.involvement.get('id')
                });
            }

            this.items.push({
                fieldLabel: 'Role',
                value: this.involvement.get('role')
            });
        }

        // Call parent first
        this.callParent(arguments);
    }
});