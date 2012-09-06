Ext.define('Lmkp.view.public.NewActivityWindow', {
    extend: 'Ext.window.Window',
    alias: ['widget.lo_newactivitywindow'],

    modal: true,
    autoScroll: true,

    layout: 'card',
    border: 0,

    initComponent: function() {

        /**
         * Parameters:
         * {aPanel}: (eg. instance of Lmkp.view.activities.NewActivity)
         * {shPanel}: (eg. instance of Lmkp.view.stakeholders.NewStakeholderSelection)
         * {activityEdit}: Boolean
         */

        if (this.aPanel && this.shPanel) {

            this.items = [
                this.aPanel,
                this.shPanel
            ];

            this.bbar = [
                {
                    xtype: 'button',
                    itemId: 'submitButton',
                    text: 'Submit',
                    disabled: !this.activityEdit
                },
                '->', {
                    id: 'card-prev',
                    text: 'Previous',
                    _dir: 'prev',
                    disabled: true
                }, {
                    id: 'card-next',
                    text: 'Next',
                    _dir: 'next'
                }
            ]
        }

        this.callParent(arguments);
    }
});