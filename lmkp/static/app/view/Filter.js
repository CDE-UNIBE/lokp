Ext.define('Lmkp.view.Filter', {
   	extend: 'Ext.panel.Panel',
   	alias: ['widget.filterPanel'],
   
   	title: 'Filters',
   	layout: {
       	type: 'vbox',
       	padding: 5,
       	align: 'stretch',
   	},
   	
   	initComponent: function() {
   		this.items = [{
			// attribute selection
	       	xtype: 'panel',
	       	id: 'filterForm',
	       	flex: 0,
	       	collapsible: true,
	       	collapsed: false, // TODO: For some reason, layout is not working (buttons disappear on Adding filter) when collapsed at start.
	       	title: 'Filter',
	       	layout: {
	           	type: 'anchor'
	       	},
	       	bodyPadding: 5,
	       	items: [{
	           // items: [{
	               // xtype: 'slider',
	               // name: 'theslider',
	               // width: 166,
	               // minValue: 1990,
	               // maxValue: 2020,
	               // values: [1995, 2015],
	               // constrainThumbs: true,
	               // clickToChange: false
	           // }]
	           	xtype: 'button',
	           	name: 'addAttributeFilter',
	           	text: '[+] Add attribute filter',
	           	tooltip: 'Add a filter based on attribute',
	           	margin: '0 5 0 0'
	       	}, {
	       		xtype: 'button',
	       		name: 'addTimeFilter',
	       		text: '[+] Add time filter',
	       		tooltip: 'Add a filter based on time'
	       	}]
		}, {
			// filter results
			xtype: 'panel',
			flex: 1,
			border: false,
			layout: {
				type: 'vbox',
				align: 'stretch'
			},
			items: [{
				xtype: 'gridpanel',
		       	id: 'filterResults',
		       	store: 'ActivityGrid',
		       	viewConfig: {
		       		stripeRows: false
		       	},
		       	columns: [{
		       		header: 'Name',
		       		name: 'namecolumn',
		       		dataIndex: 'name',
		       		flex: 1,
		       		sortable: true
		       	}],
		       	dockedItems: [{
		       		xtype: 'pagingtoolbar',
		       		store: 'ActivityGrid',
		       		dock: 'bottom',
		       		enableOverflow: true,
		       		displayInfo: true,
		       		displayMsg: 'Displaying activities {0} - {1} of {2}',
		       		emptyMsg: '<b>No activities found.</b>',
		       		items: [
		       			'-', {
		       				id: 'deleteAllFilters',
		       				text: 'Delete all filters',
		       				enableToggle: false
		       			}
		       		]
		       	}],
			}, {
				xtype: 'panel',
				id: 'detailPanel',
				flex: 1,
				bodyPadding: 5,
				tpl: Ext.create('Ext.Template', [
					'Name: {name}<br/>',
					'Area: {area}<br/>',
					'Project Use: {project_use}<br/>',
					'Status: {project_status}<br/>',
					'Year of Investment: {year_of_investment}<br/>'
				]),
				html: 'Select an activity above to show its details.'
			}]
	   	}];
	   	this.callParent(arguments);
   	}
});
