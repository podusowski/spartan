var activityCharts = {};

activityCharts.setGlobalSettings = function()
{
    Chart.defaults.global.elements.rectangle.borderColor = 'rgba(207, 74, 8, 0.8)';
    Chart.defaults.global.elements.rectangle.backgroundColor = 'rgba(207, 74, 8, 0.1)';

    Chart.defaults.bar.scales.xAxes[0].categoryPercentage = 0.9;
    Chart.defaults.bar.scales.xAxes[0].barPercentage = 1;

    Chart.defaults.global.elements.line.borderColor = 'rgba(207, 74, 8, 0.8)';
    Chart.defaults.global.elements.line.backgroundColor = 'rgba(207, 74, 8, 0.05)';
    Chart.defaults.global.legend.display = true;
    Chart.defaults.global.legend.position = "right";

    Chart.defaults.global.hover.intersect = false;

    Chart.defaults.global.tooltips.mode = 'index';
    Chart.defaults.global.tooltips.intersect = false;
    Chart.defaults.global.tooltips.multiKeyBackground = 'black';

    Chart.defaults.global.tooltips.filter = function(tooltipItem, data) {
        var label = data.datasets[tooltipItem.datasetIndex].label || '';
        return label.indexOf('AVG') == -1;
    };

    Chart.defaults.global.tooltips.callbacks.title = function(tooltipItem, data) {
        return '';
    };
}

activityCharts.render = function(charts_id, points)
{
    this.setGlobalSettings();

    var isPresent = function(data) {
        return data.length > 0 && data[0] != null;
    };

    var hr_data = points.map(function(point) { return point.hr; });
    var cad_data = points.map(function(point) { return point.cad; });

    var time_data = points.map(function (point)
    {
        var started_time = new Date(points[0].time).getTime();
        var actual_time = new Date(point.time).getTime();
        var delta_time_in_ms = actual_time - started_time;
        const one_minute_in_ms = 1000;

        return delta_time_in_ms / one_minute_in_ms;
    });

    var datasets = [];

    var makeAverage = function(data) {
        sum = data.reduce(function(a, b) { return a + b; });
        avg = sum / data.length;

        result = new Array(data.length);
        result.fill(avg);

        return result;
    };

    var makeDataset = function(data, label, color='rgba(153, 0, 0, 0.8)') {
        return {
            borderColor: color,
            label: label,
            fill: false,
            pointRadius: 0,
            data: data
        };
    };

    if (isPresent(hr_data))
    {
        datasets = datasets.concat([
            makeDataset(hr_data, "HR", 'rgba(153, 0, 0, 0.8)'),
            makeDataset(makeAverage(hr_data), "AVG HR", 'rgba(153, 0, 0, 0.4)')
        ]);
    }

    if (isPresent(cad_data))
    {
        datasets = datasets.concat([
            makeDataset(cad_data, "CADENCE", 'rgba(0, 76, 153, 0.8)'),
            makeDataset(makeAverage(cad_data), "AVG CADENCE", 'rgba(0, 76, 153, 0.4)')
        ]);
    }

    chart = new Chart($(charts_id), {
        type: "line",
        data: {
            labels: time_data,
            datasets: datasets
        },
        options: {
            scales: {
                yAxes: [{
                    gridLines: {
                        color: "rgba(207, 74, 8, 0.1)"
                    },
                    ticks: {
                        beginAtZero: false
                    }
                }],
                xAxes: [{
                    gridLines: {
                        color: "rgba(207, 74, 8, 0.1)"
                    },
                    ticks: {
                        maxTicksLimit: 10,
                        minRotation: 0,
                        maxRotation: 0
                    }
                }]
            }
        }
    });
}

