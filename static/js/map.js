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

function loadComments(sectionComments) {
    $.getJSON("static/js/data/mapObjectComments.json", function(json){
        comments = json.comments
        /*var result = comments.filter(function(){
            return comments.id === sectionComment.id
        });*/
        for (let i = 0; i < sectionComments.length; i++){
            sectionComment = sectionComments[i];
            comment = comments.find(x => x.id === sectionComment)
            console.log(comment.content);
            $("#sb-comments").prepend('<article class="media content-section" style="margin: 0; margin-top: 5px; width: 100%;">'+
                '<div class="media-body">' +
                    '<div class="article-metadata">' +
                        '<img class="rounded-circle article-img" src="' + comment.image_url + '">' +
                        '<a class="mr-2" href="#">' + comment.author + '</a>' +
                        '<small class="text-muted">' + comment.date_posted + '</small>' +
                    '</div>' +
                    '<h2><a class="article-title" href="#">' + comment.title + '</a></h2>' +
                    '<p class="article-content">' + comment.content + '</p>' +
                '</div>' +
            '</article>'
            )
        }
    });
}

function updateSidebar (section) {
    $('#sb-river-name').html('<a href="map/' + section.prefecture + '/river/' + section.river_id + '/">' + section.river + '</a>');
    $('#sb-section-name').html('<a href="map/' + section.prefecture + '/section/' + section.id + '/">' + section.name + '</a>');
    showOrHide ("sb-difficulty", "Difficulty: ", section.difficulty, "");
    $('#sb-distance').html("Air Distance: " + distance(section.start_lat,
            section.start_lng, section.end_lat, section.end_lng).toFixed(2) + " km");
    $('#sb-start').html("Start: " + mapLink(section.start_lat, section.start_lng));
    $('#sb-end').html("End: " + mapLink(section.end_lat, section.end_lng));
    showOrHide ("sb-level", "Current Level: ", section.level, "");
    showOrHide ("sb-observatory", ' Observatory: <a href="', section.url, '" target="_blank">' + section.observatory_name + '</a>');
    showOrHide ("sb-updated", "Updated: ", section.date, "");
    showOrHide ("sb-lw", "LW: ", section.low_water, "");
    showOrHide ("sb-mw", "MW: ", section.middle_water, "");
    showOrHide ("sb-hw", "HW: ", section.high_water, "");
    $('#id_section').val(section.id);
    $('#sb-comments').html("");
    if (section.comments !== undefined && section.comments.length != 0){
        loadComments(section.comments);
    } else {
        $('#sb-comments').html("No Comments yet");
    }
};

function newComment () {
    $('#sb-comment-form').show();
}

$(document).on('submit', '#sb-comment-form', function(e){
    $.ajax({
        type: 'POST',
        url: '/',
        data:{
            section:$('#id_section').val(),
            title:$('#id_title').val(),
            content:$('#id_content').val(),
            csrfmiddlewaretoken:$('input[name=csrfmiddlewaretoken]').val(),
            action: 'post'
        },
        success: function(json){
            document.getElementById("sb-comment-form").reset();
            document.getElementById("sb-comment-form").style.display = "none";
            $("#sb-comments").prepend('<article class="media content-section" style="margin: 0; margin-top: 5px; width: 100%;">'+
                '<div class="media-body">' +
                    '<div class="article-metadata">' +
                        '<img class="rounded-circle article-img" src="' + json.image_url + '">' +
                        '<a class="mr-2" href="#">' + json.author + '</a>' +
                        '<small class="text-muted">' + json.date_posted + '</small>' +
                    '</div>' +
                    '<h2><a class="article-title" href="#">' + json.title + '</a></h2>' +
                    '<p class="article-content">' + json.content + '</p>' +
                '</div>' +
            '</article>'
            )
        },
        error: function(xhr,errmsg,err) {
            console.log(xhr.status + ": " + xhr.responseText);
        }

    });
    console.log('hi')
    e.preventDefault();
});

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
                loadChart(rivers[i], 'pop-chart');
                popup.setPosition(event.latLng);
                popup.draw();
            });

            river.addListener('mouseout', function() {
                popup.hide();
            });

            river.addListener('click', function() {
                updateSidebar(rivers[i]);
                activateSidebar();
                loadChart(rivers[i], 'sb-chart');
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