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
    if (value == null || value === "") {
        $('#' + id).hide();
    }
    else {
        $('#' + id).show();
        $('#' + id).html(preText + value + postText);
    }
}

function updateSidebar (section, isSpot) {
    if(document.documentElement.lang == 'ja'){
            river = section.river_jp;
            name = section.name_jp;
            date = section.date_jp;
            observatory = section.observatory_name_jp;
            dam = section.dam_name_jp;
        } else {
            river = section.river;
            name = section.name;
            date = section.date;
            observatory = section.observatory_name;
            dam = section.dam_name;
        }
    if (section.dam_id == undefined){
        unit = " m"
    } else {
        unit = " &#13221;/s"
    }
    $('#sb-river-name').html('<a href="map/' + section.prefecture.toLowerCase() + '/river/' + section.river_id + '/">' + river + '</a>');
    if (isSpot)
        $('#sb-section-name').html('<a href="map/' + section.prefecture.toLowerCase() + '/spot/' + section.id + '/">' + name + '</a>');
    else
        $('#sb-section-name').html('<a href="map/' + section.prefecture.toLowerCase() + '/section/' + section.id + '/">' + name + '</a>');
    showOrHide ("sb-content", "", section.content, "");
    showOrHide ("sb-difficulty", gettext('Difficulty: '), section.difficulty, "");
    if (isSpot)
        $('#sb-distance').hide();
    else{
        $('#sb-distance').show();
        $('#sb-distance').html(gettext('Air Distance: ') + distance(section.start_lat,
                section.start_lng, section.end_lat, section.end_lng).toFixed(2) + gettext(' km'));
    }
    if (isSpot)
        $('#sb-start').html(gettext('Location: ') + mapLink(section.lat, section.lng));
    else
        $('#sb-start').html(gettext('Start: ') + mapLink(section.start_lat, section.start_lng));
    if (isSpot)
        $('#sb-end').hide();
    else{
        $('#sb-end').show();
        $('#sb-end').html(gettext('End: ') + mapLink(section.end_lat, section.end_lng));
    }
    showOrHide ("sb-level", gettext('Current Level: '), section.level, unit);
    showOrHide ("sb-observatory", gettext('Observatory: ') + '<a href="', section.url, '" target="_blank">' + observatory + '</a>');
    if (section.dam_id != undefined){
        showOrHide ("sb-observatory", gettext('Dam: ') + '<a href="', section.url, '" target="_blank">' + dam + '</a>');
    }
    showOrHide ("sb-updated", gettext('Updated: '), date, "");
    showOrHide ("sb-lw", gettext('LW: '), section.low_water, unit);
    showOrHide ("sb-mw", gettext('MW: '), section.middle_water, unit);
    showOrHide ("sb-hw", gettext('HW: '), section.high_water, unit);
    $('#id_section').val(section.id);
    if(isSpot) {
        $('#object_type').val('spot');
    } else {
        $('#object_type').val('section');
    }
    $('#sb-comments').html("");
    if (section.comments !== undefined && section.comments.length != 0){
        loadComments(section.comments);
    } else {
        $('#sb-comments').html(gettext('No Comments yet'));
    }
};

$('#dismiss, .overlay').on('click', function () {
    // hide sidebar
    $('#sidebar').removeClass('active');
    // hide overlay
    $('.overlay').removeClass('active');
});

// ----- River Sections on the map ----- //
var riverArray = new Array();

function loadRivers(popup) {
    $.getJSON("/static/js/data/river.json", {_: new Date().getTime()}, function(json){
        rivers = json.rivers;
        colors = ['#64DBFF', '#8A8A8A', '#2828FF', '#00D200', '#FFB300', '#FF0000'];
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

            var river_color = '#64DBFF';
            if (iriver.high_water != null || iriver.middle_water != null || iriver.low_water != null) {
                if (iriver.level >= iriver.high_water){
                    river_color = '#FF0000';
                } else if (iriver.level >= iriver.middle_water){
                    river_color = '#00D200';
                } else if (iriver.level >= iriver.low_water){
                    river_color = '#2828FF';
                } else {
                    river_color = '#8a8a8a';
                }
            }

            var river = new google.maps.Polyline({
                path: riverCoordinates,
                geodesic: true,
                strokeColor: colors[iriver.color],
                strokeOpacity: 1.0,
                strokeWeight: 7,
                id: i
            });

            river.addListener('mouseover', function(event) {
                popup.setContent(rivers[i]);
                popup.show();
                loadChart(rivers[i], 'pop-chart', 12);
                popup.setPosition(event.latLng, false);
                popup.draw();
            });

            river.addListener('mouseout', function() {
                popup.hide();
            });

            river.addListener('click', function() {
                popup.hide();
                updateSidebar(rivers[i], false);
                activateSidebar();
                loadChart(rivers[i], 'sb-chart', 12);
            });

            river.setMap(map);
            riverArray.push(river)
        }
    });
}

function SectionToggleControl(controlDiv) {
    controlDiv.src = "/media/icons/riverM.png";
    controlDiv.classList.add('rounded-circle')
    controlDiv.classList.add('control-button')
    controlDiv.classList.add('control-button-active')

    controlDiv.addEventListener('click', function() {
        if (controlDiv.classList.contains('control-button-active')) {
            hideRivers();
            controlDiv.classList.remove('control-button-active')
        } else {
            showRivers();
            controlDiv.classList.add('control-button-active')
        }
    });
}

function hideRivers() {
    for (let i = 0; i < riverArray.length; i++) {
        riverArray[i].setVisible(false);
    }
}

function showRivers() {
    for (let i = 0; i < riverArray.length; i++) {
        riverArray[i].setVisible(true);
    }
}

// ----- River Spots on the map ----- //
var spotArray = new Array();

function loadSpots(popup) {
    $.getJSON("/static/js/data/spot.json", function(json){
        spots = json.spots;
        for (let i = 0; i < spots.length; i++) {
            var ispot = spots[i];
            var coordinates = new google.maps.LatLng(spots[i].lat, spots[i].lng);
            var url = "/media/icons/Spot/MarkerSpot" + spots[i].color + ".png";

            var image = {
                url: url,
                size: new google.maps.Size(32,40),
                anchor: new google.maps.Point(16,40)
            };

            var spot = new google.maps.Marker({
                position: coordinates,
                icon: image,
                map: map
            });

            spot.addListener('mouseover', function(event) {
                popup.setContent(spots[i]);
                popup.show();
                loadChart(spots[i], 'pop-chart', 12);
                popup.setPosition(event.latLng, true);
                popup.draw();
            });

            spot.addListener('mouseout', function() {
                popup.hide();
            });

            spot.addListener('click', function() {
                updateSidebar(spots[i], true);
                activateSidebar();
                loadChart(spots[i], 'sb-chart', 12);
            });

            spot.setMap(map);
            spotArray.push(spot)
        }
    });
}

function SpotToggleControl(controlDiv, map) {
    controlDiv.src = "/media/icons/waveM.png";
    controlDiv.classList.add('rounded-circle')
    controlDiv.classList.add('control-button')
    controlDiv.classList.add('control-button-active')

    controlDiv.addEventListener('click', function() {
        if (controlDiv.classList.contains('control-button-active')) {
            hideSpots();
            controlDiv.classList.remove('control-button-active')
        } else {
            showSpots();
            controlDiv.classList.add('control-button-active')
        }
    });
}

function hideSpots() {
    for (let i = 0; i < spotArray.length; i++) {
        spotArray[i].setVisible(false);
    }
}

function showSpots() {
    for (let i = 0; i < spotArray.length; i++) {
        spotArray[i].setVisible(true);
    }
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