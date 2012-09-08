Ext.define('Lmkp.store.ActivityGrid', {
    extend: 'Ext.data.Store',
    
    // all are needed to build relation
    requires: [
    'Lmkp.model.Activity',
    'Lmkp.model.TagGroup',
    'Lmkp.model.Tag',
    'Lmkp.model.MainTag',
    'Lmkp.model.Point',
    'Lmkp.model.Involvement'
    ],
    
    model: 'Lmkp.model.Activity',

    pageSize: 10,
    remoteSort: true,

    proxy: {
        // Add the bounding box for the whole world as initial extra parameter
        // for the bounding box.
        // The bounding box is specified in the spherical mercator projection.
        extraParams: {
            bbox: "-20037508.34,-20037508.34,20037508.34,20037508.34",
            epsg: 900913,
            // Do not load involvements in grid for faster loading
            involvements: 'none'
        },
        type: 'ajax',
        url: '/activities',
        reader: {
            root: 'data',
            type: 'json',
            totalProperty: 'total'
        },
        startParam: 'offset',
        simpleSortMode: true,
        sortParam: 'order_by'
    },

    setInitialProxy: function() {

        // Update url
        this.proxy.url = '/activities';

        // Delete any traces of stakeholders
        delete this.proxy.extraParams['sh_id'];
        delete this.proxy.extraParams['return_sh'];

        // Set EPSG again if it is missing
        if (this.proxy.extraParams['bbox'] && !this.proxy.extraParams['epsg']) {
            this.proxy.extraParams['epsg'] = 900913;
        }
    },
    
    deleteFilters: function() {
        // Delete any filters
        var prefix_a = 'a__';
        var prefix_sh = 'sh__';
        for (var i in this.proxy.extraParams) {
            if (i.slice(0, prefix_a.length) == prefix_a
                || i.slice(0, prefix_sh.length) == prefix_sh) {
                delete this.proxy.extraParams[i];
            }
        }    },
    
    syncWithStakeholders: function(extraParams) {
    	
    	// Update url
    	this.proxy.url = '/stakeholders';
    	
    	// Update extraParams
    	if (!extraParams['return_a']) {
    		extraParams['return_a'] = true;
       	}
    	this.proxy.extraParams = extraParams;

        // (Re)load store (load at page 1, otherwise entries may be hidden)
    	this.loadPage(1);
    },

    syncWithOther: function(extraParams) {
        this.syncWithStakeholders(extraParams);
    },
    
    syncByOtherId: function(identifier) {
    	
    	// Update url
    	this.proxy.url = '/activities';
    	
    	// Update extraParams
    	this.proxy.extraParams = {
    		'sh_id': identifier
    	};
    	
    	// Reload store (load at page 1, otherwise entries may be hidden)
    	this.loadPage(1);
    }
});