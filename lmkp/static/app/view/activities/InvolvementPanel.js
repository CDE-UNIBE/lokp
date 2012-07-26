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
    title: Lmkp.ts.msg('involvements-title'),

    config: {
        editable: true
    },

    initComponent: function() {

        if (this.involvement_type && this.involvement) {

            this.items = []

            // If it is not an Involvement Model, create one
            if (!this.involvement.isModel) {
                var iStore = Ext.create('Ext.data.Store', {
                    model: 'Lmkp.model.Involvement',
                    data: this.involvement,
                    proxy: {
                        type: 'memory',
                        reader: {
                            type: 'json'
                        }
                    }
                });
                iStore.load();
                this.involvement = iStore.getAt(0);
            }

            // For full involvements, ID is empty
            if (this.involvement.get('id')) {
                this.items.push({
                    fieldLabel: Lmkp.ts.msg('id'),
                    value: this.involvement.get('id')
                });
            }

            this.items.push({
                fieldLabel: Lmkp.ts.msg('involvements-role'),
                value: this.involvement.get('role')
            });

            // If 'data' in raw, show full involvement
            if (this.involvement.raw.data) {

                // Activity or Stakeholder?
                var model = null;
                var xtype = null;
                if (this.involvement_type == 'activity') {
                    model = 'Lmkp.model.Activity';
                    xtype = 'Lmkp.view.activities.ActivityPanel';
                } else if (this.involvement_type == 'stakeholder') {
                    model = 'Lmkp.model.Stakeholder';
                    xtype = 'Lmkp.view.stakeholders.StakeholderPanel';
                }

                // Simulate a Store to create a Model instance which allows to
                // access its TagGroups and Tags
                var store = Ext.create('Ext.data.Store', {
                    model: model,
                    data: this.involvement.raw.data,
                    proxy: {
                        type: 'memory',
                        reader: {
                            type: 'json'
                        }
                    }
                });
                store.load();
                var invItem = store.getAt(0);

                if (invItem) {
                    this.items.push(
                        Ext.create(xtype, {
                            contentItem: invItem,
                            border: 0,
                            editable: this.editable
                        })
                    );
                }
            }

        } else {
            this.items = {
                xtype: 'panel',
                html: Lmkp.ts.msg('unknown')
            }
        }

        // Call parent first
        this.callParent(arguments);
    }
});