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
         * {showPage}: Integer
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
                    text: Lmkp.ts.msg('button_submit'),
                    disabled: !this.activityEdit
                },
                '->', {
                    id: 'card-prev',
                    text: Lmkp.ts.msg('button_back'),
                    _dir: 'prev'
                }, {
                    id: 'card-next',
                    text: Lmkp.ts.msg('button_next'),
                    _dir: 'next'
                }
            ];
        }

        this.callParent(arguments);
    }
});