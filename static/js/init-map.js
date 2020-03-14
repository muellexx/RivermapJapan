var map, popup, Popup;

function initMap() {
    map = new google.maps.Map(document.getElementById('map'), {
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
            },
            {
                featureType: 'administrative.country',
                elementType: 'geometry.stroke',
                stylers: [{
                    "weight": "3"
                }]
            },
            {
                featureType: 'administrative.country',
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

    Popup = createPopupClass();
    popup = new Popup(
        new google.maps.LatLng(35.8, 139.19),
        document.getElementById('riverinfo'));
    popup.setMap(map);
    loadRivers(popup);
    loadSpots(popup);
}

function createPopupClass() {
  /**
   * A customized popup on the map.
   * @param {!google.maps.LatLng} position
   * @param {!Element} riverinfo The bubble div.
   * @constructor
   * @extends {google.maps.OverlayView}
   */
  function Popup(position, riverinfo) {
    this.position = position;
    this.upperHalf = false;

    // This zero-height div is positioned at the bottom of the bubble.
    var bubbleAnchor = document.createElement('div');
    bubbleAnchor.classList.add('popup-bubble-anchor');
    bubbleAnchor.appendChild(riverinfo);

    // This zero-height div is positioned at the bottom of the tip.
    this.containerDiv = document.createElement('div');
    this.containerDiv.classList.add('popup-container');
    this.containerDiv.appendChild(bubbleAnchor);
    this.containerDiv.style.visibility = 'hidden';

    // Optionally stop clicks, etc., from bubbling up to the map.
    google.maps.OverlayView.preventMapHitsAndGesturesFrom(this.containerDiv);
  }
  // ES5 magic to extend google.maps.OverlayView.
  Popup.prototype = Object.create(google.maps.OverlayView.prototype);

  /** Called when the popup is added to the map. */
  Popup.prototype.onAdd = function() {
    this.getPanes().floatPane.appendChild(this.containerDiv);
  };

  /** Called when the popup is removed from the map. */
  Popup.prototype.onRemove = function() {
    if (this.containerDiv.parentElement) {
      this.containerDiv.parentElement.removeChild(this.containerDiv);
    }
  };

  /** Called each frame when the popup needs to draw itself. */
  Popup.prototype.draw = function() {
    var divPosition = this.getProjection().fromLatLngToDivPixel(this.position);
    if(this.upperHalf) {
        riverinfo.className = "popup-bubble";
        riverinfo.classList.add('content-section');
        this.containerDiv.children[0].className = "popup-bubble-anchor";
        this.containerDiv.className = "popup-container";
    }else{
        riverinfo.className = "popdown-bubble";
        riverinfo.classList.add('content-section');
        this.containerDiv.children[0].className = "popdown-bubble-anchor";
        this.containerDiv.className = "popdown-container";
    }

    // Hide the popup when it is far out of view.
    var display =
        Math.abs(divPosition.x) < 4000 && Math.abs(divPosition.y) < 4000 ?
        'block' :
        'none';

    if (display === 'block') {
      this.containerDiv.style.left = divPosition.x + 'px';
      this.containerDiv.style.top = divPosition.y + 'px';
    }

    // Set the visibility to 'hidden' or 'visible'.
    Popup.prototype.hide = function() {
      if (this.containerDiv) {
        // The visibility property must be a string enclosed in quotes.
        this.containerDiv.style.visibility = 'hidden';
      }
    };

    Popup.prototype.show = function() {
    if (this.containerDiv) {
        this.containerDiv.style.visibility = 'visible';
      }
    };

    if (this.containerDiv.style.display !== display) {
      this.containerDiv.style.display = display;
    }

    Popup.prototype.setPosition = function(position, isSpot) {
        divPosition = this.getProjection().fromLatLngToDivPixel(position);
        if (this.getProjection().fromLatLngToDivPixel(position).y > 0) {
            if (isSpot){
                divPosition.y -= 48;
            } else {
                divPosition.y -= 15;
            }
            this.upperHalf = true;
        }
        else {
            if (isSpot){
                divPosition.y += 0;
            } else {
                divPosition.y += 15;
            }
            this.upperHalf = false;
        }
        this.position = this.getProjection().fromDivPixelToLatLng(divPosition);
    }

    Popup.prototype.setContent = function(section) {
        riverinfo.innerHTML = "<h4>" + section.river + "</h4>";
        if (section.difficulty != null) {
            riverinfo.innerHTML += "<h6>" + section.name + "(" + section.difficulty + ")</h6>";
        } else {
            riverinfo.innerHTML += "<h6>" + section.name + "</h6>";
        }
        riverinfo.innerHTML += '<div id="pop-chart-div"></div>'
        if (section.observatory_id != undefined) {
            riverinfo.innerHTML += "Updated: " + section.date + "</p>";
            riverinfo.innerHTML += '<p style="float: right;"><a href="' + section.url + '" target="_blank">Source</a></p>';
        }
        if ((section.low_water != null)||(section.middle_water != null)||(section.high_water != null)) {
            riverinfo.innerHTML += "LW: " + section.low_water + " &nbsp; MW: " + section.middle_water + " &nbsp; HW: " + section.high_water;
        }
    }
  };

  return Popup;
}