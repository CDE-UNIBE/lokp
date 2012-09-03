Ext.define('Lmkp.store.StakeholderGrid', {
    extend: 'Ext.data.Store',

    requires: [
        'Lmkp.model.Stakeholder',
        'Lmkp.model.TagGroup',
        'Lmkp.model.Tag',
        'Lmkp.model.MainTag',
        'Lmkp.model.Involvement'
    ],

    model: 'Lmkp.model.Stakeholder',

    pageSize: 10,
    remoteSort: true,

    proxy: {
        type: 'ajax',
        url: '/stakeholders',
        reader: {
            root: 'data',
            type: 'json',
            totalProperty: 'total'
        },
        startParam: 'offset',
        simpleSortMode: true,
        sortParam: 'order_by',
        extraParams: {
            // Do not load involvements in grid for faster loading
            involvements: 'none'
        }
    },

    setInitialProxy: function() {

        // Update url
        this.proxy.url = '/stakeholders';

        // Delete any reference to activities
        delete this.proxy.extraParams['a_id'];
        delete this.proxy.extraParams['return_a'];

        // Delete any filters
        var prefix_a = 'a__';
        var prefix_sh = 'sh__';
        for (var i in this.proxy.extraParams) {
            if (i.slice(0, prefix_a.length) == prefix_a
                || i.slice(0, prefix_sh.length) == prefix_sh) {
                delete this.proxy.extraParams[i];
            }
        }
    },
    
    syncWithActivities: function(extraParams) {

    	// Update url
    	this.proxy.url = '/activities';
    	
    	// Update extraParams
    	if (!extraParams['return_sh']) {
    		extraParams['return_sh'] = true;
       	}
    	this.proxy.extraParams = extraParams;

		// (Re)load store (load at page 1, otherwise entries may be hidden)
    	this.loadPage(1);
    },

    syncWithOther: function(extraParams) {
        this.syncWithActivities(extraParams);
    },
    
    syncByOtherId: function(identifier) {
    	
    	// Update url
    	this.proxy.url = '/stakeholders';
    	
    	// Update extraParams
    	this.proxy.extraParams = {
    		'a_id': identifier
    	};
    	
    	// Reload store (load at page 1, otherwise entries may be hidden)
    	this.loadPage(1);
    }
});