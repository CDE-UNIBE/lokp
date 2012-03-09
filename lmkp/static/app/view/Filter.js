Ext.define('Lmkp.view.Filter', {
   	extend: 'Ext.panel.Panel',
   	alias: ['widget.filterPanel'],
   
   	title: 'Filters',
   	layout: {
       	type: 'vbox',
       	align: 'stretch',
       	pack: 'start'
   	},
   	bodyPadding: 5,
   	
   	
   	initComponent: function() {
   		this.items = [{
			// attribute selection
	       	xtype: 'form',
	       	id: 'filterForm',
	       	layout: {
	           	type: 'anchor'
	       	},
	       	border: false,
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
	           	tooltip: 'Add attribute filter'
	       	}, {
	       		xtype: 'button',
	       		name: 'addTimeFilter',
	       		text: '[+] Add time filter',
	       		tooltip: 'Add time filter'
	       	}]
		}, {
			// filter results
			xtype: 'panel',
			border: false,
			bodyStyle: {
				margin: '0 5px 0 0'
			},
			// layout: 'border',
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
		       				text: 'Delete filter',
		       				enableToggle: false
		       			}
		       		]
		       	}],
			}, {
				xtype: 'panel',
				id: 'detailPanel',
				tpl: Ext.create('Ext.Template', [
					'Name: {name}<br/>',
					'Area: {area}<br/>',
					'Project Use: {project_use}<br/>',
					'Status: {project_status}<br/>',
					'Year of Investment: {year_of_investment}<br/>'
				]),
				html: 'Select an activity above to show its details.',
				height: 100
			}]
	   	}];
	   	this.callParent(arguments);
   	}
});
