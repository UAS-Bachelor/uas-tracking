function displayNoFlightZones() {
    let noFlyZoneLayer = new ol.layer.Vector({
        source: new ol.source.Vector({
            url: kmlUrl,
            format: new ol.format.KML()
        })
    });
    map.addLayer(noFlyZoneLayer);
}


displayNoFlightZones();