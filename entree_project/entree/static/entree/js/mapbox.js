(function () {

    // get location info embedded in webpage
    var lat = $('#lat').text();
    var long = $('#long').text();
    var business_name = $('#business_name').text();

    // populate the mapbox
    mapboxgl.accessToken = 'pk.eyJ1IjoicGh5cmJvbHR6IiwiYSI6ImNpbjNuMXVvaTBjMWJ2OWtrZGMyamdwaDcifQ.Y_IZJ7YQTHS6CXfhXlwIvw';
    var map = new mapboxgl.Map({
        container: 'map', // container id
        style: 'mapbox://styles/phyrboltz/cin3n2wmx000gahnlnghbmyx0', //stylesheet location
        center: [long, lat], // starting position
        zoom:  15 // starting zoom
    });
    
    map.on('load', function () {
        map.addSource("markers", {
            "type": "geojson",
            "data": {
                "type": "FeatureCollection",
                "features": [{
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [long, lat]
                    },
                    "properties": {
                        "title": business_name,
                        "marker-symbol": "marker",
                        "marker-color": "#0c84e4",
                        "marker-size": "large"
                    }
                }]
            }
        });
        map.addLayer({
            "id": "markers",
            "type": "symbol",
            "source": "markers",
            "layout": {
                "icon-image": "{marker-symbol}-15",
                "text-field": "{title}",
                "text-font": ["Open Sans Semibold", "Arial Unicode MS Bold"],
                "text-offset": [0, -.6],
                "text-anchor": "bottom"
            }
        });
    });
})();