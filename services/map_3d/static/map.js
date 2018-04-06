var viewer = new Cesium.Viewer('cesiumContainer', {
    infoBox: false, //Disable InfoBox widget
    selectionIndicator: false, //Disable selection indicator
    shouldAnimate: true // Enable animations
});



//Enable depth testing so things behind the terrain disappear.
viewer.scene.globe.depthTestAgainstTerrain = true;

//Set the random number seed for consistent results.
Cesium.Math.setRandomNumberSeed(3);

//Set bounds of our simulation time
//var start = Cesium.JulianDate.fromDate(new Date(2015, 2, 25, 16));
var routeStartTime = droneRoutes[0]['time'];
var start = Cesium.JulianDate.fromDate(new Date(routeStartTime * 1000)); // * 1000 to go from seconds to milliseconds, since Date takes milliseconds
//var stop = Cesium.JulianDate.addSeconds(start, 360, new Cesium.JulianDate());
var routeEndTime = droneRoutes[droneRoutes.length - 1]['time'];
var stop = Cesium.JulianDate.fromDate(new Date(routeEndTime * 1000));

//Make sure viewer is at the desired time.
viewer.clock.startTime = start.clone();
viewer.clock.stopTime = stop.clone();
viewer.clock.currentTime = start.clone();
viewer.clock.clockRange = Cesium.ClockRange.LOOP_STOP; //Loop at the end
viewer.clock.multiplier = 1;

//Set timeline to simulation bounds
viewer.timeline.zoomTo(start, stop);

var lineWidth = 7;

//Generate a random circular pattern with varying heights.
function computeCirclularFlight(lon, lat, radius) {
    var property = new Cesium.SampledPositionProperty();
    for (var i = 0; i <= 360; i += 45) {
        var radians = Cesium.Math.toRadians(i);
        var time = Cesium.JulianDate.addSeconds(start, i, new Cesium.JulianDate());
        var position = Cesium.Cartesian3.fromDegrees(lon + (radius * 1.5 * Math.cos(radians)), lat + (radius * Math.sin(radians)), Cesium.Math.nextRandomNumber() * 500 + 1750);
        property.addSample(time, position);

        //Also create a point for each sample we generate.
        viewer.entities.add({
            position: position,
            point: {
                pixelSize: 8,
                color: Cesium.Color.TRANSPARENT,
                outlineColor: Cesium.Color.YELLOW,
                outlineWidth: 3
            }
        });
    }
    return property;
}

function computeFlightCoordinates() {
    var positionProperty = new Cesium.SampledPositionProperty();
    for (let i = 0; i < droneRoutes.length; i++) {
        let droneRoute = droneRoutes[i];
        let time = Cesium.JulianDate.fromDate(new Date(droneRoute['time'] * 1000));
        let position = Cesium.Cartesian3.fromDegrees(droneRoute['lon'], droneRoute['lat'], 20.0);
        positionProperty.addSample(time, position);

        //Also create a point for each sample we generate.
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

//Compute the entity position property.
//var position = computeCirclularFlight(-112.110693, 36.0994841, 0.03);
var position = computeFlightCoordinates();

//Actually create the entity
var entity = viewer.entities.add({

    //Set the entity availability to the same interval as the simulation time.
    availability: new Cesium.TimeIntervalCollection([new Cesium.TimeInterval({
        start: start,
        stop: stop
    })]),

    //Use our computed positions
    position: position,

    //Automatically compute orientation based on position movement.
    orientation: new Cesium.VelocityOrientationProperty(position),

    //Load the Cesium plane model to represent the entity
    model: {
        uri: droneModel,
        minimumPixelSize: 32
    },

    //Show the path as a pink line sampled in 1 second increments.
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

//Add button to view the path from the top down
function viewTopDown() {
    viewer.trackedEntity = undefined;
    viewer.zoomTo(viewer.entities);//, new Cesium.HeadingPitchRange(0, Cesium.Math.toRadians(-90)));
}

//Add button to view the path from the side
function viewSide() {
    viewer.trackedEntity = undefined;
    viewer.zoomTo(viewer.entities, new Cesium.HeadingPitchRange(Cesium.Math.toRadians(-90), Cesium.Math.toRadians(-15), 7500));
}

//Add button to track the entity as it moves
function viewAircraft() {
    viewer.trackedEntity = entity;
}

//Add a combo box for selecting each interpolation mode.
function linearInterpolation() {
    entity.position.setInterpolationOptions({
        interpolationDegree: 1,
        interpolationAlgorithm: Cesium.LinearApproximation
    })
}
function lagrangePolynomialInterpolation() {
    entity.position.setInterpolationOptions({
        interpolationDegree: 5,
        interpolationAlgorithm: Cesium.LagrangePolynomialApproximation
    })
}
function hermitePolynomialInterpolation() {
    entity.position.setInterpolationOptions({
        interpolationDegree: 2,
        interpolationAlgorithm: Cesium.HermitePolynomialApproximation
    })
}

$('#dropdownMenu').html("Viewing drone")
$('#viewDrone').click(clickViewDrone)
$('#viewTopdown').click(clickViewTopdown);

function clickViewDrone() {
    viewAircraft();
    $('#dropdownMenu').html("Viewing drone")
    $('#viewTopdown').removeClass('active');
    $('#viewDrone').addClass('active');
}

function clickViewTopdown() {
    viewTopDown();
    $('#dropdownMenu').html("Viewing top down")
    $('#viewDrone').removeClass('active');
    $('#viewTopdown').addClass('active');
}

clickViewDrone();
lagrangePolynomialInterpolation();


function createModel(url) {
    viewer.entities.removeAll();

    position = Cesium.Cartesian3.fromDegrees(10.329182, 55.473886, 20.0);
    var heading = Cesium.Math.toRadians(-90);
    var pitch = 0;
    var roll = 0;
    var hpr = new Cesium.HeadingPitchRoll(heading, pitch, roll);
    var orientation = Cesium.Transforms.headingPitchRollQuaternion(position, hpr);

    var entity = viewer.entities.add({
        name: url,
        position: position,
        orientation: orientation,
        model: {
            uri: url,
            maximumScale: 20000
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

console.log(droneModel)
console.log(droneRoutes)

//createModel(document.getElementById('droneModel').value);

