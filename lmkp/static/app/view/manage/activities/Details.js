Ext.define('Lmkp.view.manage.activities.Details',{
    extend: 'Ext.form.Panel',

    alias: [ 'widget.manageactivitiesdetails' ],

    buttons: [{
        text: 'Submit'
    }],

    defaults: {
        anchor: '100%'
    },

    defaultType: 'textfield',

    /*items: [{
        fieldLabel: 'init',
        name: 'kdkd'
    }],

    items: [{
        fieldLabel: 'Details',
        name: 'details'

    },{
        allowBlank: false,
        fieldLabel: 'Details2',
        name: 'details2',
        //regex: /[0-9]/,
        xtype: 'numberfield'
    }],*/

    layout: 'anchor',

    initComponent: function(){
        console.log('details');
       /* this.add({
            fieldLabel: 'Details',
            name: 'details'
        });*/
        this.callParent(arguments);
    }
});