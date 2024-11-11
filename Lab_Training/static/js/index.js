$.ajaxSetup({
    headers: { 'X-CSRFToken': csrf_token },
    type: 'POST',
});

$(document).ready(function(){

    figure_one();
    $("#start-date").datepicker({
        dateFormat: "yy-mm-dd",
        onSelect: function(dateText) {
            $("#start-date").val(dateText);
        }
    });

    $("#end-date").datepicker({
        dateFormat: "yy-mm-dd",
        onSelect: function(dateText) {
            $("#end-date").val(dateText);
        }
    });

    // Date picker button click events
    $("#start-date-picker").click(function() {
        $("#start-date").datepicker("show");
    });

    $("#end-date-picker").click(function() {
        $("#end-date").datepicker("show");
    });

    $('#submit').click(function(){
        $.ajax({
            headers: { 'X-CSRFToken': window.csrf_token },
            type: 'POST',
            url: '/web_tool/ajax_data/', 
            data: {
                'action': 'search_stock',
                'name': $('input[name="stock_id"]').val(), //讀取html輸入框
                'sub_name': $('input[name="sub_stock_id"]').val(), //讀取html輸入框
                'start_day':$('#start-date').val(),
                'end_day':$('#end-date').val(),
            },
            // data: $('#ajax_form').serialize(),
            success: function(response){ 
                $("#message").html('<div class="alert alert-warning">' + response.message + '</div>');
                console.log(response.stock_name);

                //三角
                figure_two(response.data_stock, response.stock_name, response.stock_name_red, response.stock_name_green, response.sub_stock_name_red, response.sub_stock_name_green);

                //損益
                render_profit_loss_graph(
                    "profit_loss_plot",
                    response.pl_daily_profits,
                    response.pl_total_values,
                    response.pl_entry_point,
                    response.pl_exit_point,
                );

                //布林帶
                render_bands_graph(
                    "bollinger_bands_plot",
                    response.spread,
                    response.middle_line,
                    response.upper_line,
                    response.lower_line,
                    response.bands_signals_sell,
                    response.bands_signals_buy
                );

                //DataTable
                $("#buy_sell_table").DataTable({
                    autoWidth: false,
                    bDestroy: true,
                    searching: false,
                    lengthMenu: [
                      [5, 10, 20, -1],
                      [5, 10, 20, "All"],
                    ],
                    data: response.table_signals,
                    columns: [
                      { data: "date", title: "date" },
                      { data: "type", title: "signal" },
                      { data: "stock_name_action", title: `signal of ${response.stock_name[0]}` },
                      { data: "stock_name_price", title: `price of ${response.stock_name[0]}` },
                      { data: "sub_stock_name_action", title: `signal of ${response.stock_name[1]}` },
                      { data: "sub_stock_name_price", title: `price of ${response.stock_name[1]}` },
                    ],
                    // columnDefs: [
                    //   {
                    //     targets: [2, 3],
                    //     createdCell: function (td, cellData, rowData, row, col) {
                    //       $(td).css("background-color", "white");
                    //     },
                    //   },
                    //   {
                    //     targets: [4, 5],
                    //     createdCell: function (td, cellData, rowData, row, col) {
                    //       $(td).css("background-color", "lightgray");
                    //     },
                    //   },
                    // ],
                    fnRowCallback: function (nRow, aData) {
                      if (aData["type"] == "Open") {
                        $(nRow).find("td:eq(0)").css("background-color", "white");
                        $(nRow).find("td:eq(1)").css("background-color", "white");
                        $(nRow).find("td:eq(2)").css("background-color", "white");
                        $(nRow).find("td:eq(3)").css("background-color", "white");
                        $(nRow).find("td:eq(4)").css("background-color", "white");
                        $(nRow).find("td:eq(5)").css("background-color", "white");
                      } else {
                        $(nRow).find("td:eq(0)").css("background-color", "lightgray");
                        $(nRow).find("td:eq(1)").css("background-color", "lightgray");
                        $(nRow).find("td:eq(2)").css("background-color", "lightgray");
                        $(nRow).find("td:eq(3)").css("background-color", "lightgray");
                        $(nRow).find("td:eq(4)").css("background-color", "lightgray");
                        $(nRow).find("td:eq(5)").css("background-color", "lightgray");
                      }
                    },
                  });
        
                  $("#profit_loss_table").DataTable({
                    autoWidth: false,
                    bDestroy: true,
                    searching: false,
                    lengthMenu: [
                      [5, 10, 20, -1],
                      [5, 10, 20, "All"],
                    ],
                    data: response.exe_table_signals,
                    columns: [
                      { data: "date", title: "date" },
                      { data: "type", title: "signal" },
                      { data: "stock_name_action", title: `signal of ${response.stock_name[0]}` },
                      { data: "stock_name_price", title: `price of ${response.stock_name[0]}` },
                      { data: "sub_stock_name_action", title: `signal of ${response.stock_name[1]}` },
                      { data: "sub_stock_name_price", title: `price of ${response.stock_name[1]}` },
                      { data: "percentage", title: ` profit_loss (%)` },
                    ],
                    // columnDefs: [
                    //   {
                    //     targets: [2, 3],
                    //     createdCell: function (td, cellData, rowData, row, col) {
                    //       $(td).css("background-color", "white");
                    //     },
                    //   },
                    //   {
                    //     targets: [4, 5],
                    //     createdCell: function (td, cellData, rowData, row, col) {
                    //       $(td).css("background-color", "lightgray");
                    //     },
                    //   },
                    // ],
                    fnRowCallback: function (nRow, aData) {
                      if (aData["type"] == "Open") {
                        $(nRow).find("td:eq(0)").css("background-color", "white");
                        $(nRow).find("td:eq(1)").css("background-color", "white");
                        $(nRow).find("td:eq(2)").css("background-color", "white");
                        $(nRow).find("td:eq(3)").css("background-color", "white");
                        $(nRow).find("td:eq(4)").css("background-color", "white");
                        $(nRow).find("td:eq(5)").css("background-color", "white");
                      } else {
                        $(nRow).find("td:eq(0)").css("background-color", "lightgray");
                        $(nRow).find("td:eq(1)").css("background-color", "lightgray");
                        $(nRow).find("td:eq(2)").css("background-color", "lightgray");
                        $(nRow).find("td:eq(3)").css("background-color", "lightgray");
                        $(nRow).find("td:eq(4)").css("background-color", "lightgray");
                        $(nRow).find("td:eq(5)").css("background-color", "lightgray");
                        $(nRow).find("td:eq(6)").css("background-color", "lightgray");
                      }
                    },
                  });

            },
            error: function(){
                alert('Something error11');
            },
        });
    });
});

function figure_one(){
    var obj1 = {

        title: {
            text: 'U.S Solar Employment Growth',
            align: 'left'
        },
    
        subtitle: {
            text: 'By Job Category. Source: <a href="https://irecusa.org/programs/solar-jobs-census/" target="_blank">IREC</a>.',
            align: 'left'
        },
    
        yAxis: {
            title: {
                text: 'Number of Employees'
            }
        },
    
        xAxis: {
            accessibility: {
                rangeDescription: 'Range: 2010 to 2022'
            }
        },
    
        legend: {
            layout: 'vertical',
            align: 'right',
            verticalAlign: 'middle'
        },
    
        plotOptions: {
            series: {
                label: {
                    connectorAllowed: false
                },
                pointStart: 2010
            }
        },
    
        series: [{
            name: 'Installation & Developers',
            data: [
                43934, 48656, 65165, 81827, 112143, 142383,
                171533, 165174, 155157, 161454, 154610, 168960, 171558
            ]
        }, {
            name: 'Manufacturing',
            data: [
                24916, 37941, 29742, 29851, 32490, 30282,
                38121, 36885, 33726, 34243, 31050, 33099, 33473
            ]
        }, {
            name: 'Sales & Distribution',
            data: [
                11744, 30000, 16005, 19771, 20185, 24377,
                32147, 30912, 29243, 29213, 25663, 28978, 30618
            ]
        }, {
            name: 'Operations & Maintenance',
            data: [
                null, null, null, null, null, null, null,
                null, 11164, 11218, 10077, 12530, 16585
            ]
        }, {
            name: 'Other',
            data: [
                21908, 5548, 8105, 11248, 8989, 11816, 18274,
                17300, 13053, 11906, 10073, 11471, 11648
            ]
        }],
    
        responsive: {
            rules: [{
                condition: {
                    maxWidth: 500
                },
                chartOptions: {
                    legend: {
                        layout: 'horizontal',
                        align: 'center',
                        verticalAlign: 'bottom'
                    }
                }
            }]
        }
    
    };
    Highcharts.chart('figure_one',obj1);
}

function figure_two(data_stock, stock_name, stock_name_red, stock_name_green, sub_stock_name_red, sub_stock_name_green){
    (async () => {
        // const data = await fetch(
        //     'https://demo-live-data.highcharts.com/aapl-c.json'
        // ).then(response => response.json());
        Highcharts.stockChart('figure_two', {
            rangeSelector: {
                selected: 1
            },
    
            title: {
                text: 'Stock Price & entry point(進出場)'
            },
            
            xAxis: {
                min: Date.UTC(2021, 1, 1), // 自定义开始日期（例如：2022年1月1日）
                max: Date.UTC(2024, 1, 1) // 自定义结束日期（例如：2023年12月31日）
            },

            series: [
                {
                    name: stock_name[0],
                    data: data_stock[0],  //stock_name
                    lineWidth: 2,
                    dashStyle: 'Solid',
                    shadow: {
                        color: 'rgba(0, 0, 0, 0.6)', // 设置阴影颜色
                        offsetX: 2, // 阴影水平偏移
                        offsetY: 2, // 阴影垂直偏移
                        opacity: 0.5 // 阴影透明度
                    },
                    marker: {
                        fillColor: 'white', // 设置标记填充颜色
                        lineColor: 'black', // 设置标记边框颜色
                        lineWidth: 1, // 设置标记边框宽度
                        states: {
                            // 鼠标悬停状态
                            hover: {
                                enabled: true, // 启用悬停效果
                            },
                        }
                    },
                },
                {
                    name: stock_name[1],
                    data: data_stock[1],  //sub_stock_name
                    lineWidth: 2,
                    dashStyle: 'Solid',
                    shadow: {
                        color: 'rgba(0, 0, 0, 0.6)', // 设置阴影颜色
                        offsetX: 2, // 阴影水平偏移
                        offsetY: 2, // 阴影垂直偏移
                        opacity: 0.5 // 阴影透明度
                    },
                    marker: {
                        fillColor: 'white', // 设置标记填充颜色
                        lineColor: 'black', // 设置标记边框颜色
                        lineWidth: 1 ,// 设置标记边框宽度
                        states: {
                            // 鼠标悬停状态
                            hover: {
                                enabled: true, // 启用悬停效果
                            },
                        }
                    },
                },
                {
                    type: 'scatter',
                    name: 'Sell Signal',
                    data: stock_name_red, // 只为 Stock A
                    marker: {
                        symbol: 'triangle-down',
                        fillColor: 'red',
                        lineColor: 'red',
                        lineWidth: 2,
                        radius: 6,
                    },
                    visible: true,
                },
                {
                    type: 'scatter',
                    name: 'Buy Signal',
                    data: stock_name_green,
                    marker: {
                        symbol: 'triangle',
                        fillColor: 'green',
                        lineColor: 'green',
                        lineWidth: 2,
                        radius: 6,
                    },
                    visible: true,
                },
                {
                    type: 'scatter',
                    name: 'Sell Signal',
                    data: sub_stock_name_red, // 只为 Stock B
                    marker: {
                        symbol: 'triangle-down',
                        fillColor: 'red',
                        lineColor: 'red',
                        lineWidth: 2,
                        radius: 6,
                    },
                    visible: true,
                },
                {
                    type: 'scatter',
                    name: 'Sell Signal',
                    data: sub_stock_name_green, // 只为 Stock B
                    marker: {
                        symbol: 'triangle',
                        fillColor: 'green',
                        lineColor: 'green',
                        lineWidth: 2,
                        radius: 6,
                    },
                    visible: true,
                },
            ]
        });
    })();
}

function render_profit_loss_graph(
    container,
    daily_profits,
    total_values,
    entry_point,
    exit_point,
  ){
    // set the allowed units for data grouping
    groupingUnits = [
        [
            "week", // unit name
            [1], // allowed multiples
        ],
        ["month", [1, 2, 3, 4, 6]],
        ];
    
        var obj = {
            rangeSelector: {
                selected: 5,
            },
        
            title: {
                text: "Profits & Loss(損益圖)",
            },
        
            xAxis: {
                gridLineWidth: 1, // 設定x軸網格線的寬度
            },
        
            yAxis: [
                {
                labels: {
                    align: "right",
                    x: -6,
                    formatter: function () {
                        return (this.value).toFixed(2) + '%'; // 將數值轉換為百分比格式
                    }
                },
                title: {
                    text: "percentage",
                },
                top: "0%",
                height: "100%",
                offset: 0,
                lineWidth: 1,
                resize: {
                    enabled: true,
                },
                },
            ],
        
            tooltip: {
                split: true,
            },
        
            series: [
                {
                name: "Daily",
                data: daily_profits,
                color: "darkmagenta",
                lineWidth: 2,
                dataGrouping: {
                    units: groupingUnits,
                },
                shadow: {
                    color: 'rgba(0, 0, 0, 0.6)', // 设置阴影颜色
                    offsetX: 2, // 阴影水平偏移
                    offsetY: 2, // 阴影垂直偏移
                    opacity: 0.5 // 阴影透明度
                },
                marker: {
                    fillColor: 'white', // 设置标记填充颜色
                    lineColor: 'black', // 设置标记边框颜色
                    lineWidth: 1 ,// 设置标记边框宽度
                    states: {
                        // 鼠标悬停状态
                        hover: {
                            enabled: true, // 启用悬停效果
                        },
                    }
                },
                },
                {
                name: "Cash",
                data: total_values,
                color: "RoyalBlue",
                lineWidth: 2,
                dataGrouping: {
                    units: groupingUnits,
                },
                shadow: {
                    color: 'rgba(0, 0, 0, 0.6)', // 设置阴影颜色
                    offsetX: 2, // 阴影水平偏移
                    offsetY: 2, // 阴影垂直偏移
                    opacity: 0.5 // 阴影透明度
                },
                marker: {
                    fillColor: 'white', // 设置标记填充颜色
                    lineColor: 'black', // 设置标记边框颜色
                    lineWidth: 1 ,// 设置标记边框宽度
                    states: {
                        // 鼠标悬停状态
                        hover: {
                            enabled: true, // 启用悬停效果
                        },
                    }
                },
                },
                {
                type: "scatter",
                data: exit_point, // 使用傳遞的數據
                name: "Exit Point",
                marker: {
                    symbol: "circle",
                    fillColor: "green",
                    lineColor: "green",
                    name: "Exit Point",
                    enabled: true,
                    radius: 3,
                },
                visibility: true,
                },
                {
                type: "scatter",
                data: entry_point, // 使用傳遞的數據
                name: "Entry Point",
                marker: {
                    symbol: "circle",
                    fillColor: "brown",
                    lineColor: "brown",
                    name: "Entry Point",
                    enabled: true,
                    radius: 3,
                },
                visibility: true,
                },
            ],
            };
        
            Highcharts.stockChart(container, obj);
}

function render_bands_graph(
    container,
    spread,
    middle_line,
    upper_line,
    lower_line,
    bands_signals_sell,
    bands_singals_buy
  ){
    // set the allowed units for data grouping
    groupingUnits = [
        [
            "week", // unit name
            [1], // allowed multiples
        ],
        ["month", [1, 2, 3, 4, 6]],
        ];
    
        var obj = {
            rangeSelector: {
              selected: 5,
            },
        
            title: {
              text: "Bollinger Bands(布林通道)",
            },
        
            xAxis: {
              gridLineWidth: 1, // 設定x軸網格線的寬度
            },
        
            yAxis: [
              {
                labels: {
                  align: "right",
                  x: -6,
                },
                title: {
                  text: "value",
                },
                top: "0%",
                height: "100%",
                offset: 0,
                lineWidth: 1,
                resize: {
                  enabled: true,
                },
              },
            ],
        
            tooltip: {
              split: true,
            },
        
            series: [
              {
                name: "top",
                data: upper_line,
                color: "purple",
                lineWidth: 1,
                dashStyle: "Dash", // 線條樣式
                dataGrouping: {
                  units: groupingUnits,
                },
                shadow: {
                    color: 'rgba(0, 0, 0, 0.6)', // 设置阴影颜色
                    offsetX: 2, // 阴影水平偏移
                    offsetY: 2, // 阴影垂直偏移
                    opacity: 0.5 // 阴影透明度
                },
                marker: {
                    fillColor: 'white', // 设置标记填充颜色
                    lineColor: 'black', // 设置标记边框颜色
                    lineWidth: 1 ,// 设置标记边框宽度
                    states: {
                        // 鼠标悬停状态
                        hover: {
                            enabled: true, // 启用悬停效果
                        },
                    }
                },
              },
              {
                name: "low",
                data: lower_line,
                color: "gray",
                lineWidth: 1,
                dashStyle: "Dash", // 線條樣式
                dataGrouping: {
                  units: groupingUnits,
                },
                shadow: {
                    color: 'rgba(0, 0, 0, 0.6)', // 设置阴影颜色
                    offsetX: 2, // 阴影水平偏移
                    offsetY: 2, // 阴影垂直偏移
                    opacity: 0.5 // 阴影透明度
                },
                marker: {
                    fillColor: 'white', // 设置标记填充颜色
                    lineColor: 'black', // 设置标记边框颜色
                    lineWidth: 1 ,// 设置标记边框宽度
                    states: {
                        // 鼠标悬停状态
                        hover: {
                            enabled: true, // 启用悬停效果
                        },
                    }
                },
              },
              {
                name: "mid",
                data: middle_line,
                color: "lightblue",
                lineWidth: 1,
                dashStyle: "Dash", // 線條樣式
                dataGrouping: {
                  units: groupingUnits,
                },
                shadow: {
                    color: 'rgba(0, 0, 0, 0.6)', // 设置阴影颜色
                    offsetX: 2, // 阴影水平偏移
                    offsetY: 2, // 阴影垂直偏移
                    opacity: 0.5 // 阴影透明度
                },
                marker: {
                    fillColor: 'white', // 设置标记填充颜色
                    lineColor: 'black', // 设置标记边框颜色
                    lineWidth: 1 ,// 设置标记边框宽度
                    states: {
                        // 鼠标悬停状态
                        hover: {
                            enabled: true, // 启用悬停效果
                        },
                    }
                },
              },
              {
                name: "spread",
                data: spread,
                color: "black",
                lineWidth: 2,
                dataGrouping: {
                  units: groupingUnits,
                },
                shadow: {
                    color: 'rgba(0, 0, 0, 0.6)', // 设置阴影颜色
                    offsetX: 2, // 阴影水平偏移
                    offsetY: 2, // 阴影垂直偏移
                    opacity: 0.5 // 阴影透明度
                },
                marker: {
                    fillColor: 'white', // 设置标记填充颜色
                    lineColor: 'black', // 设置标记边框颜色
                    lineWidth: 1 ,// 设置标记边框宽度
                    states: {
                        // 鼠标悬停状态
                        hover: {
                            enabled: true, // 启用悬停效果
                        },
                    }
                },
              },

              {
                type: "scatter",
                data: bands_singals_buy, // 使用傳遞的數據
                name: "Long",
                marker: {
                  symbol: "triangle",
                  fillColor: "green",
                  lineColor: "green",
                  lineWidth: 2,
                  name: "buy",
                  enabled: true,
                  radius: 6,
                },
                visibility: true,
              },
              {
                type: "scatter",
                data: bands_signals_sell, // 使用傳遞的數據
                name: "Short",
                marker: {
                  symbol: "triangle-down",
                  fillColor: "red",
                  lineColor: "red",
                  lineWidth: 2,
                  name: "sell",
                  enabled: true,
                  radius: 6,
                },
                visibility: true,
              },
            ],
          };
        
          Highcharts.stockChart(container, obj);

}