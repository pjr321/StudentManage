(function($){
        //严格模式
        "use strict";

        // Counter Number
        $('.count').each(function () {
            $(this).prop('Counter',0).animate({
                Counter: $(this).text()
            }, {
                duration: 3000,
                easing: 'swing',
                step: function (now) {
                    $(this).text(Math.ceil(now));
                }
            });
        });


        //widgetChart1
        var ctx = document.getElementById( "widgetChart1" );
        ctx.height = 150;
        var myChart = new Chart( ctx, {
            type: 'line',
            data: {
                labels: ['January', 'February', 'March', 'April', 'May', 'June', 'July'],
                type: 'line',
                datasets: [ {
                    data: [1, 18, 9, 17, 34, 22, 11],
                    label: 'Dataset',
                    backgroundColor: '#63c2de',
                    borderColor: 'rgba(255,255,255,.55)',
                }, ]
            },
            options: {
                maintainAspectRatio: false,
                legend: {
                    display: false
                },
                responsive: true,
                scales: {
                    xAxes: [ {
                        display:false,
                        gridLines: {
                            color: 'transparent',
                            zeroLineColor: 'transparent'
                        },
                        ticks: {
                            fontSize: 2,
                            fontColor: 'transparent'
                        }
                    } ],
                    yAxes: [ {
                        display:false,
                        ticks: {
                            display: false,
                        }
                    } ]
                },
                title: {
                    display: false,
                },
                elements: {
                    line: {
                        tension: 0.00001,
                        borderWidth: 1
                    },
                    point: {
                        radius: 4,
                        hitRadius: 10,
                        hoverRadius: 4
                    }
                }
            }
        } );
    })(jQuery);