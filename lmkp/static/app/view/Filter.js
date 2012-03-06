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
   items: [{
       // attribute selection
       xtype: 'form',
       id: 'attrForm',
       layout: {
           type: 'anchor'
       },
       border: false,
       items: [{
           xtype: 'fieldset',
           title: 'Set attribute filter',
           checkboxToggle: true,
           checkboxName: 'filterAttributeCheckbox',
           collapsed: true,
           items: [{
               xtype: 'combobox',
               id: 'filterAttribute',
               name: 'filterAttribute',
               store: 'Config',
               valueField: 'fieldLabel',
               displayField: 'name',
               queryMode: 'local',
               typeAhead: true,
               forceSelection: true,
               emptyText: 'Select attribute',
               width: 166
          }, {
              xtype: 'button',
              id: 'filterAdd',
              text: '+'
          }]
       }, {
           xtype: 'fieldset',
           title: 'Set time filter',
           checkboxToggle: true,
           checkboxName: 'filterTimeCheckbox',
           collapsed: true,
           items: [{
               xtype: 'slider',
               name: 'theslider',
               width: 166,
               minValue: 1990,
               maxValue: 2020,
               values: [1995, 2015],
               constrainThumbs: true,
               clickToChange: false
           }]
       }],
       buttons: [{
           text: 'Filter',
           id: 'filterSubmit',
           disabled: true
       }]
   }, {
       // filter results
       xtype: 'gridpanel',
       id: 'filterResults',
       store: 'ActivityGrid',
       hidden: false,
       bodyStyle: 'padding: 5px',
       margin: '10 0 0 0',
       columns: [{
       		header: 'Name',
       		dataIndex: 'name' ,
       		flex: 1,
       		sortable: true
       }],
       dockedItems: [{
       		xtype: 'pagingtoolbar',
       		store: 'ActivityGrid',
       		dock: 'bottom',
       		displayInfo: true
       }]
   }],
      
   initComponent: function() {
       console.log("initComponent view/Filter.js");
       
       this.callParent(arguments);
   }
});
