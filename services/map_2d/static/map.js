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
for (var i = 0; i < droneRoutes.length; i++) {
    coordinates.push([droneRoutes[i]['lon'], droneRoutes[i]['lat']])
}

//var coords = [[10.3, 55.2], [10.4, 55.5], [10.3, 55.9]];

var lineWidth = 7;
if(
    (screen.width <= 640) || 
    (window.matchMedia && 
     window.matchMedia('only screen and (max-width: 640px)').matches
    )
  ){
   lineWidth = 12;
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
            radius: (lineWidth / 2), 
            fill: new ol.style.Fill({
                color: '#f5f5f5'
            }), 
            stroke: new ol.style.Stroke({
              color: '#2865a2',
              width: (lineWidth / 3)
          })
        }), 
        zIndex: 2
      })
];

var routeFeatures = [
    new ol.Feature({
        geometry: lineString,
        name: 'Rute<br>start ' + droneRoutes[0]['time_stamp'] + '<br>slut &nbsp;' + droneRoutes[droneRoutes.length - 1]['time_stamp'] + '<br>varighed ' + routeDuration
    })
];

var pointFeatures = []

var geometry = routeFeatures[0].getGeometry()
var i = 0;
geometry.forEachSegment(function(start, end) {
    var droneRoute = droneRoutes[i];
    pointFeatures.push(new ol.Feature({
        geometry: new ol.geom.Point(start), 
        name: 'Punkt<br>lat ' + droneRoute['lat'] + '<br>lon ' + droneRoute['lon'] + '<br>tid ' + droneRoute['time_stamp']
    }))
    i++;
});

var source = new ol.source.Vector({
	features: routeFeatures.concat(pointFeatures)
});
var vector = new ol.layer.Vector({
	source: source,
	style: styles
});

map.addLayer(vector)



//Tooltip - whole class needs to be cleaned up

var tooltip = document.getElementById('tooltip');
var overlay = new ol.Overlay({
  element: tooltip,
  offset: [10, 10],
  positioning: 'top-left'
});
map.addOverlay(overlay);

function displayTooltip(evt) {
  var pixel = evt.pixel;
  var feature = map.forEachFeatureAtPixel(pixel, function(feature) {
    return feature;
  });
  tooltip.style.display = feature ? '' : 'none';
  if (feature) {
    overlay.setPosition(evt.coordinate);
    tooltip.innerHTML = feature.get('name');
  }
};

map.on('pointermove', displayTooltip);

