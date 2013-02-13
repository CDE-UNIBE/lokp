Ext.define('Lmkp.controller.translation.Main', {
    extend: 'Ext.app.Controller',

    views: [
        'translation.Main',
        'translation.OverviewTab',
        'translation.KeyValueTree'
    ],

    stores: [
        'ActivityYamlScan'
    ],

    init: function() {
        this.control({
           'lo_translationpanel lo_translationkeyvaluetree[itemId=keyvalueactivities]': {
               activate: this.onKeyValueActivitiesActivate
           }
        });
    },

    onKeyValueActivitiesActivate: function(tab) {
        console.log("bla");
//        console.log(this);
        console.log(tab);


        var x = this.getActivityYamlScanStore();
        console.log(x),
        console.log("blabla");

//        tab.setStore(x);

        x.load({
            callback: function() {
                console.log("loaded");
                console.log(x);
                console.log(x.getRootNode());
                console.log(tab);
                tab.setRootNode(x.getRootNode());
//                tab.setStore(x);
//                tab.store = x;
            }
        });

//        x.load(function() {
//
//            console.log("loaded");
//            console.log(x);
//            console.log(x.getRootNode());
//        });

        


//        x.load(function() {
//            console.log("loaded");
//            console.log(x);
//
////            tab.setStore(x);
////            tab.setRootNode(x);
//        });

//        var y = tab.getLoader();
//        console.log(y);

//        y.load();

//        x.load(function() {
//            console.log("loaded");
//            console.log(this);
//            tab.setStore(this);
//        });
//        console.log(tab);
    }
});