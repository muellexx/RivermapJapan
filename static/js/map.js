/*var rivrs;
$.getJSON("static/js/river.json", function(json) {
        rivrs = json;
        console.log("success");
    })
    .done(function() {
        console.log("second success");
    })
    .fail(function() {
        console.log("error");
    })
    .always(function() {
        console.log("complete");
    });*/

function loadRivers() {
    $.getJSON("static/js/river.json", setRivers);
    //console.log("hi");
}

function setRivers(json) {
    rivers = json.rivers;
    for (let i = 0; i < rivers.length; i++) {
        var id = 0;
        var riverCoordinates = [{
                lat: rivers[i].start_lat,
                lng: rivers[i].start_lng
            },
            {
                lat: rivers[i].end_lat,
                lng: rivers[i].end_lng
            }
        ];

        var river = new google.maps.Polyline({
            path: riverCoordinates,
            geodesic: true,
            strokeColor: '#FF0000',
            strokeOpacity: 1.0,
            strokeWeight: 5
        });

        var contentString = '<div id="content">' +
            '<div id="siteNotice">' +
            '</div>' +
            '<h1 id="firstHeading" class="firstHeading">Tama River</h1>' +
            '<div id="bodyContent">' +
            '<p><b>Tama River</b>, located in <b>Tokyo Prefecture</b>, is a local ' +
            'River of WhiteWater Level II-III.</p>' +
            '</div>' +
            '</div>';

        var infowindow = new google.maps.InfoWindow({
            content: contentString,
        });

        river.addListener('mouseover', function(event) {
            infowindow.setPosition(event.latLng);
            infowindow.open(map);
        });

        river.addListener('mouseout', function() {
            infowindow.close(map);
        });

        river.setMap(map);
    }
}