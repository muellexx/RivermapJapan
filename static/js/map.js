var rivers = $.getJson( "map.json", function() {
  console.log( "success" );
})
  .done(function() {
    console.log( "second success" );
  })
  .fail(function() {
    console.log( "error" );
  })
  .always(function() {
    console.log( "complete" );
  });

function initMap() {
    var map = new google.maps.Map(document.getElementById('map'), {
        zoom: 12,
        center: {
            lat: 35.802514,
            lng: 139.194369
        },
        mapTypeId: 'terrain',
        styles: [{
                elementType: 'all',
                stylers: [{
                    "visibility": "on"
                }]
            },
            {
                featureType: 'road',
                elementType: 'labels',
                stylers: [{
                    "visibility": "off"
                }]
            },
            {
                featureType: 'water',
                elementType: 'geometry',
                stylers: [{
                    "gamma": "0.3"
                }]
            },
            {
                featureType: 'water',
                elementType: 'labels',
                stylers: [{
                    "color": "#000000"
                }]
            },
            {
                featureType: 'poi',
                elementType: 'labels',
                stylers: [{
                    "visibility": "off"
                }]
            },
            {
                featureType: 'transit.line',
                elementType: 'labels',
                stylers: [{
                    "visibility": "off"
                }]
            },
            {
                featureType: 'transit.station',
                elementType: 'labels.text.fill',
                stylers: [{
                    "color": "#808080"
                }]
            },
            {
                featureType: 'transit.station',
                elementType: 'labels.icon',
                stylers: [{
                    "lightness": "60"
                }]
            },
            {
                featureType: 'administrative.province',
                elementType: 'geometry.stroke',
                stylers: [{
                    "weight": "3"
                }]
            },
            {
                featureType: 'administrative.province',
                elementType: 'geometry.stroke',
                stylers: [{
                    "color": "#000000"
                }]
            }
        ]
    });

    //var river = [];
    //var infowindow = [];

    var id = 0;
    var riverCoordinates = [{
            lat: 35.8,
            lng: 139.176
        },
        {
            lat: 35.785,
            lng: 139.257
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