function loadRivers(popup) {
    $.getJSON("static/js/data/river.json", function(json){
        rivers = json.rivers;
        for (let i = 0; i < rivers.length; i++) {
        var iriver = rivers[i];
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
        if (iriver.level >= iriver.high_water){
            river_color = '#FF0000';
        } else if (iriver.level >= iriver.middle_water){
            river_color = '#00FF00';
        } else if (iriver.level >= iriver.low_water){
            river_color = '#0000FF';
        } else {
            river_color = '#8a8a8a';
        }

        var river = new google.maps.Polyline({
            path: riverCoordinates,
            geodesic: true,
            strokeColor: river_color,
            strokeOpacity: 1.0,
            strokeWeight: 7,
            id: i
        });

        river.addListener('mouseover', function(event) {
            popup.setContent(rivers[i]);
            popup.show();
            popup.setPosition(event.latLng);
            popup.draw();
        });

        river.addListener('mouseout', function() {
            popup.hide();
        });

        river.setMap(map);
    }
    });
}