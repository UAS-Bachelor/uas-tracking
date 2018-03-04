var viewer = new Cesium.Viewer('cesiumContainer', {
    shouldAnimate : true
});

var canvas = viewer.canvas;
canvas.setAttribute('tabindex', '0'); // needed to put focus on the canvas
canvas.addEventListener('click', function() {
    canvas.focus();
});
canvas.focus();

var scene = viewer.scene;

var pathPosition = new Cesium.SampledPositionProperty();
var entityPath = viewer.entities.add({
    position : pathPosition,
    name : 'path',
    path : {
        show : true,
        leadTime : 5,
        trailTime : 5,
        width : 10,
        resolution : 1,
        material : new Cesium.PolylineGlowMaterialProperty({
            glowPower : 0.3,
            color : Cesium.Color.PALEGOLDENROD
        })
    }
});


var hpRoll = new Cesium.HeadingPitchRoll();
var hpRange = new Cesium.HeadingPitchRange();
var speed = 1;
var deltaRadians = Cesium.Math.toRadians(3.0);

var position = Cesium.Cartesian3.fromDegrees(10.432013, 55.367383, 20.0);
var speedVector = new Cesium.Cartesian3();
var fixedFrameTransform = Cesium.Transforms.localFrameToFixedFrameGenerator('north', 'west');

var planeEntity = viewer.entities.add({
    position : position, 
    //orientation : new Cesium.VelocityOrientationProperty(position),
    model : {
        uri : document.getElementById('droneModel').value
    },
})

viewer.trackedEntity = planeEntity;

document.addEventListener('keydown', function(e) {
    switch (e.keyCode) {
        case 40:
            if (e.shiftKey) {
                // speed down
                speed = Math.max(--speed, 1);
            } else {
                // pitch down
                hpRoll.pitch -= deltaRadians;
                if (hpRoll.pitch < -Cesium.Math.TWO_PI) {
                    hpRoll.pitch += Cesium.Math.TWO_PI;
                }
            }
            break;
        case 38:
            if (e.shiftKey) {
                // speed up
                speed = Math.min(++speed, 100);
            } else {
                // pitch up
                hpRoll.pitch += deltaRadians;
                if (hpRoll.pitch > Cesium.Math.TWO_PI) {
                    hpRoll.pitch -= Cesium.Math.TWO_PI;
                }
            }
            break;
        case 39:
            if (e.shiftKey) {
                // roll right
                hpRoll.roll += deltaRadians;
                if (hpRoll.roll > Cesium.Math.TWO_PI) {
                    hpRoll.roll -= Cesium.Math.TWO_PI;
                }
            } else {
                // turn right
                hpRoll.heading += deltaRadians;
                if (hpRoll.heading > Cesium.Math.TWO_PI) {
                    hpRoll.heading -= Cesium.Math.TWO_PI;
                }
            }
            break;
        case 37:
            if (e.shiftKey) {
                // roll left until
                hpRoll.roll -= deltaRadians;
                if (hpRoll.roll < 0.0) {
                    hpRoll.roll += Cesium.Math.TWO_PI;
                }
            } else {
                // turn left
                hpRoll.heading -= deltaRadians;
                if (hpRoll.heading < 0.0) {
                    hpRoll.heading += Cesium.Math.TWO_PI;
                }
            }
            break;
        default:
    }
});

var headingSpan = document.getElementById('heading');
var pitchSpan = document.getElementById('pitch');
var rollSpan = document.getElementById('roll');
var speedSpan = document.getElementById('speed');
var fromBehind = document.getElementById('fromBehind');

var height = 20.0

viewer.scene.preUpdate.addEventListener(function(scene, time) {

height += 0.005

    planeEntity.position = Cesium.Cartesian3.fromDegrees(10.432013, 55.367383, height);

    speedVector = Cesium.Cartesian3.multiplyByScalar(Cesium.Cartesian3.UNIT_Z, speed / 10, speedVector);
    //position = Cesium.Cartesian3.multiplyByScalar(planeEntity.position, speedVector, position);
    position.x += speedVector.x
    position.y += speedVector.y
    position.z += 1//speedVector.z

    //planeEntity.position = position

        //position = Cesium.Matrix4.multiplyByPoint(planeEntity.modelMatrix, speedVector, position);
    pathPosition.addSample(Cesium.JulianDate.now(), position);
    //Cesium.Transforms.headingPitchRollToFixedFrame(position, hpRoll, Cesium.Ellipsoid.WGS84, fixedFrameTransform, planeEntity.position);
    console.log(position)
    //if (fromBehind.checked) {
        // Zoom to model
        /*Cesium.Matrix4.multiplyByPoint(planePrimitive.modelMatrix, planePrimitive.boundingSphere.center, center);
        hpRange.heading = hpRoll.heading;
        hpRange.pitch = hpRoll.pitch;
        camera.lookAt(center, hpRange);*/
        //camera.lookAt(position, hpRange);

    //}
});

viewer.scene.preRender.addEventListener(function(scene, time) {
    headingSpan.innerHTML = Cesium.Math.toDegrees(hpRoll.heading).toFixed(1);
    pitchSpan.innerHTML = Cesium.Math.toDegrees(hpRoll.pitch).toFixed(1);
    rollSpan.innerHTML = Cesium.Math.toDegrees(hpRoll.roll).toFixed(1);
    speedSpan.innerHTML = speed.toFixed(1);
});
