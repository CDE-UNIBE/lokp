Ext.require('Ext.data.JsonStore');
Ext.require('Ext.chart.Chart');
Ext.require('Ext.container.Viewport');
Ext.require('Ext.layout.container.Border');
Ext.require('Ext.chart.series.Bar');
Ext.require('Ext.chart.axis.Category');
Ext.require('Ext.chart.axis.Numeric');
Ext.require('Ext.tab.Panel');
Ext.require('Ext.form.field.ComboBox');

Ext.onReady(function () {
    var loadingMask = Ext.get('loading-mask');
    loadingMask.fadeOut({
        duration: 1000,
        remove: true
    });

    var store1 = Ext.create('Ext.data.JsonStore',{
        autoLoad: true,
        proxy: {
            type: 'ajax',
            url: '/evaluation/1',
            reader: {
                type: 'json',
                root: 'data',
                idProperty: 'Main Crop'
            }
        },
        fields: [{
            name: 'Activity (count)',
            type: 'integer'
        }, {
            name: 'Main Crop',
            type: 'string'
        }]
    });

    var chart1 = Ext.create('Ext.chart.Chart',{
        title: 'Count of Activities per Product',
        width: 600,
        height: 800,
        animate: true,
        store: store1,
        axes: [{
            type: 'Category',
            position: 'left',
            fields: ['Main Crop'],
            label: {
            //renderer: Ext.util.Format.numberRenderer('0')
            },
            title: 'Product'
        }, {
            minimum: 0,
            maximum: 50,
            grid: true,
            type: 'Numeric',
            position: 'bottom',
            fields: ['Activity (Count)'],
            title: 'Number of activities'
        }],
        series: [{
            type: 'bar',
            axis: 'left',
            highlight: true,
            tips: {
                trackMouse: true,
                width: 140,
                height: 28,
                renderer: function(storeItem, item) {
                    this.setTitle(storeItem.get('Main Crop') + ": " + storeItem.get('Activity (count)'));
                }
            },
            label: {
                display: 'insideEnd',
                field: 'Activity (Count)',
                renderer: Ext.util.Format.numberRenderer('0'),
                orientation: 'horizontal',
                color: '#333',
                'text-anchor': 'middle'
            },
            yField: 'Activity (count)',
            xField: 'Main Crop'
        }]
    });

    var store3 = Ext.create('Ext.data.JsonStore',{
        autoLoad: true,
        proxy: {
            type: 'ajax',
            url: '/evaluation/3',
            reader: {
                type: 'json',
                root: 'data',
                idProperty: 'Country'
            }
        },
        fields: [{
            name: 'Activity (count)',
            type: 'integer'
        },{
            name: 'Size of Investment (sum)',
            type: 'integer'
        },{
            name: 'Country',
            type: 'string'
        }]
    });

    var chart3 = Ext.create('Ext.chart.Chart', {
        title: 'Number of Activities and Total Size of Investments per Country',
        animate: true,
        //theme:'Category2',
        store: store3,
        axes: [{
            type: 'Numeric',
            position: 'left',
            fields: ['Size of Investment (sum)'],
            title: 'Total size of investments'
        }, {
            type: 'Numeric',
            position: 'bottom',
            fields: ['Activity (count)'],
            title: 'Number of activities',
            minimum: 0,
            maximum: 20
        }],
        series: [{
            type: 'scatter',
            markerConfig: {
                radius: 5,
                size: 5
            },
            highlight: true,
            tips: {
                trackMouse: true,
                width: 200,
                height: 60,
                renderer: function(storeItem, item) {
                    var msg = storeItem.get('Country') + ":<br/>";
                    msg += storeItem.get('Activity (count)');
                    msg += " activities with a total area of ";
                    msg += storeItem.get('Size of Investment (sum)');
                    this.setTitle(msg);
                }
            },
            axis: 'bottom',
            xField: 'Activity (count)',
            yField: 'Size of Investment (sum)'
        }]
    });

    Ext.application({
        name: 'Lmkp',
        appFolder: 'static/app',

        requires: [
        'Lmkp.view.login.Toolbar'
        ],

        controllers: [
        'login.Toolbar'
        ],

        launch: function() {
            Ext.create('Ext.container.Viewport', {
                border: false,
                layout: {
                    type: 'border',
                    padding: 0
                },
                items: [{
                    items: [
                    chart1,
                    chart3,
                    {
                        contentEl: 'heatmap-div',
                        padding: 5,
                        title: 'Heat Map',
                        xtype: 'panel'
                    }],
                    region: 'center',
                    xtype: 'tabpanel'
                },{
                    region: 'north',
                    xtype: 'lo_logintoolbar'
                },{
                    contentEl: 'header-div',
                    height: 80,
                    region: 'north',
                    xtype: 'panel'
                }]
            });
        }
    });

    
});