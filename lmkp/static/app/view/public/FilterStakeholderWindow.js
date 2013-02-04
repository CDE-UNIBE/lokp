Ext.define('Lmkp.view.public.FilterStakeholderWindow', {
    extend: 'Ext.window.Window',
    alias: ['widget.lo_filterstakeholderwindow'],

    requires: ['Lmkp.view.stakeholders.Filter'],

    layout: 'fit',
    border: 0,

    // Never destroy window, only hide it
    closeAction: 'hide',
    modal: true,

    title: Lmkp.ts.msg('stakeholders_filter-title'),
    width: 570,

    items: [
        {
            xtype: 'lo_stakeholderfilterpanel'
        }
    ]
});