Ext.define('Lmkp.view.public.FilterActivityWindow', {
    extend: 'Ext.window.Window',
    alias: ['widget.lo_filteractivitywindow'],

    requires: ['Lmkp.view.activities.Filter'],

    layout: 'fit',
    modal: true,
    border: 0,

    items: [
        {
            xtype: 'lo_editoractivityfilterpanel'
        }
    ]
});