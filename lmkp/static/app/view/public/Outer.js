Ext.define('Lmkp.view.public.Outer' ,{
    extend: 'Lmkp.view.Panel',
    alias : ['widget.lo_publicouterpanel'],

    border: false,
    layout: 'border',

    items: [{
        contentEl: 'header-div',
        height: 80,
        region: 'north',
        xtype: 'lo_panel'
    },{
        region: 'center',
        html: 'public <i>panel</i><br/>Please login to see more ...<br/>Hint: there are 3 users ;) <ul><li>user1</li><li>user2</li><li>user3</li></ul>',
        xtype: 'lo_panel'
    }],

    tbar: {
        xtype: 'lo_logintoolbar'
    }
});