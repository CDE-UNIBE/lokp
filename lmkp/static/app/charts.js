Ext.require('Ext.data.JsonStore');
Ext.require('Ext.data.reader.Json');
Ext.require('Ext.chart.Chart');
Ext.require('Ext.chart.axis.Category');
Ext.require('Ext.chart.axis.Numeric');
Ext.require('Ext.chart.series.Scatter');
Ext.require('Ext.chart.series.Bar');
Ext.require('Ext.chart.series.Line');
Ext.require('Ext.chart.series.Pie');
Ext.require('Ext.container.Viewport');
Ext.require('Ext.form.Label');
Ext.require('Ext.form.Panel');
Ext.require('Ext.form.action.StandardSubmit');
Ext.require('Ext.layout.container.Border');
Ext.require('Ext.tab.Panel');
Ext.require('Ext.form.field.ComboBox');
Ext.require('Ext.util.*');
Ext.require('Lmkp.controller.login.Toolbar');
Ext.require('Lmkp.model.SectorAreaPerYear');
Ext.require('Lmkp.view.login.Toolbar');

Ext.onReady(function () {
    var loadingMask = Ext.get('loading-mask');
    loadingMask.fadeOut({
        duration: 1000,
        remove: true
    });

    var mainTabPanel = Ext.create('Ext.tab.Panel',{
        items: [{
            autoScroll: true,
            contentEl: 'heatmap-div',
            padding: 5,
            title: 'Heat Map',
            xtype: 'panel'
        }],
        region: 'center'
    });

    var store1 = Ext.create('Ext.data.JsonStore',{
        autoLoad: true,
        proxy: {
            type: 'ajax',
            url: '/evaluation/1',
            reader: {
                type: 'json',
                root: 'data',
                idProperty: 'intention_of_investment'
            }
        },
        fields: [{
            mapping: "Activity (count)",
            name: 'activities',
            type: 'int'
        }, {
            mapping: "Intention of Investment",
            name: 'intention_of_investment',
            type: 'string'
        }]
    });
    
    // Create the chart after loading
    var chart1 = Ext.create('Ext.chart.Chart',{
        title: 'Deals per Sector',
        width: 600,
        height: 800,
        animate: true,
        store: store1,
        axes: [{
            type: 'Category',
            position: 'left',
            fields: ['intention_of_investment'],
            label: {
            //renderer: Ext.util.Format.numberRenderer('0')
            },
            title: 'Sector'
        }, {
            minimum: 0,
            //maximum: store.max('activities'),
            grid: true,
            type: 'Numeric',
            position: 'bottom',
            fields: ['activities'],
            title: 'Number of land deals'
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
                    this.setTitle(storeItem.get('intention_of_investment') + ": " + storeItem.get('activities'));
                }
            },
            label: {
                display: 'insideEnd',
                field: 'activities',
                renderer: Ext.util.Format.numberRenderer('0'),
                orientation: 'horizontal',
                color: '#333',
                'text-anchor': 'middle'
            },
            yField: 'activities',
            xField: 'intention_of_investment'
        }]
    });
    mainTabPanel.insert(chart1);

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
            name: 'Contract area (ha) (sum)',
            type: 'integer'
        },{
            name: 'Country',
            type: 'string'
        }]
    });

    var chart3 = Ext.create('Ext.chart.Chart', {
        title: 'Land deals and contracted Area per Country',
        animate: true,
        //theme:'Category2',
        store: store3,
        axes: [{
            type: 'Numeric',
            position: 'left',
            fields: ['Contract area (ha) (sum)'],
            title: 'Contracted area in hectares'
        }, {
            type: 'Numeric',
            position: 'bottom',
            fields: ['Activity (count)'],
            title: 'Number of land deals',
            minimum: 0,
            maximum: store3.max('Activity (count)')
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
                    msg += storeItem.get('Contract area (ha) (sum)');
                    msg += " hectares."
                    this.setTitle(msg);
                }
            },
            axis: 'bottom',
            xField: 'Activity (count)',
            yField: 'Contract area (ha) (sum)'
        }]
    });
    mainTabPanel.insert(chart3);

    var store4 = Ext.create('Ext.data.JsonStore',{
        autoLoad: true,
        proxy: {
            type: 'ajax',
            url: '/evaluation/4',
            reader: {
                type: 'json',
                root: 'data',
                idProperty: 'year_of_agreement'
            }
        },
        fields: [{
            mapping: "Year of agreement",
            name: 'year_of_agreement',
            type: 'int'
        }, {
            mapping: "Activity (count)",
            name: 'activity',
            type: 'int'
        }, {
            mapping: "Contract area (ha) (sum)",
            name: 'contract_area',
            type: 'float'
        }]
    });

    var chart4 = Ext.create('Ext.chart.Chart', {
        title: 'Contracts per Year',
        animate: true,
        store: store4,
        axes: [{
            type: 'Numeric',
            position: 'left',
            fields: ['activity'],
            title: 'Number of newly signed contracts'
        }, {
            type: 'Numeric',
            position: 'right',
            fields: ['contract_area'],
            title: 'Newly contracted area in ha'
        }, {
            type: 'Numeric',
            position: 'bottom',
            fields: ['year_of_agreement'],
            title: 'Year',
            minimum: 1995,
            maximum: 2011
        }],
        series: [{
            axis: 'left',
            type: 'line',
            markerConfig: {
                radius: 5,
                size: 5
            },
            highlight: true,
            smooth: true,
            tips: {
                trackMouse: true,
                width: 120,
                height: 47,
                renderer: function(storeItem, item) {
                    var msg = storeItem.get('year_of_agreement') + ":<br/>";
                    msg += storeItem.get('activity');
                    msg += " newly signed contracts";
                    this.setTitle(msg);
                }
            },
            xField: 'year_of_agreement',
            yField: 'activity'
        },{
            axis: 'right',
            type: 'line',
            markerConfig: {
                radius: 5,
                size: 5
            },
            highlight: true,
            smooth: true,
            tips: {
                trackMouse: true,
                width: 200,
                height: 47,
                renderer: function(storeItem, item) {
                    var msg = storeItem.get('year_of_agreement') + ":<br/>";
                    msg += storeItem.get('contract_area');
                    msg += " newly contracted hectares";
                    this.setTitle(msg);
                }
            },
            xField: 'year_of_agreement',
            yField: 'contract_area'
        }]
    });
    mainTabPanel.insert(chart4);


    Ext.Ajax.request({
        url: '/evaluation/5',
        scope: this,
        success: function(response){

            var responseObj = Ext.decode(response.responseText);

            // Transform the input to a suitable output store
            var inputStore = Ext.create('Ext.data.Store', {
                fields: [{
                    mapping: 'Intention of Investment',
                    name: 'intention_of_investment',
                    type: 'string'
                },{
                    mapping: 'Year of agreement',
                    name: 'year',
                    type: 'int'
                },{
                    mapping: 'Activity (count)',
                    name: 'activity',
                    type: 'int'
                },{
                    mapping: 'Contract area (ha) (sum)',
                    name: 'area',
                    type: 'float'
                }],
                data: responseObj.data,
                proxy: {
                    type: 'memory',
                    reader: {
                        type: 'json'
                    }
                }
            });

            var outputStore = Ext.create('Ext.data.Store',{
                model: 'Lmkp.model.SectorAreaPerYear'
            });

            inputStore.each(function(record){
                var y = record.get('year');

                if(y < 1990) {
                    return;
                }

                var matchedIndex = outputStore.find('year', y);

                var outputRecord;
                if(matchedIndex != -1){
                    outputRecord = outputStore.getAt(matchedIndex);
                } else {
                    outputRecord = Ext.create('Lmkp.model.SectorAreaPerYear',{
                        year: y
                    });
                    outputStore.add(outputRecord);
                }
                
                var sector = record.get('intention_of_investment');
                
                switch(sector){
                    case 'Agriculture':
                        outputRecord.set('agriculture', record.get('area'));
                        break;
                    case 'Forestry':
                        outputRecord.set('forestry', record.get('area'));
                        break;
                    case 'Mining':
                        outputRecord.set('mining', record.get('area'));
                        break;
                    case 'Other':
                        outputRecord.set('other', record.get('area'));
                        break;
                    case 'Renewable energy':
                        outputRecord.set('renewable_energy', record.get('area'));
                        break;
                    case 'Tourism':
                        outputRecord.set('tourism', record.get('area'));
                        break;
                }

            }, this);

            var store5 = Ext.create('Ext.data.JsonStore',{
                autoLoad: true,
                model: 'Lmkp.model.SectorAreaPerYear',
                data: outputStore.getRange()
            });

            var chart5 = Ext.create('Ext.chart.Chart', {
                animate: true,
                axes: [{
                    grid: true,
                    position: 'bottom',
                    fields: ['agriculture', 'forestry', 'mining', 'other', 'renewable_energy', 'tourism'],
                    title: 'Newly contracted year',
                    type: 'Numeric'
                },{
                    type: 'Category',
                    position: 'left',
                    fields: ['year'],
                    title: 'Year of Agreement',
                    minimum: 1995,
                    maximum: 2011
                }],
                legend: {
                    position: 'right'
                },
                series: [{
                    axis: 'bottom',
                    type: 'bar',
                    gutter: 80,
                    stacked: true,
                    tips: {
                        trackMouse: true,
                        width: 120,
                        height: 47,
                        renderer: function(storeItem, item) {
                            var msg = item.yField + ":<br/>";
                            msg += item.value[1] + " ha in " + item.value[0];
                            this.setTitle(msg);
                        }
                    },
                    xField: 'year',
                    yField: ['agriculture', 'forestry', 'mining', 'other', 'renewable_energy', 'tourism']
                }],
                store: store5,
                title: 'Newly contracted area in ha'
            });

            mainTabPanel.insert(chart5);
        }
    });
    
    var store6 = Ext.create('Ext.data.JsonStore',{
        autoLoad: true,
        proxy: {
            type: 'ajax',
            url: '/evaluation/6',
            reader: {
                type: 'json',
                root: 'data',
                idProperty: 'country'
            }
        },
        fields: [{
            mapping: "Country",
            name: 'country',
            type: 'string'
        }, {
            mapping: "Stakeholder (count)",
            name: 'stakeholder',
            type: 'int'
        }]
    });

    var chart6 = Ext.create('Ext.chart.Chart', {
        animate: true,
        legend: {
            position: 'right'
        },
        series: [{
            markerConfig: {
                radius: 5,
                size: 5
            },
            field: 'stakeholder',
            highlight: true,
            label: {
                field: 'country',
                display: 'rotate',
                contrast: true,
                font: '18px Arial'
            },
            showInLegend: true,
            tips: {
                trackMouse: true,
                width: 120,
                height: 47,
                renderer: function(storeItem, item) {
                    var msg = storeItem.get('stakeholder');
                    msg += " stakeholders from " + storeItem.get('country');
                    this.setTitle(msg);
                }
            },
            type: 'pie'
        }],
        shadow: true,
        store: store6,
        title: 'Stakeholders\' country of origin'
    });
    mainTabPanel.insert(chart6);

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
                items: [
                mainTabPanel,{
                    region: 'north',
                    xtype: 'lo_logintoolbar'
                },{
                    autoScroll: true,
                    contentEl: 'header-div',
                    height: 105,
                    region: 'north',
                    xtype: 'panel'
                }]
            });
        }
    });

    
});