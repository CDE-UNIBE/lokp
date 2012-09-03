Ext.define('Lmkp.view.public.FilterStakeholderWindow', {
    extend: 'Ext.window.Window',
    alias: ['widget.lo_filterstakeholderwindow'],

    requires: ['Lmkp.view.stakeholders.Filter'],

    layout: 'fit',
    border: 0,

    // Never destroy window, only hide it
    closeAction: 'hide',
    modal: true,

    items: [
        {
            xtype: 'lo_editorstakeholderfilterpanel'
        }
    ]
});