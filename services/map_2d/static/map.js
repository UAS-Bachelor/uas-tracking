var map = new ol.Map({
    target: 'map',
    view: new ol.View({
        projection: 'EPSG:3857',
        center: ol.proj.transform([10.4, 55.9], 'EPSG:4326', 'EPSG:3857'),
        zoom: 7
    })
});
map.addLayer(new ol.layer.Tile({
    source: new ol.source.OSM()
}));
var coordinates = []
for (var i = 0; i < droneRoutes.length; i++) {
    coordinates.push([droneRoutes[i]['lon'], droneRoutes[i]['lat']]);
}

//var coords = [[10.3, 55.2], [10.4, 55.5], [10.3, 55.9]];

var lineWidth = 7;
var hitTolerance = 2;
if (
    (screen.width <= 640) ||
    (window.matchMedia &&
        window.matchMedia('only screen and (max-width: 640px)').matches
    )
) {
    lineWidth = 9;
    hitTolerance = 10;
}


var lineString = new ol.geom.LineString(coordinates);
lineString.transform('EPSG:4326', 'EPSG:3857');

var styles = [
    new ol.style.Style({ //lineStyle
        stroke: new ol.style.Stroke({
            color: '#00b3fd',
            width: lineWidth
        }),
        zIndex: 1
    }),
    new ol.style.Style({ //lineBorderStyle
        stroke: new ol.style.Stroke({
            color: '#2865a2',
            width: lineWidth + (lineWidth / 3)
        }),
        zIndex: 0
    }),
    new ol.style.Style({ //pointStyle
        image: new ol.style.Circle({
            radius: (lineWidth / 3),
            fill: new ol.style.Fill({
                color: '#f5f5f5'
            }),
            stroke: new ol.style.Stroke({
                color: '#2865a2',
                width: (lineWidth / 4)
            })
        }),
        zIndex: 2
    })
];

var startTime = droneRoutes[0]['time_stamp'];
var endTime = droneRoutes[droneRoutes.length - 1]['time_stamp'];
var routeFeatures = [ // can NOT handle multiple routes right now - would have to have a 2 dimensional array droneRoutes[][]
    new ol.Feature({
        geometry: lineString,
        html: '<b>Rute</b><br>' +
            '<b>Start:</b> ' + startTime + '<br>' +
            '<b>Slut:</b> ' + endTime + '<br>' +
            '<b>Varighed:</b> ' + routeDuration
    })
];

var pointFeatures = [];

for (var i = 0; i < routeFeatures.length; i++) { // can handle multiple routes
    var geometry = routeFeatures[i].getGeometry();
    var j = 0;
    geometry.forEachSegment(function (start, end) {
        pointFeatures.push(new ol.Feature({
            geometry: new ol.geom.Point(start),
            html: createHtmlForPointTooltip(droneRoutes[j])
        }));

        j++;

        if (j == droneRoutes.length - 1) { //add end point
            pointFeatures.push(new ol.Feature({
                geometry: new ol.geom.Point(end),
                html: createHtmlForPointTooltip(droneRoutes[j])
            }));
        }
    });
}

function createHtmlForPointTooltip(droneRoute) {
    var lat = droneRoute['lat'];
    var lon = droneRoute['lon'];
    var time = droneRoute['time_stamp'];
    return '<b>Punkt</b><br>' +
        '<b>Latitude:</b> ' + lat + '<br>' +
        '<b>Longitude:</b> ' + lon + '<br>' +
        '<b>Tid:</b> ' + time
}

var source = new ol.source.Vector({
    features: routeFeatures.concat(pointFeatures)
});
var vector = new ol.layer.Vector({
    source: source,
    style: styles
});

map.addLayer(vector);



//Tooltip - whole class needs to be cleaned up

var tooltip = document.getElementById('tooltip');
var overlay = new ol.Overlay({
    element: tooltip,
    offset: [10, 10],
    positioning: 'top-left'
});
map.addOverlay(overlay);

function displayTooltip(event) {
    var pixel = event.pixel;
    var feature = map.forEachFeatureAtPixel(pixel, function (feature) {
        return feature;
    }, {
            hitTolerance: 3
        });
    tooltip.style.display = feature ? '' : 'none';
    if (feature) {
        overlay.setPosition(event.coordinate);
        tooltip.innerHTML = feature.get('html');
    }
};

map.on('pointermove', function (event) {
    if (event.dragging) {
        return;
    }
    displayTooltip(event);
});

