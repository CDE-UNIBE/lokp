Ext.define('Lmkp.store.YamlScan', {
	extend: 'Ext.data.TreeStore',
	requires: 'Lmkp.model.YamlScan',
	model: 'Lmkp.model.YamlScan',
	
	// proxy: {
		// type: 'ajax',
		// url: '/config/scan',
		// reader: {
			// type: 'json'
		// },
		// folderSort: true
	// }
});
