Ext.define('Lmkp.view.stakeholders.NewStakeholderSelection', {
    extend: 'Ext.panel.Panel',

    alias: ['widget.lo_newstakeholderselection'],

    title: 'Add Stakeholders',

    layout: 'fit',
    defaults: {
        border: 0
    },

    initComponent: function() {

        var form = Ext.create('Ext.form.Panel', {
            autoScroll: true,
            bodyPadding: 5,
            border: 0,
            layout: 'anchor',
            defaults: {
                anchor: '100%'
            },
            tbar: [
                {
                    itemId: 'addNewStakeholderButton',
                    scale: 'medium',
                    text: 'Create new Stakeholder'
                }
            ],
            items: [
                {
                    xtype: 'fieldset',
                    title: 'Associated Stakeholders',
                    itemId: 'selectStakeholderFieldSet'
                }
            ]
        });

        this.items = form;

        this.callParent(arguments);

    },

    showForm: function() {
        var form = this.down('form');
        form.add({
            xtype: 'lo_stakeholderselection'
        });
    }
});