Ext.define('Lmkp.view.public.FilterActivityWindow', {
    extend: 'Ext.window.Window',
    alias: ['widget.lo_filteractivitywindow'],

    requires: ['Lmkp.view.activities.Filter'],

    layout: 'fit',
    border: 0,

    // Never destroy window, only hide it
    closeAction: 'hide',
    modal: true,

    items: [
        {
            xtype: 'lo_editoractivityfilterpanel'
        }
    ]
});