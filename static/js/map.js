function activateSidebar () {
    $('#sidebar').addClass('active');
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
            activateSidebar();
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