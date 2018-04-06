var viewer;
var entity;
var start;
var stop;
var lineWidth = 7;


function initMap() {
    viewer = new Cesium.Viewer('cesiumContainer', {
        infoBox: false,
        selectionIndicator: false,
        shouldAnimate: true
        //timeline: false, 
        //navigationHelpButton: false
    });
    //Enable depth testing so things behind the terrain disappear.
    //viewer.scene.globe.depthTestAgainstTerrain = true;
}

function initTime() {
    let routeStartTime = droneRoutes[0]['time'];
    let routeEndTime = droneRoutes[droneRoutes.length - 1]['time'];

    start = Cesium.JulianDate.fromDate(new Date(routeStartTime * 1000)); // * 1000 to go from seconds to milliseconds, since Date takes milliseconds
    stop = Cesium.JulianDate.fromDate(new Date(routeEndTime * 1000));

    viewer.clock.startTime = start.clone();
    viewer.clock.stopTime = stop.clone();
    viewer.clock.currentTime = start.clone();
    viewer.clock.clockRange = Cesium.ClockRange.LOOP_STOP;
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
}

function computeFlightCoordinates() {
    var positionProperty = new Cesium.SampledPositionProperty();
    for (let i = 0; i < droneRoutes.length; i++) {
        let droneRoute = droneRoutes[i];
        let time = Cesium.JulianDate.fromDate(new Date(droneRoute['time'] * 1000));
        let position = Cesium.Cartesian3.fromDegrees(droneRoute['lon'], droneRoute['lat'], 20.0);
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
    $('#dropdownMenu').html("Viewing drone")
    $('#viewDrone').click(clickViewDrone)
    $('#viewSide').click(clickViewSide)
    $('#viewTopDown').click(clickViewTopDown);
}

function clickViewDrone() {
    viewDrone();
    $('#dropdownMenu').html("Viewing drone")
    $('#viewSide').removeClass('active');
    $('#viewTopDown').removeClass('active');
    $('#viewDrone').addClass('active');
}

function clickViewSide() {
    viewSide();
    $('#dropdownMenu').html("Viewing side")
    $('#viewDrone').removeClass('active');
    $('#viewTopDown').removeClass('active');
    $('#viewSide').addClass('active');
}

function clickViewTopDown() {
    viewTopDown();
    $('#dropdownMenu').html("Viewing top down")
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
        interpolationDegree: 5,
        interpolationAlgorithm: Cesium.HermitePolynomialApproximation
    })
}


initMap();
initTime();
createDrone();
initDropdown();

clickViewTopDown();
hermitePolynomialInterpolation();
