window.chartColors = {
	red: 'rgb(255, 0, 0)',
	orange: 'rgb(255, 159, 64)',
	yellow: 'rgb(255, 205, 86)',
	green: 'rgb(0, 200, 0)',
	blue: 'rgb(0, 0, 200)',
	cyan: 'rgb(0, 255, 255',
	purple: 'rgb(153, 102, 255)',
	grey: 'rgb(201, 203, 207)'
};

function loadChart(section, canvasId) {

    $('#' + canvasId).remove();
    if (section.observatory_id == undefined) {
        return;
    }
    if (canvasId == 'pop-chart') {
        $('#' + canvasId + '-div').append('<canvas id="' + canvasId + '" height="150"></canvas>');
        aspectRatio = true;
    } else if (canvasId == 'chart') {
        $('#' + canvasId + '-div').append('<canvas id="' + canvasId + '" height="300"></canvas>');
        aspectRatio = false;
    } else {
        $('#' + canvasId + '-div').append('<canvas id="' + canvasId + '" height="300"></canvas>');
        aspectRatio = true;
    }

    $.getJSON("/static/js/data/river/" + section.observatory_id + ".json", {_: new Date().getTime()}, function(json){
        data = json.level;

        xData = [];
        yData = [];
        lwData = [];
        mwData = [];
        hwData = [];
        graphData = [];
        if (canvasId == 'pop-chart') {
            var i = data.length / 2;
        } else {
            var i = 0;
        }
        for (i; i < data.length; i++) {
            point = data[i];
            if (canvasId == 'pop-chart') {
                xData.push(point.time);
            } else {
                xData.push(point.date + ", " + point.time);
            }
            yData.push(point.level);
            if (section.low_water != null){
                lwData.push(section.low_water);
            }
            if (section.middle_water != null){
                mwData.push(section.middle_water);
            }
            if (section.high_water != null){
                hwData.push(section.high_water);
            }
        }

        var index = -1, resIndex = -1, values = [];
        while(++index < yData.length){
            var value = yData[index];
            if (!(isNaN(value))) {
                values[++resIndex] = value;
            }
        }
        minLevel = Math.min.apply(null, values);
        maxLevel = Math.max.apply(null, values);
        buffer = (maxLevel - minLevel)*0.5;
        minLevel = minLevel - buffer;
        maxLevel = maxLevel + buffer;

        if ((minLevel > section.low_water)||(maxLevel < section.low_water)){
            lwData = [];
        }
        if ((minLevel > section.middle_water)||(maxLevel < section.middle_water)){
            mwData = [];
        }
        if ((minLevel > section.high_water)||(maxLevel < section.high_water)){
            hwData = [];
        }

        var lineChartData = {
            labels: xData,
            datasets: [{
                label: 'Water Level',
                borderColor: window.chartColors.blue,
                backgroundColor: window.chartColors.black,
                fill: false,
                data: yData,
                yAxisID: 'y-axis-1',
                lineTension: 0.4,
                spanGaps: true,
            }, {
                borderColor: window.chartColors.cyan,
                data: lwData,
                pointRadius: 0,
                fill: false,
            }, {
                borderColor: window.chartColors.green,
                data: mwData,
                pointRadius: 0,
                fill: false,
            }, {
                borderColor: window.chartColors.red,
                data: hwData,
                pointRadius: 0,
                fill: false,
            }]
        };

        var ctx = $('#' + canvasId);
        window.myLine = Chart.Line(ctx, {
            data: lineChartData,
            options: {
                responsive: true,
                maintainAspectRatio: aspectRatio,
                hoverMode: 'index',
                stacked: false,
                title: {
                    display: false,
                    text: 'Chart.js Line Chart - Multi Axis'
                },
                scales: {
                    yAxes: [{
                        type: 'linear',
                        display: true,
                        position: 'left',
                        id: 'y-axis-1',
                    }],
                },
                hover: {
                    mode: 'nearest',
                    axis: 'y',
                    animationDuration: 200
                },
                legend: {
                    display: false
                }
            }
        });
    });
};