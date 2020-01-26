var map, popup, Popup;

function addSection(event) {
    console.log(event.latLng);
}

function initMap() {
    map = new google.maps.Map(document.getElementById('map-small'), {
        zoom: 8,
        minZoom: 5,
        center: {
            lat: 35.802514,
            lng: 139.194369
        },
        scaleControl: true,
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

    // Get Location of User.
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function(position) {
            var pos = {
                lat: position.coords.latitude,
                lng: position.coords.longitude
            };
            if (pos.lat > 21 && pos.lat < 47 && pos.lng > 119 && pos.lng < 151) {
                map.setCenter(pos);
            }
        });
    }

    Section = createSectionClass();
    section = new Section();
    section.setMap(map);

    map.addListener('click', function(event) {
        section.addSection(event);
    });

}

function createSectionClass() {
    function Section() {
        this.startLat = null;
        this.startLng = null;
        this.endLat = null;
        this.endLat = null;
        this.river = null;
    }

    Section.prototype = Object.create(google.maps.Polyline.prototype);

    Section.prototype.addSection = function(event) {
        if ((this.startLat == null)||(this.endLat != null)){
            this.startPoint(event);
        } else {
            this.endPoint(event);
        }
        this.drawSection();
    };

    Section.prototype.startPoint = function(event) {
        this.startLat = event.latLng.lat();
        this.startLng = event.latLng.lng();
        num = this.startLat.toFixed(2)
        console.log(num);
        this.endLat = null;
        this.endLng = null;
        document.getElementById("id_lat").value = this.startLat.toFixed(5);
        document.getElementById("id_lng").value = this.startLng.toFixed(5);
        document.getElementById("id_end_lat").value = null;
        document.getElementById("id_end_lng").value = null;
    }

    Section.prototype.endPoint = function(event) {
        this.endLat = event.latLng.lat();
        this.endLng = event.latLng.lng();
        document.getElementById("id_end_lat").value = this.endLat.toFixed(5);
        document.getElementById("id_end_lng").value = this.endLng.toFixed(5);
    }

    Section.prototype.drawSection = function() {

        if (this.endLat == null){
            var riverCoordinates = [{
                    lat: this.startLat,
                    lng: this.startLng
                },
                {
                    lat: this.startLat,
                    lng: this.startLng
                }
            ];
            var weight = 20;
        } else {
            var riverCoordinates = [{
                    lat: this.startLat,
                    lng: this.startLng
                },
                {
                    lat: this.endLat,
                    lng: this.endLng
                }
            ];
            var weight = 7;
        }
        if (this.river == null) {
            this.river = new google.maps.Polyline({
                path: riverCoordinates,
                geodesic: true,
                strokeColor: '#00FF00',
                strokeOpacity: 1.0,
                strokeWeight: weight,
                id: 1
            });
        } else {
            //this.river.setPath(riverCoordinates);
            this.river.setOptions({
                path: riverCoordinates,
                strokeWeight: weight,
            });
        }

        this.river.setMap(this.map);
    }

    return Section;
}