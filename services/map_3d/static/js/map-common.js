var viewer;

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

initMap();