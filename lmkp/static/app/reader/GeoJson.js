Ext.define('Lmkp.reader.GeoJson',{
    extend: 'Ext.data.reader.Json',

    alias: 'reader.geojson',

    read: function(response) {

        var data = response.responseText;
        console.log('Lmkp.reader.GeoJson.read(): ', data);

        return this.readRecords(data)
    },

    readRecords: function(data){

        var format = new OpenLayers.Format.GeoJSON();
        var features = format.read(data);

        var fields = new Array();
        fields.push('id');
        fields.push('geometry');

        for (var key in features[0].attributes) {
            fields.push(key);
        }

        Ext.define('Feature', {
            extend: 'Ext.data.Model',
            fields: fields
        });

        var records = new Array();

        for (var f = 0; f < features.length; f++){
            var feature = features[f];
            var record = Ext.create('Feature',{
                id: feature.id,
                geometry: feature.geometry.toString()
            });
            for (var key in feature.attributes){
                record.set(key, feature.attributes[key]);
            }

            records.push(record);
        }

        return Ext.create('Ext.data.ResultSet',{
            count: records.length,
            records: records,
            success: true,
            total: records.length
        });
    },

    constructor: function(config){
        this.initConfig(config);

        return this;
    }
});