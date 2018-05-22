var liveDroneSource;

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
            liveDroneSource.addFeature(new ol.Feature({
                geometry: new ol.geom.Point(getCoordinates(liveDrone)), 
                name: createHtmlForDroneTooltip(liveDrone)
            }));
            
            var overlay = new ol.Feature({
                geometry: new ol.geom.Circle(getCoordinates(liveDrone), liveDrone['buffer_radius']),               
                name: createHtmlForDroneTooltip(liveDrone),
            });
            overlay.setStyle(new ol.style.Style({ //pointStyle
                    fill: new ol.style.Fill({
                        color: 'rgba(193, 215, 245, 0.35)' // rbga for alpha/opacity, same in hex: #c1d7f5
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


initLiveDrones();
updateLiveDrones();
setInterval(function () {
    updateLiveDrones();
}, 2000);