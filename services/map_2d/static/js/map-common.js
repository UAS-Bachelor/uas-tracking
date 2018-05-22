var map;
var tooltipContainer;
var tooltipOverlay;
var coordinates;
var routeLine;
var styles;

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

function getCoordinates(coordinateSource) {
    return ol.proj.transform([coordinateSource['lon'], coordinateSource['lat']], 'EPSG:4326', 'EPSG:3857')
}


initMap();
initToolTip();
createStyles();