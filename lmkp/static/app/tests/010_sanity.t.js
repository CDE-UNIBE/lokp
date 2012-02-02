StartTest(function(t) {
	t.diag("Sanity");
	
	t.ok(Ext, 'ExtJS is here');
	t.ok(OpenLayers, 'OpenLayers is here');
	
	t.done();
})