Ext.define('Lmkp.view.moderator.Review', {
    extend: 'Ext.panel.Panel',
    alias: ['widget.lo_moderatorreviewpanel'],
    
    bodyPadding: 5,
    layout: {
        type: 'anchor'
    },
    defaults: {
    	margin: '0 0 5 0',
    	anchor: '100%'
    },
    
    items: [{
        xtype: 'panel',
        html: 'Select an item on the left.',
        border: 0
    }]
});