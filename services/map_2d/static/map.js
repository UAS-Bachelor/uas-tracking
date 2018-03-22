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
var coordinates = []
for (var i = 0; i < drone_routes.length; i++) {
    coordinates.push([drone_routes[i]['lon'], drone_routes[i]['lat']])
}

var coords = [[10.3, 55.2], [10.4, 55.5], [10.3, 55.9]];


var lineString = new ol.geom.LineString(coordinates);
lineString.transform('EPSG:4326', 'EPSG:3857');


var lineStyle = new ol.style.Style({
    stroke: new ol.style.Stroke({
        color: '#ffcc33',
        width: 10
    })
});

var source = new ol.source.Vector({
	features: [new ol.Feature({
        geometry: lineString,
        name: 'Line'
    })]
});
var vector = new ol.layer.Vector({
	source: source,
	style: [lineStyle]
});

map.addLayer(vector)


//console.log($('#my-data').data());