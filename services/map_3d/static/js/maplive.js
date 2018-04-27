var viewer;
var entity;
var start;
var stop;
var lineWidth = 7;


function initMap() {
    Cesium.BingMapsApi.defaultKey = 'AlP_7a7Bu5IKn_jRniYtal7yLOFyLfCG8X-tSLiE56287FLtKqX7nko0IQmtogg5';
    let west = 8.0;
    let south = 53.5;
    let east = 13.0;
    let north = 58.0;

    let rectangle = Cesium.Rectangle.fromDegrees(west, south, east, north);

    Cesium.Camera.DEFAULT_VIEW_FACTOR = 0;
    Cesium.Camera.DEFAULT_VIEW_RECTANGLE = rectangle;
    viewer = new Cesium.Viewer('cesiumContainer', {
        infoBox: false,
        selectionIndicator: false,
        shouldAnimate: true, 
        timeline: true, 
        //navigationHelpButton: false
    });
    //Enable depth testing so things behind the terrain disappear.
    //viewer.scene.globe.depthTestAgainstTerrain = true;
}

function initTime() {
    let routeStartTime = droneRoute[0]['time'];
    let routeEndTime = droneRoute[droneRoute.length - 1]['time'];

    start = Cesium.JulianDate.fromDate(new Date(routeStartTime * 1000)); // * 1000 to go from seconds to milliseconds, since Date takes milliseconds
    stop = Cesium.JulianDate.fromDate(new Date(routeEndTime * 1000));

    viewer.clock.startTime = start.clone();
    viewer.clock.stopTime = stop.clone();
    viewer.clock.currentTime = start.clone();
    viewer.clock.clockRange = Cesium.ClockRange.CLAMPED;
    viewer.clock.multiplier = 1;

    viewer.timeline.zoomTo(start, stop);
}

function createDrone() {
    let position = computeFlightCoordinates();
    entity = viewer.entities.add({
        availability: new Cesium.TimeIntervalCollection([new Cesium.TimeInterval({
            start: start,
            stop: stop
        })]),
        position: position,
        orientation: new Cesium.VelocityOrientationProperty(position),
        model: {
            uri: droneModel,
            minimumPixelSize: 32
        },
        path: {
            resolution: 1,
            material: new Cesium.PolylineOutlineMaterialProperty({
                color: Cesium.Color.fromCssColorString('#00b3fd'),
                outlineColor: Cesium.Color.fromCssColorString('#2865a2'),
                outlineWidth: (lineWidth / 3)
            }),
            width: lineWidth
        }
    });

    let newPoint = droneRoute[droneRoute.length - 1];
    let oldPoint = droneRoute[droneRoute.length - 2];

    var newPosition = Cesium.Cartesian3.fromDegrees(newPoint['lon'], newPoint['lat'], newPoint['alt']);
    var oldPosition = Cesium.Cartesian3.fromDegrees(oldPoint['lon'], oldPoint['lat'], oldPoint['alt']);
    
    var speedVector = new Cesium.Cartesian3();
     speedVector = Cesium.Cartesian3.subtract(newPosition, oldPosition, speedVector);

    //var positionVector = Cesium.Cartesian3.fromDegrees(droneRoutePoint['lon'], droneRoutePoint['lat'], droneRoutePoint['alt']);

    var positionVector = oldPosition.clone()


    /*viewer.scene.preUpdate.addEventListener(function(scene, time) {
        
        positionVector = Cesium.Cartesian3.add(positionVector, speedVector, positionVector);

        console.log(speedVector)

        /*position = Cesium.Matrix4.multiplyByPoint(planePrimitive.modelMatrix, speedVector, position);
        pathPosition.addSample(Cesium.JulianDate.now(), position);
        Cesium.Transforms.headingPitchRollToFixedFrame(position, hpRoll, Cesium.Ellipsoid.WGS84, fixedFrameTransform, planePrimitive.modelMatrix);
    
        if (fromBehind.checked) {
            // Zoom to model
            Cesium.Matrix4.multiplyByPoint(planePrimitive.modelMatrix, planePrimitive.boundingSphere.center, center);
            hpRange.heading = hpRoll.heading;
            hpRange.pitch = hpRoll.pitch;
            camera.lookAt(center, hpRange);
        }*/
    //});


    let droneRoutePoint = droneRoute[droneRoute.length - 1];
    
    let posi = Cesium.Cartesian3.fromDegrees(droneRoutePoint['lon'], droneRoutePoint['lat'], droneRoutePoint['alt'] + 200);

    viewer.entities.add({
        availability: new Cesium.TimeIntervalCollection([new Cesium.TimeInterval({
            start: start,
            stop: stop
        })]),
        position: posi,
        model: {
            uri: droneModel,
            minimumPixelSize: 32
        }
    });
}

function computeFlightCoordinates() {
    var positionProperty = new Cesium.SampledPositionProperty();
    for (let i = 0; i < droneRoute.length; i++) {
        let droneRoutePoint = droneRoute[i];
        let time = Cesium.JulianDate.fromDate(new Date(droneRoutePoint['time'] * 1000));
        let position = Cesium.Cartesian3.fromDegrees(droneRoutePoint['lon'], droneRoutePoint['lat'], droneRoutePoint['alt']);
        positionProperty.addSample(time, position);

        viewer.entities.add({
            position: position,
            point: {
                pixelSize: (lineWidth / 1.5),
                color: Cesium.Color.fromCssColorString('#f5f5f5'),
                outlineColor: Cesium.Color.fromCssColorString('#2865a2'),
                outlineWidth: (lineWidth / 3)
            }
        });
    }
    return positionProperty;
}


function initDropdown() {
    $('#dropdownMenu').html("Viewing drone");
    $('#viewDrone').click(clickViewDrone);
    $('#viewSide').click(clickViewSide);
    $('#viewTopDown').click(clickViewTopDown);
}


var liveDrones = {}

function updateLiveDrones() {
    $.get(liveDronesUrl, function (listOfLiveDrones) {
        for (let i = 0; i < listOfLiveDrones.length; i++) {
            let liveDrone = listOfLiveDrones[i];
            //console.log(liveDrone)
            let droneEntity = viewer.entities.getById(liveDrone['id']);
            if (typeof droneEntity === 'undefined') {
                console.log('adding drone to drawing')
                createDrone(liveDrone);
            }
            else {
                updateDrone(droneEntity, liveDrone);
            }
        }
    });
}

function updateDrone(droneEntity, liveDrone) {
    let time = Cesium.JulianDate.fromDate(new Date(((liveDrone['time'] + 15) * 1000)));
    let position = Cesium.Cartesian3.fromDegrees(liveDrone['lon'], liveDrone['lat'], liveDrone['alt']);

    droneEntity.position.addSample(time, position);
}

function createDrone(liveDrone) {
    let positionProperty = new Cesium.SampledPositionProperty();
    let time = Cesium.JulianDate.fromDate(new Date(((liveDrone['time'] + 5) * 1000)));
    console.log(new Date(((liveDrone['time'] + 150) * 1000)));
    let position = Cesium.Cartesian3.fromDegrees(liveDrone['lon'], liveDrone['lat'], liveDrone['alt']);

    positionProperty.addSample(time, position);

    let entity = viewer.entities.add({
        id: liveDrone['id'], 
        position: positionProperty,
        orientation: new Cesium.VelocityOrientationProperty(positionProperty),
        model: {
            uri: droneModel,
            minimumPixelSize: 32
        }
    });
    return entity;
}


function clickViewDrone() {
    viewDrone();
    $('#dropdownMenu').html("Viewing drone");
    $('#viewSide').removeClass('active');
    $('#viewTopDown').removeClass('active');
    $('#viewDrone').addClass('active');

    let routeEndTime = droneRoute[droneRoute.length - 1]['time'];



    var newStop = Cesium.JulianDate.fromDate(new Date((routeEndTime + 15) * 1000));
    viewer.clock.stopTime = newStop.clone();

    viewer.timeline.zoomTo(start, newStop);
    

    entity.availability = new Cesium.TimeIntervalCollection([new Cesium.TimeInterval({
        start: entity.availability.start,
        stop: newStop
    })]);
    

    let droneRoutePoint = droneRoute[droneRoute.length - 1];

    let time = Cesium.JulianDate.fromDate(new Date((droneRoutePoint['time'] + 15) * 1000));
    let position = Cesium.Cartesian3.fromDegrees(droneRoutePoint['lon'], droneRoutePoint['lat'], droneRoutePoint['alt'] + 200);

    entity.position.addSample(time, position);
}

function clickViewSide() {
    viewSide();
    $('#dropdownMenu').html("Viewing side");
    $('#viewDrone').removeClass('active');
    $('#viewTopDown').removeClass('active');
    $('#viewSide').addClass('active');
}

function clickViewTopDown() {
    viewTopDown();
    $('#dropdownMenu').html("Viewing top down");
    $('#viewDrone').removeClass('active');
    $('#viewSide').removeClass('active');
    $('#viewTopDown').addClass('active');
}

function viewTopDown() {
    viewer.trackedEntity = undefined;
    viewer.zoomTo(viewer.entities);//, new Cesium.HeadingPitchRange(0, Cesium.Math.toRadians(-90)));
}

function viewSide() {
    viewer.trackedEntity = undefined;
    viewer.zoomTo(viewer.entities, new Cesium.HeadingPitchRange(Cesium.Math.toRadians(-90), Cesium.Math.toRadians(-15), 7500));
}

function viewDrone() {
    viewer.trackedEntity = entity;
}



function hermitePolynomialInterpolation() {
    entity.position.setInterpolationOptions({
        interpolationDegree: 3,
        interpolationAlgorithm: Cesium.HermitePolynomialApproximation
    });
}


initMap();
if (typeof droneRoute !== 'undefined' && Object.keys(droneRoute[0]).length !== 0) {
    initTime();
    createDrone();
    initDropdown();

    clickViewTopDown();
    hermitePolynomialInterpolation();
}
if (typeof liveDronesUrl !== 'undefined') {
    updateLiveDrones();
    setInterval(function () {
        updateLiveDrones();
    }, 2000);
}