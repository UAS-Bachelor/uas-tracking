var map;
var tooltipContainer;
var tooltipOverlay;
var coordinates;
var routeLine;
var styles;
var routeFeatures = [];
var pointFeatures = [];
var liveDroneSource;

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

function initMap() {
    map = new ol.Map({
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
}

function initLiveDrones() {
    liveDroneSource = new ol.source.Vector({
    });
    liveDroneSource.useSpatialIndex = false;
    let liveDroneLayer = new ol.layer.Vector({
        source: liveDroneSource,
        style: [new ol.style.Style({ //pointStyle
            image: new ol.style.Circle({
                radius: lineWidth,
                fill: new ol.style.Fill({
                    color: '#f5f5f5'
                }),
                stroke: new ol.style.Stroke({
                    color: '#2865a2',
                    width: (lineWidth / 4)
                })
            }),
            zIndex: 3
        })]
    });
    map.addLayer(liveDroneLayer);
}

function updateLiveDrones() {
    $.get(liveDronesUrl, function (listOfLiveDrones) {
        liveDroneSource.clear();
        for (let i = 0; i < listOfLiveDrones.length; i++) {
            liveDrone = listOfLiveDrones[i];
            console.log(liveDrone)
            liveDroneSource.addFeature(new ol.Feature({
                geometry: new ol.geom.Point(getCoordinates(liveDrone)), 
                name: createHtmlForDroneTooltip(liveDrone)
            }));
            var overlay = new ol.Feature({
                geometry: new ol.geom.Point(getCoordinates(liveDrone)),
                name: createHtmlForDroneTooltip(liveDrone)
            });
            overlay.setStyle(new ol.style.Style({ //pointStyle
                image: new ol.style.Circle({
                    radius: 50,
                    fill: new ol.style.Fill({
                        color: '#ff0000'
                    }),
                    stroke: new ol.style.Stroke({
                        color: '#000000',
                        width: 10
                    })
                }),
                zIndex: 2
            }))
            liveDroneSource.addFeature(overlay);
        }
        liveDroneSource.refresh();
    });
}

function displayNoFlightZones() {
    let noFlyZoneLayer = new ol.layer.Vector({
        source: new ol.source.Vector({
            url: kmlUrl,
            format: new ol.format.KML()
        })
    });
    map.addLayer(noFlyZoneLayer);
}

function initToolTip() {
    tooltipContainer = document.getElementById('tooltip');
    tooltipOverlay = new ol.Overlay({
        element: tooltipContainer,
        offset: [10, 10],
        positioning: 'top-left'
    });
    map.addOverlay(tooltipOverlay);
    map.on('pointermove', function (event) {
        if (event.dragging) {
            return;
        }
        displayTooltip(event);
    });
}

function displayTooltip(event) {
    let pixel = event.pixel;
    let feature = map.forEachFeatureAtPixel(pixel, function (feature) {
        return feature;
    }, {
            hitTolerance: 3
        });
    tooltipContainer.style.display = feature ? 'inline-block' : 'none';
    if (feature) {
        tooltipOverlay.setPosition(event.coordinate);
        tooltipContainer.innerHTML = feature.get('name');
        document.getElementById('map').style.cursor = 'pointer';
    }
    else {
        document.getElementById('map').style.cursor = '';
    }
}

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


function getCoordinates(coordinateSource) {
    return ol.proj.transform([coordinateSource['lon'], coordinateSource['lat']], 'EPSG:4326', 'EPSG:3857')
}

function createStyles() {
    styles = [
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

function createHtmlForDroneTooltip(drone) {
    let id = drone['id'];
    let lat = drone['lat'];
    let lon = drone['lon'];
    let time = drone['time_stamp'];
    return '<b>Drone</b><br>' +
        '<b>DroneID:</b> ' + id + '<br>' + 
        '<b>Latitude:</b> ' + lat + '<br>' +
        '<b>Longitude:</b> ' + lon + '<br>' +
        '<b>Tid:</b> ' + time
}


initMap();
initToolTip();
createStyles();
if (typeof kmlUrl !== 'undefined') {
    displayNoFlightZones();
}
if (typeof droneRoute !== 'undefined' && Object.keys(droneRoute[0]).length !== 0) { //historic routes
    createRoute();
    createPointsOnRoute();
    addRouteFeaturesToMap();
}
if (typeof liveDronesUrl !== 'undefined') {
    initLiveDrones();
    updateLiveDrones();
    setInterval(function () {
        updateLiveDrones();
    }, 2000);
}

