var map, popup, Popup, latt, lngg, zooom, objectType;
var currStartLat, currStartLng, currEndLat, currEndLng;

function addSection(event) {
    console.log(event.latLng);
}

function setCoords(latt, lngg, zooom) {
    this.latt = latt;
    this.lngg = lngg;
    this.zooom = zooom;
}

function setSectionCoords(currStartLat, currStartLng, currEndLat, currEndLng) {
    this.currStartLat = currStartLat;
    this.currStartLng = currStartLng;
    this.currEndLat = currEndLat;
    this.currEndLng = currEndLng;
    this.latt = (currStartLat + currEndLat)/2;
    this.lngg = (currStartLng + currEndLng)/2;
}

function setType(objectType) {
    this.objectType = objectType;
}

function initMap() {
    map = new google.maps.Map(document.getElementById('map-small'), {
        zoom: zooom,
        minZoom: 5,
        center: {
            lat: latt,
            lng: lngg
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

    if(this.objectType == 0 || this.objectType == 2) {
        Section = createSectionClass();
        section = new Section();
        section.setMap(map);
        map.addListener('click', function(event) {
            section.addSection(event);
        });
    } else if(this.objectType == 1 || this.objectType == 3) {
    console.log('hi')
        Spot = createSpotClass();
        spot = new Spot();
        map.addListener('click', function(event) {
            spot.addSpot(event);
        });
    }
    if (this.objectType == 2){
        var riverCoordinates = [{
            lat: this.currStartLat,
            lng: this.currStartLng
        },
        {
            lat: this.currEndLat,
            lng: this.currEndLng
        }
        ];
        this.currRiver = new google.maps.Polyline({
            path: riverCoordinates,
            geodesic: true,
            strokeColor: '#00D200',
            strokeOpacity: 1.0,
            strokeWeight: 7,
            map: this.map
        });
    } else if (this.objectType == 3){
        var coordinates = new google.maps.LatLng(this.latt, lngg);
        var image = {
            url: "/media/icons/Spot/MarkerSpot3.png",
            size: new google.maps.Size(32,40),
            anchor: new google.maps.Point(16,40)
        };
        var currSpot = new google.maps.Marker({
            position: coordinates,
            icon: image,
            map: this.map
        });
    }

}

function createSpotClass() {
    function Spot() {
        this.lat = null;
        this.lng = null;
        this.spot = null;
    }

    Spot.prototype = Object.create(google.maps.Marker.prototype);

    Spot.prototype.addSpot = function(event) {
        this.setPoint(event);
        this.drawSpot();
    };

    Spot.prototype.setPoint = function(event) {
        this.lat = event.latLng.lat();
        this.lng = event.latLng.lng();
        num = this.lat.toFixed(2)
        console.log(num);
        document.getElementById("id_lat").value = this.lat.toFixed(5);
        document.getElementById("id_lng").value = this.lng.toFixed(5);
    }

    Spot.prototype.drawSpot = function() {
        var coordinates = new google.maps.LatLng(this.lat, this.lng);
        var image = {
            url: "/media/icons/Spot/MarkerSpot0.png",
            size: new google.maps.Size(32,40),
            anchor: new google.maps.Point(16,40)
        };
        if (this.spot == null) {
            this.spot = new google.maps.Marker({
                position: coordinates,
                icon: image,
                map: map
            });
        } else {
            this.spot.setOptions({
                position: coordinates,
            });
        }
    }

    return Spot;
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
                strokeColor: '#64DBFF',
                strokeOpacity: 1.0,
                strokeWeight: weight,
                id: 1
            });
        } else {
            this.river.setOptions({
                path: riverCoordinates,
                strokeWeight: weight,
            });
        }

        this.river.setMap(this.map);
    }

    return Section;
}