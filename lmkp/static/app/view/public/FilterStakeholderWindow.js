Ext.define('Lmkp.view.public.FilterStakeholderWindow', {
    extend: 'Ext.window.Window',
    alias: ['widget.lo_filterstakeholderwindow'],

    requires: ['Lmkp.view.stakeholders.Filter'],

    layout: 'fit',
    modal: true,
    border: 0,

    items: [
        {
            xtype: 'lo_editorstakeholderfilterpanel'
        }
    ]
});