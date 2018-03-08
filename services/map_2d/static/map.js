var map = new ol.Map({
    target: 'map', 
    view: new ol.View({
        projection: 'EPSG:3857',
        center: ol.proj.transform([10.4, 55.9],  'EPSG:4326', 'EPSG:3857'),
        zoom: 7
    })
});
map.addLayer(new ol.layer.Tile({
    source: new ol.source.OSM()
}));
//map.zoomToMaxExtent();