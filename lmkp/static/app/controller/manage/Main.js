Ext.define('Lmkp.controller.manage.Main',{
    extend: 'Ext.app.Controller',

    views: [
        'manage.MainPanel',
        'manage.activities.Details',
        'manage.activities.TreePanel'
    ],

    init: function(){
        console.log(window);
    }
    
});