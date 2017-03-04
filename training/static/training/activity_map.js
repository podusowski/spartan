activityMap = {}

activityMap.makeLineStyle = function(color, width) {
    stroke = new ol.style.Stroke({color: color, width: width });
    return new ol.style.Style({ stroke: stroke });
};

activityMap.makeGpsLayer = function(json) {
    var points = json.map(function(point) { return [point.lon, point.lat]; });
    var track = new ol.geom.LineString(points).transform('EPSG:4326', 'EPSG:3857');

    var featureLine = new ol.Feature({
        geometry: track
    });

    var sourceLine = new ol.source.Vector({
        features: [featureLine]
    });

    var styles = [
        this.makeLineStyle('#333', 6),
        this.makeLineStyle('orange', 3),
    ];

    var layer = new ol.layer.Vector({
        source: sourceLine,
        style: styles
    });

    return layer
};

activityMap.renderMap = function(target, layer) {
    var osmLayer = new ol.layer.Tile({source: new ol.source.OSM()});

    var map = new ol.Map({
            controls: ol.control.defaults().extend([new ol.control.FullScreen()]),
            layers: [osmLayer, layer],
            target: target
        });

    map.getView().fit(layer.getSource().getExtent(), map.getSize());
};
