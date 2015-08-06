$(function () {
    $('#chart-players-country').highcharts({
        chart: {
            type: 'area',
            zoomType: 'x'
        },
        title: {
            text: 'Players on DDNet by Country'
        },
        xAxis: {
            type: 'datetime',
            title: {
                text: 'Date'
            }
        },
        yAxis: {
            title: {
                text: 'Players'
            },
            min: 0
        },
        plotOptions: {
            area: {
                stacking: 'normal'
            },
            line: {
                marker: {
                    radius: 2
                },
                lineWidth: 1,
                states: {
                    hover: {
                        lineWidth: 1
                    }
                },
                threshold: null
            },
            column: {
                animation: false
            }
        },
        tooltip: {
            shared: true,
            formatter: function () {
                var ind = '<span style="font-size: 75%%">' + Highcharts.dateFormat('%%A, %%b %%e, %%H:%%M', this.x) + '</span><br>',
                    sum = 0;

                $.each(this.points, function (i, point) {
                    ind += '<span style="color:' + point.series.color + '">\u25CF</span> ' + point.series.name + ': <b>' + point.y + '</b><br/>';
                });

                ind += '<br/>Total: <b>' + this.points[0].total + '</b>'

                console.log(this);
                return ind;
            }
        },
        series: [%s]
    });
    $('#chart-players-mod').highcharts({
        chart: {
            type: 'area',
            zoomType: 'x'
        },
        title: {
            text: 'Players on DDNet by Mod'
        },
        xAxis: {
            type: 'datetime',
            title: {
                text: 'Date'
            }
        },
        yAxis: {
            title: {
                text: 'Players'
            },
            min: 0
        },
        plotOptions: {
            area: {
                stacking: 'normal'
            },
            line: {
                marker: {
                    radius: 2
                },
                lineWidth: 1,
                states: {
                    hover: {
                        lineWidth: 1
                    }
                },
                threshold: null
            },
            column: {
                animation: false
            }
        },
        tooltip: {
            shared: true,
            formatter: function () {
                var ind = '<span style="font-size: 75%%">' + Highcharts.dateFormat('%%A, %%b %%e, %%H:%%M', this.x) + '</span><br>',
                    sum = 0;

                $.each(this.points, function (i, point) {
                    ind += '<span style="color:' + point.series.color + '">\u25CF</span> ' + point.series.name + ': <b>' + point.y + '</b><br/>';
                });

                ind += '<br/>Total: <b>' + this.points[0].total + '</b>'

                console.log(this);
                return ind;
            }
        },
        series: [%s]
    });
    $('#chart-finishes').highcharts({
        chart: {
            type: 'area',
            zoomType: 'x'
        },
        title: {
            text: 'Finishes on DDNet per Day'
        },
        xAxis: {
            type: 'datetime',
            title: {
                text: 'Date'
            }
        },
        yAxis: {
            title: {
                text: 'Finishes'
            },
            min: 0
        },
        tooltip: {
            shared: true
        },
        plotOptions: {
            line: {
                marker: {
                    radius: 2
                },
                lineWidth: 1,
                states: {
                    hover: {
                        lineWidth: 1
                    }
                },
                threshold: null
            },
            column: {
                animation: false
            }
        },
        series: [{
          name: 'Map finishes',
          pointInterval: 24 * 3600 * 1000,
          pointStart: Date.UTC(2013,6,18),
          data: [%s]
        }]
    });
    $('#chart-points-country').highcharts({
        chart: {
            type: 'area',
            zoomType: 'x'
        },
        title: {
            text: 'Points earned per Day by Country'
        },
        xAxis: {
            type: 'datetime',
            title: {
                text: 'Date'
            }
        },
        yAxis: {
            title: {
                text: 'Points'
            },
            min: 0
        },
        plotOptions: {
            area: {
                stacking: 'normal'
            },
            line: {
                marker: {
                    radius: 2
                },
                lineWidth: 1,
                states: {
                    hover: {
                        lineWidth: 1
                    }
                },
                threshold: null
            },
            column: {
                animation: false
            }
        },
        tooltip: {
            shared: true,
            formatter: function () {
                var ind = '<span style="font-size: 75%%">' + Highcharts.dateFormat('%%A, %%b %%e, %%H:%%M', this.x) + '</span><br>',
                    sum = 0;

                $.each(this.points, function (i, point) {
                    ind += '<span style="color:' + point.series.color + '">\u25CF</span> ' + point.series.name + ': <b>' + point.y + '</b><br/>';
                });

                ind += '<br/>Total: <b>' + this.points[0].total + '</b>'

                console.log(this);
                return ind;
            }
        },
        series: [%s]
    });
    $('#chart-points-server').highcharts({
        chart: {
            type: 'area',
            zoomType: 'x'
        },
        title: {
            text: 'Points earned per Day by Server Type'
        },
        xAxis: {
            type: 'datetime',
            title: {
                text: 'Date'
            }
        },
        yAxis: {
            title: {
                text: 'Points'
            },
            min: 0
        },
        plotOptions: {
            area: {
                stacking: 'normal'
            },
            line: {
                marker: {
                    radius: 2
                },
                lineWidth: 1,
                states: {
                    hover: {
                        lineWidth: 1
                    }
                },
                threshold: null
            },
            column: {
                animation: false
            }
        },
        tooltip: {
            shared: true,
            formatter: function () {
                var ind = '<span style="font-size: 75%%">' + Highcharts.dateFormat('%%A, %%b %%e, %%H:%%M', this.x) + '</span><br>',
                    sum = 0;

                $.each(this.points, function (i, point) {
                    ind += '<span style="color:' + point.series.color + '">\u25CF</span> ' + point.series.name + ': <b>' + point.y + '</b><br/>';
                });

                ind += '<br/>Total: <b>' + this.points[0].total + '</b>'

                console.log(this);
                return ind;
            }
        },
        series: [%s]
    });
    $('#chart-maps').highcharts({
        chart: {
            type: 'area',
            zoomType: 'x'
        },
        title: {
            text: 'Map Releases on DDNet by Server Type'
        },
        xAxis: {
            type: 'datetime',
            title: {
                text: 'Date'
            }
        },
        yAxis: {
            title: {
                text: 'Maps'
            },
            min: 0
        },
        tooltip: {
            shared: true
        },
        plotOptions: {
            area: {
                stacking: 'normal'
            },
            line: {
                marker: {
                    radius: 2
                },
                lineWidth: 1,
                states: {
                    hover: {
                        lineWidth: 1
                    }
                },
                threshold: null
            },
            column: {
                animation: false
            }
        },
        tooltip: {
            shared: true,
            formatter: function () {
                var ind = '<span style="font-size: 75%%">' + Highcharts.dateFormat('%%A, %%b %%e, %%H:%%M', this.x) + '</span><br>',
                    sum = 0;

                $.each(this.points, function (i, point) {
                    ind += '<span style="color:' + point.series.color + '">\u25CF</span> ' + point.series.name + ': <b>' + point.y + '</b><br/>';
                });

                ind += '<br/>Total: <b>' + this.points[0].total + '</b>'

                console.log(this);
                return ind;
            }
        },
        series: [%s]
    });
}); 
