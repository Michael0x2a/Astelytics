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

function formatToBarChartData(question, data) {
    'use strict';
    
    return [{
        key: question,
        values: formatToPieChartData(question, data)
    }];
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

function formatToPieChartData(question, data) {
    'use strict';
    var arr = [];
    var i;
    for (i in data) {
        arr.push({ "label": i, "value": data[i] });
    }
    
    return arr;
}

function makeWordCloud() {
    'use strict';
    var chart = d3.layout.cloud()
        //.words(data)
        .padding(5)
        .rotate(function() { return ~~(Math.random() * 2) * 0; })
        .font("Impact")
        .fontSize(function(d) { return d.size; });
        
    chart.kind = 'word cloud';
    return chart;
}

function updateWordCloud(target, chart, data) {
    'use strict';
    
    d3.select(target).text('');

    var fill = d3.scale.category20();
    function draw(words) {
        d3.select(target)
            .attr("width", 400)
            .attr("height", 300)
          .append("g")
            .attr("transform", "translate(150,150)")
          .selectAll("text")
            .data(words)
          .enter().append("text")
            .style("font-size", function(d) { return d.size + "px"; })
            .style("font-family", "Impact")
            .style("fill", function(d, i) { return fill(i); })
            .attr("text-anchor", "middle")
            .attr("transform", function(d) {
              return "translate(" + [d.x, d.y] + ")rotate(" + d.rotate + ")";
            })
            .text(function(d) { return d.text; });
    }
            
    chart = chart
        .words(data)
        .on("end", draw)
        .start();    
        
    return chart
}

function formatToWordCloudData(target, data) {
    return data.map(function (t) { 
        return {
            "text": t[0],
            "size": 10 + t[1] * 10
        };
    });
}

function updateChart(target, chart, data) {
    'use strict';
    
    if (chart.kind === 'word cloud') {
        var temp = data.map(function (x) { return x[0] + x[1]}).join();;
        if (chart.previous !== temp) {
            updateWordCloud(target, chart, data);
            
            chart.previous = temp;
        }
        return chart;
    }
    
    d3.select(target)
        .datum(data)
        .transition().duration(500)
        .call(chart);
        
    return chart;
}

function setChartUpdate() {
    'use strict';
    
    var mapping = {
        'bar': [makeBarChart, formatToBarChartData],
        'pie': [makePieChart, formatToPieChartData],
        'text': [makeWordCloud, formatToWordCloudData]
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
                //alert(textStatus + " | " + errorThrown);
            }
        });
    }, 500);
}