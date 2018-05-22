function initKml() {
    viewer.dataSources.add(new Cesium.KmlDataSource.load(kmlUrl)).then(function (kml) {
        let entities = kml.entities.values;
        let extrudedHeight = entities[0]._polygon._extrudedHeight;
        extrudedHeight._value = 1000;
        for (let i = 0; i < entities.length; i++) {
            if (typeof entities[i]._polygon != 'undefined') {
                entities[i]._polygon._extrudedHeight = extrudedHeight;
            }
        }
    });
}

initKml();