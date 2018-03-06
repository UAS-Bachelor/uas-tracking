/*var viewer = new Cesium.Viewer('cesiumContainer');

var position = Cesium.Cartesian3.fromDegrees(10.432013, 55.367383, 20.0)

var heading = Cesium.Math.toRadians(135);
var pitch = 0; //side til side
var roll = 0; //frem og tilbage
var hpr = new Cesium.HeadingPitchRoll(heading, pitch, roll);
var orientation = Cesium.Transforms.headingPitchRollQuaternion(position, hpr);


var redBox = viewer.entities.add({
    name : 'Red box with black outline',
    position: position,
    orientation: orientation, 
    box : {
        dimensions : new Cesium.Cartesian3(50.0, 50.0, 40.0),
        material : Cesium.Color.RED.withAlpha(0.5),
        outline : true,
        outlineColor : Cesium.Color.BLACK
    }
});

viewer.zoomTo(viewer.entities);
*/

var keys = {};

$(document).keydown(function (e) {
    keys[e.which] = true;
    
    move();
});

$(document).keyup(function (e) {
    delete keys[e.which];
    
    move();
});

function move() {
    for (var e in keys) {
        if (!keys.hasOwnProperty(e)) continue;
        
        console.log(e)
        switch(e) {
            case '87'://w
                viewer.trackedEntity.properties.lat._value = viewer.trackedEntity.properties.lat._value + 0.000005
                break;
            case '83'://s
                viewer.trackedEntity.properties.lat._value = viewer.trackedEntity.properties.lat._value - 0.000005
                break;
            case '65'://a
                viewer.trackedEntity.properties.lon._value = viewer.trackedEntity.properties.lon._value - 0.000005
                break;
            case '68'://d
                viewer.trackedEntity.properties.lon._value = viewer.trackedEntity.properties.lon._value + 0.000005
                break;
            case '32'://space
                viewer.trackedEntity.properties.height._value = viewer.trackedEntity.properties.height._value + 0.2
                break;
            case '88'://x
                viewer.trackedEntity.properties.height._value = viewer.trackedEntity.properties.height._value - 0.2
                break;
            case '38'://op
                viewer.trackedEntity.properties.pitch._value -= 0.05
                break;
            case '40'://ned
                viewer.trackedEntity.properties.pitch._value += 0.05
                break;
            case '37'://venstre
                viewer.trackedEntity.properties.roll._value -= 0.05
                break;
            case '39'://højre
                viewer.trackedEntity.properties.roll._value += 0.05
                break;
        }
        
    }
    var newPos = Cesium.Cartesian3.fromDegrees(
            viewer.trackedEntity.properties.lon._value, 
            viewer.trackedEntity.properties.lat._value,
            viewer.trackedEntity.properties.height._value
        )
    viewer.trackedEntity.position = newPos;

    var heading = viewer.trackedEntity.properties.heading._value;
    var pitch = viewer.trackedEntity.properties.pitch._value;
    var roll = viewer.trackedEntity.properties.roll._value;
    var hpr = new Cesium.HeadingPitchRoll(heading, pitch, roll);
    var orientation = Cesium.Transforms.headingPitchRollQuaternion(position, hpr);
    viewer.trackedEntity.orientation = orientation;
}


var viewer = new Cesium.Viewer('cesiumContainer', {
    infoBox : false,
    selectionIndicator : false,
    shadows : true,
    shouldAnimate : true
});

function createModel(url) {
    viewer.entities.removeAll();

    position = Cesium.Cartesian3.fromDegrees(10.329182, 55.473886, 20.0);
    var heading = Cesium.Math.toRadians(-90);
    var pitch = 0;
    var roll = 0;
    var hpr = new Cesium.HeadingPitchRoll(heading, pitch, roll);
    var orientation = Cesium.Transforms.headingPitchRollQuaternion(position, hpr);

    var entity = viewer.entities.add({
        name : url,
        position : position,
        orientation : orientation,
        model : {
            uri : url,
            maximumScale : 20000
        }, 
        properties: {
            lon: 10.329182,
            lat: 55.473886, 
            height: 20.0, 
            heading: Cesium.Math.toRadians(-90), 
            roll: 0, 
            pitch: 0
        }
    });
    viewer.trackedEntity = entity;
}

console.log(document.getElementById('droneModel').value)

createModel(document.getElementById('droneModel').value);