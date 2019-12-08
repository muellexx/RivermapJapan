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
        river = rivers[i];
        var riverCoordinates = [{
                lat: rivers[i].start_lat,
                lng: rivers[i].start_lng
            },
            {
                lat: rivers[i].end_lat,
                lng: rivers[i].end_lng
            }
        ];

        var river_color;
        if (river.level >= river.highwater){
            river_color = '#FF0000';
        } else if (river.level >= river.middlewater){
            river_color = '#00FF00';
        } else if (river.level >= river.lowwater){
            river_color = '#0000FF';
        } else {
            river_color = '#999999';
        }
        console.log(river_color);
        var river = new google.maps.Polyline({
            path: riverCoordinates,
            geodesic: true,
            strokeColor: river_color,
            strokeOpacity: 1.0,
            strokeWeight: 5
        });

        var contentString = '<div id="content">' +
            '<div id="siteNotice">' +
            '</div>' +
            '<h1 id="firstHeading" class="firstHeading">' + rivers[i].name + '</h1>' +
            '<div id="bodyContent">' +
            '<p><b>Waterevel:</b>' + rivers[i].level + '</p>' +
            '<p><a href="' + rivers[i].url + '" target="_blank">Source</a></p>' +
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