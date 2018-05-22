var routeFeatures = [];
var pointFeatures = [];

function createRoute() {
    coordinates = []
    for (let i = 0; i < droneRoute.length; i++) {
        coordinates.push(getCoordinates(droneRoute[i]));
    }
    routeLine = new ol.geom.LineString(coordinates);

    routeFeatures.push( // can NOT handle multiple routes right now - would have to have a 2 dimensional array droneRoute[][]
        new ol.Feature({
            geometry: routeLine,
            name: createHtmlForRouteTooltip()
        })
    );
}

function createPointsOnRoute() {
    for (let i = 0; i < routeFeatures.length; i++) { // can handle multiple routes
        let geometry = routeFeatures[i].getGeometry();
        let j = 0;
        geometry.forEachSegment(function (start, end) {
            addPointFeature(start, j);
            j++;
        });
        addPointFeature(geometry.getLastCoordinate(), j);
    }
}

function addPointFeature(coordinates, index) {
    pointFeatures.push(new ol.Feature({
        geometry: new ol.geom.Point(coordinates),
        name: createHtmlForPointTooltip(droneRoute[index])
    }));
}

function addRouteFeaturesToMap() {
    let vectorSource = new ol.source.Vector({
        features: routeFeatures.concat(pointFeatures)
    });
    let vector = new ol.layer.Vector({
        source: vectorSource,
        style: styles
    });
    map.addLayer(vector);
}

function createHtmlForPointTooltip(droneRoutePoint) {
    let lat = droneRoutePoint['lat'];
    let lon = droneRoutePoint['lon'];
    let time = droneRoutePoint['time_stamp'];
    return '<b>Punkt</b><br>' +
        '<b>Latitude:</b> ' + lat + '<br>' +
        '<b>Longitude:</b> ' + lon + '<br>' +
        '<b>Tid:</b> ' + time
}

function createHtmlForRouteTooltip() {
    let startTime = droneRoute[0]['time_stamp'];
    let endTime = droneRoute[droneRoute.length - 1]['time_stamp'];
    return '<b>Rute</b><br>' +
        '<b>Start:</b> ' + startTime + '<br>' +
        '<b>Slut:</b> ' + endTime + '<br>' +
        '<b>Varighed:</b> ' + routeDuration
}


if (Object.keys(droneRoute[0]).length !== 0) {
    createRoute();
    createPointsOnRoute();
    addRouteFeaturesToMap();
}