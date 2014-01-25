function makeBarChart() {
    'use strict';
    
    var chart = nv.models.discreteBarChart()
        .x(function (d) { return d.label; })
        .y(function (d) { return d.value; })
        .staggerLabels(false)
        .tooltips(true)
        .showValues(true);
        
    nv.utils.windowResize(chart.update);
    nv.addGraph(chart);
    
    return chart;
}

function makePieChart() {
    'use strict';
    
    var chart = nv.models.pieChart()
        .x(function (d) { return d.label; })
        .y(function (d) { return d.value; })
        .showLabels(true);
        
    nv.utils.windowResize(chart.update);
    nv.addGraph(chart);
    
    return chart;
}

function updateChart(target, chart, data) {
    'use strict';
    
    d3.select(target)
        .datum(data)
        .transition().duration(500)
        .call(chart);
        
    return chart;
}

function formatToBarChartData(question, data) {
    'use strict';
    
    return [{
        key: question,
        values: formatToPieChartData(question, data)
    }];
}

function formatToPieChartData(question, data) {
    'use strict';
    var arr = [];
    var i;
    for (i in data) {
        arr.push({ "label": i, "value": data[i] });
    }
    
    return arr;
}

function setChartUpdate() {
    'use strict';
    
    var mapping = {
        'bar': [makeBarChart, formatToBarChartData],
        'pie': [makePieChart, formatToPieChartData]
    };
    
    
    var charts = {};
    
    $('.response').each(function (index, elem) {
        var chartType = $(elem).attr('class').split(' ')[1];
        var chart = mapping[chartType][0]();
        
        charts[$(elem).attr('id')] = chart;
    });
    
    setInterval(function() {
        $.ajax({
            url: 'http://localhost:5000/survey/1/analytics', 
            dataType: "json",
            success: function(json) {
                var question;
                for (question in json) {
                    var response = json[question];
                    var formatter = mapping[response['display']['default']][1];
                    var formatted = formatter(question, response['data']);
                    
                    var unique_id = response['unique-id'];
                    updateChart('#' + unique_id + ' svg', charts[unique_id], formatted);
                }
            },
            error: function(jqXHR, textStatus, errorThrown) {
                alert(textStatus + " | " + errorThrown);
            }
        });
    }, 500);
}