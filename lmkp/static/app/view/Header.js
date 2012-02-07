Ext.define('Lmkp.view.Header' ,{
    extend: 'Ext.panel.Panel',
    alias : ['widget.header'],
    layout: 'fit',
    contentEl: 'header-div',

    initComponent: function() {
        this.callParent(arguments);
    }
});