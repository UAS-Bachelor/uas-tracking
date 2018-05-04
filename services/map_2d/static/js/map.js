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
var overlay;
var overlayCircleRadius = 1000;

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
        controls: ol.control.defaults({
            attributionOptions: {
              collapsible: false
            }}),
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

function printZoom(){
    console.log(map.getView().getZoom());
}


function Circle(x,y,r) {
  this.x = x;
  this.y = y;
  this.r = r;
}

function circleIntersection(c1, c2) {
    var c1R, c2R, c1X, c1Y, c2X, c2Y;

    if(c1 < c2) {
        c1R = c1.r; c2R = c2.r;
        c1X = c1.x; c2X = c2.x;
        c1Y = c1.y; c2Y = c2.y;
    } else {
        c1R = c2.r; c2R = c1.r;
        c1X = c2.x; c2X = c1.x;
        c1Y = c2.y; c2Y = c2.y;
    }
    
    if((c1R-c2R)^2  <= (c1X-c2X)^2 +(c1Y-c2Y)^2 <= (c1R + c2R)^2) {
        console.log('Circles are intersecting');
        return true;
    } 
    /*https://stackoverflow.com/questions/8367512/how-do-i-detect-intersections-between-a-circle-and-any-other-circle-in-the-same?utm_medium=organic&utm_source=google_rich_qa&utm_campaign=google_rich_q
    if(Math.abs(c1R - c2R) <= Math.sqrt((c1X - c2X)^2 + (c1Y - c2Y)^2) <= (c1R - c2R)) {
        console.log('hej')
    } */
}


      
function updateLiveDrones() {
    $.get(liveDronesUrl, function (listOfLiveDrones) {
        liveDroneSource.clear();
        for (let i = 0; i < listOfLiveDrones.length; i++) {
            liveDrone = listOfLiveDrones[i];
          //  console.log(liveDrone)
            liveDroneSource.addFeature(new ol.Feature({
                geometry: new ol.geom.Point(getCoordinates(liveDrone)), 
                name: createHtmlForDroneTooltip(liveDrone)
            }));
            overlay = new ol.Feature({
                geometry: new ol.geom.Circle(getCoordinates(liveDrone), overlayCircleRadius),               
                name: createHtmlForDroneTooltip(liveDrone),
            });
            overlay.setId(liveDrone.id);
           // console.log(overlay)
            overlay.setStyle(new ol.style.Style({ //pointStyle
                    fill: new ol.style.Fill({
                        color: 'rgba(193, 215, 245, 0.15)' // rbga for alpha (opacity), same in hex: #c1d7f5
                    }),
                    stroke: new ol.style.Stroke({
                        color: '#2b8cee',
                        width: 1
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
        c1 = new Circle(5,1,1)
        c2 = new Circle(3,1,1)
        circleIntersection(c1,c2);
        //circleCircleIntersectionPoints(Circle(liveDroneSource.getFeatureById(911).getGeometry().getCoordinates, 1000), Circle(liveDroneSource.getFeatureById(911).getGeometry().getCoordinates, 1000))
      //  console.log(liveDroneSource.getFeatureById(911).getGeometry);
     // console.log(liveDroneSource.getFeatureById(911).getGeometry().getCoordinates())
     // console.log(liveDroneSource.getFeatures())
    }, 2000);
    
}

