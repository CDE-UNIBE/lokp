Ext.define('Lmkp.utils.PermalinkWindow', {
    extend: 'Ext.window.Window',

    layout: 'fit',
    border: false,

    title: Lmkp.ts.msg('Link'),

    initComponent: function() {

        var value = (this.url) ? this.url : 'No link provided';

        this.items = {
            xtype: 'textfield',
            value: value,
            size: 100,
            readOnly: true,
            selectOnFocus: true
        }

        this.callParent(arguments);
    }
});