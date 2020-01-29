function activateSidebar () {
    $('#sidebar').addClass('active');
};

function distance(lat1, lng1, lat2, lng2) {
    if ((lat1 == lat2) && (lng1 == lng2)) {return 0;}
    else{
        var radlat1 = Math.PI * lat1/180;
		var radlat2 = Math.PI * lat2/180;
		var theta = lng1-lng2;
		var radtheta = Math.PI * theta/180;
		var dist = Math.sin(radlat1) * Math.sin(radlat2) + Math.cos(radlat1) * Math.cos(radlat2) * Math.cos(radtheta);
		if (dist > 1) {
			dist = 1;
		}
		dist = Math.acos(dist);
		dist = dist * 180/Math.PI;
		dist = dist * 60 * 1.1515;
        dist = dist * 1.609344
		return dist;
    }
}

function mapLink (lat, lng) {
    return '<a href="https://www.google.com/maps/search/?api=1&query=' + lat + ',' + lng + '" target="_blank">'
            + lat + ', ' + lng + '</a>';
}

function showOrHide (id, preText, value, postText) {
    if (value == null) {
        $('#' + id).hide();
    }
    else {
        $('#' + id).show();
        $('#' + id).html(preText + value + postText);
    }
}

function updateSidebar (section) {
    $('#sb-river-name').html(section.river);
    $('#sb-section-name').html(section.name);
    showOrHide ("sb-difficulty", "Difficulty: ", section.difficulty, "");
    $('#sb-distance').html("Air Distance: " + distance(section.start_lat,
            section.start_lng, section.end_lat, section.end_lng).toFixed(2) + " km");
    $('#sb-start').html("Start: " + mapLink(section.start_lat, section.start_lng));
    $('#sb-end').html("End: " + mapLink(section.end_lat, section.end_lng));
};

$('#dismiss, .overlay').on('click', function () {
    // hide sidebar
    $('#sidebar').removeClass('active');
    // hide overlay
    $('.overlay').removeClass('active');
});

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

            river.addListener('click', function() {
                updateSidebar(rivers[i]);
                activateSidebar();
                loadChart(rivers[i]);
            });

            river.setMap(map);
        }
    });
}

$(function() {
  var $tabButtonItem = $('#tab-button li'),
      $tabSelect = $('#tab-select'),
      $tabContents = $('.tab-contents'),
      activeClass = 'is-active';

  $tabButtonItem.first().addClass(activeClass);
  $tabContents.not(':first').hide();

  $tabButtonItem.find('a').on('click', function(e) {
    var target = $(this).attr('href');

    $tabButtonItem.removeClass(activeClass);
    $(this).parent().addClass(activeClass);
    $tabSelect.val(target);
    $tabContents.hide();
    $(target).show();
    e.preventDefault();
  });

  $tabSelect.on('change', function() {
    var target = $(this).val(),
        targetSelectNum = $(this).prop('selectedIndex');

    $tabButtonItem.removeClass(activeClass);
    $tabButtonItem.eq(targetSelectNum).addClass(activeClass);
    $tabContents.hide();
    $(target).show();
  });
});