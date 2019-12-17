var map, popup, Popup;

function initMap() {
    map = new google.maps.Map(document.getElementById('map'), {
        zoom: 8,
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
    Popup = createPopupClass();
    popup = new Popup(
        new google.maps.LatLng(35.8, 139.19),
        document.getElementById('content'));
    popup.setMap(map);
    loadRivers(popup);
}

/**
 * Returns the Popup class.
 *
 * Unfortunately, the Popup class can only be defined after
 * google.maps.OverlayView is defined, when the Maps API is loaded.
 * This function should be called by initMap.
 */
function createPopupClass() {
  /**
   * A customized popup on the map.
   * @param {!google.maps.LatLng} position
   * @param {!Element} content The bubble div.
   * @constructor
   * @extends {google.maps.OverlayView}
   */
  function Popup(position, content) {
    this.position = position;

    content.classList.add('popup-bubble');

    // This zero-height div is positioned at the bottom of the bubble.
    var bubbleAnchor = document.createElement('div');
    bubbleAnchor.classList.add('popup-bubble-anchor');
    bubbleAnchor.appendChild(content);

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
    //content.innerHTML = divPosition.y + ", ";
    //content.innerHTML = this.containerDiv.children[0].className; //divPosition.y + ", ";
    if(divPosition.y > 0){
        content.className = "popup-bubble";
        this.containerDiv.children[0].className = "popup-bubble-anchor";
        this.containerDiv.className = "popup-container";
    }else{
        content.className = "popdown-bubble";
        this.containerDiv.children[0].className = "popdown-bubble-anchor";
        this.containerDiv.className = "popdown-container";
        //bubbleAnchor.className = "popdown-bubble-anchor";
        //this.containerDiv.children[0].style.border-left = 12px;
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

    Popup.prototype.setPosition = function(position) {
        this.position = position;
    }

    Popup.prototype.setContent = function(river) {
        //console.log(river);
        content.innerHTML = "<h3>" + river.name + "</h3>";
        content.innerHTML += "<p><b>Current Level: " + river.level + " m</b></br>";
        content.innerHTML += "Updated: " + river.date + "</p>";
        content.innerHTML += "LW: " + river.low_water + " &nbsp; MW: " + river.middle_water + " &nbsp; HW: " + river.high_water;
        content.innerHTML += '<p align="right"><a href="' + river.url + '" target="_blank">Source</a></p>';
    }
  };

  return Popup;
}