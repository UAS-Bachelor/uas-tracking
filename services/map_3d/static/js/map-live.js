var liveDroneTimeOffset = 5;

function updateLiveDrones() {
    $.get(liveDronesUrl, function (listOfLiveDrones) {
        for (let i = 0; i < listOfLiveDrones.length; i++) {
            let liveDrone = listOfLiveDrones[i];
            //console.log(liveDrone)
            let droneEntity = viewer.entities.getById(liveDrone['id']);
            let labelEntity = viewer.entities.getById('label' + liveDrone['id']);
            if (typeof droneEntity === 'undefined') {
                createLiveDrone(liveDrone);
            }
            else {
                updateLiveDrone(droneEntity, liveDrone, labelEntity);
            }
        }
    });
}

function updateLiveDrone(droneEntity, liveDrone, labelEntity) {
    let startTime = new Date(((liveDrone['time'] + liveDroneTimeOffset) * 1000));
    let now = new Date();
    if(((now - startTime) / 1000) > liveDroneTimeOffset) {
        startTime = now;
    }
    let time = Cesium.JulianDate.fromDate(startTime);
    Cesium.JulianDate.addSeconds(time, liveDroneTimeOffset, time);

    let position = Cesium.Cartesian3.fromDegrees(liveDrone['lon'], liveDrone['lat'], liveDrone['alt']);

    //droneEntity.position.addSample(time, position);
    droneEntity.position = position;
    labelEntity.position = position;
}

function createLiveDrone(liveDrone) {
    let positionProperty = new Cesium.SampledPositionProperty();

    let startTime = new Date(((liveDrone['time'] + liveDroneTimeOffset) * 1000));
    let time = Cesium.JulianDate.fromDate(startTime);

    let position = Cesium.Cartesian3.fromDegrees(liveDrone['lon'], liveDrone['lat'], liveDrone['alt']);

    positionProperty.addSample(time, position);

    let entity = viewer.entities.add({
        id: liveDrone['id'], 
        //position: positionProperty,
        position: position,
        //orientation: new Cesium.VelocityOrientationProperty(positionProperty),
        model: {
            uri: droneModel,
            minimumPixelSize: 32
        }
    });
    viewer.entities.add({
        id: 'label' + liveDrone['id'], 
        label: {
            text: liveDrone['id'], 
            show: true,
            showBackground: true,
            font: '14px monospace',
            horizontalOrigin: Cesium.HorizontalOrigin.CENTER,
            verticalOrigin: Cesium.VerticalOrigin.BOTTOM
        }, 
        position: position
    })
    return entity;
}

function hideDropdown() {
    $('#dropdownMenu').hide();
}

hideDropdown();
updateLiveDrones();
setInterval(function () {
    updateLiveDrones();
}, 2000);