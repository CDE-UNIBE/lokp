var Harness = Siesta.Harness.Browser.ExtJS;

Harness.configure({
	title : 'Test Suite',
	
	preload : [
		'/static/lib/ext-4.0.7-gpl/resources/css/ext-all.css',
		'/static/lib/ext-4.0.7-gpl/ext-all-debug.js',
		'/static/lib/OpenLayers-2.11/OpenLayers.js'
	]
});

Harness.start(
	'/static/app/tests/010_sanity.t.js'
);