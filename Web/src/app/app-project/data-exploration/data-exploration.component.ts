import { Component, Input, OnInit, ViewChild } from '@angular/core';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';
import { ToastrService } from 'ngx-toastr';
import { DataExplorationApiService } from '../data-exploration.service';
import { Chart } from 'angular-highcharts';
import * as Highcharts from 'highcharts';
import { DataTableDirective } from 'angular-datatables';

Highcharts.setOptions({
  colors: ['#058DC7', '#50B432', '#ED561B', '#DDDF00', '#24CBE5', '#64E572',
    '#FF9655', '#FFF263', '#6AF9C4'],
  chart: {
    backgroundColor: {
      stops: [
        [0, 'rgb(255, 255, 255)'],
        [1, 'rgb(240, 240, 255)']
      ]
    },
  },
  title: {
    style: {
      display: 'none',
      color: '#fff',
      font: 'bold 16px "Trebuchet MS", Verdana, sans-serif'
    }
  },
  subtitle: {
    style: {
      color: '#fff',
      font: 'bold 12px "Trebuchet MS", Verdana, sans-serif'
    }
  },
  legend: {
    itemStyle: {
      font: '9pt Trebuchet MS, Verdana, sans-serif',
      color: '#fff'
    },
    itemHoverStyle: {
      color: '#fff'
    }
  },
  credits: {
    style: {
      display: 'none'
    }
  },
  xAxis: {
    gridLineColor: '#32394e',
    labels: {
      style: {
        color: '#bfc8e2'
      }
    },
    lineColor: '#32394e',
    minorGridLineColor: '#505053',
    tickColor: '#32394e',
    tickWidth: 1,
  },
  yAxis: {
    gridLineColor: '#32394e',
    labels: {
      style: {
        color: '#bfc8e2'
      }
    },
    lineColor: '#32394e',
    minorGridLineColor: '#505053',
    tickColor: '#707073',
    tickWidth: 0,
  },
});
@Component({
  selector: 'app-data-exploration',
  templateUrl: './data-exploration.component.html',
  styleUrls: ['./data-exploration.component.scss']
})

export class DataExplorationComponent implements OnInit {

  constructor(public apiService: DataExplorationApiService, public toaster: ToastrService, private modalService: NgbModal,) { }
  @ViewChild(DataTableDirective, { static: false })
  datatableElement: DataTableDirective;
  dtOptions: DataTables.Settings = {};
  @Input() public dataset_id: any;
  @Input() public title: any;
  @Input() public project_id: any;
  @Input() public schema_id: any;
  chart: Chart;
  loaderdiv = false;
  displaytitle = "false";
  exploredData: any = [];
  finaldata: any = [];
  columnlabelChart: any;
  columnlabelChartexpand: any;
  boxplotChartexpand: any;
  animation = "progress-dark";
  theme = {
    'border-radius': '5px',
    'height': '40px',
    'background-color': ' rgb(34 39 54)',
    'border': '1px solid #32394e',
    'animation-duration': '20s'
  };
  displayselectedtitle = "Continous";
  displayrightoutliers: any = false;
  displayleftoutliers: any = false;

  ngOnInit(): void {
    this.dtOptions = {
      paging: false,
      ordering: false,
      scrollCollapse: true,
      info: false,
      searching: false,
      
      scrollY: "calc(100vh - 365px)",
    }
    this.loaderdiv = true;
    this.columnlabelChart={
      chart: {
        height: '80px',
         width: '100%',
        type: 'bar',
        offsetX: -25,
        offsetY: -25,
        toolbar: {
          show: false
      },
      selection: {
        enabled: true
      }
      },
      plotOptions: {
        bar: {
          distributed: true
        }
      },
     
      dataLabels: {
            enabled: false
          },
          yaxis: {
            axisBorder: {
              show: false
            },
            axisTicks: {
              show: false,
            },
            labels: {
              show: false,
              formatter: (val) => {
                return val;
              }
            }
          },
          xaxis: {
            axisBorder: {
              show: false
            },
            axisTicks: {
              show: false,
            },
            labels: {
              show: false,
              formatter: (val) => {
                return val;
              }
            }
          },
      legend: {
        show: false
      }

    };
    // this.columnlabelChart = {
    //   chart: {
    //     width: '100%',
    //     type: 'bar',
    //     offsetX: 0,
    //     offsetY: -26,
    //     toolbar: {
    //       show: false
    //     },
    //   },
    //   plotOptions: {
    //     bar: {
    //       distributed: true
    //     }
    //   },
    //   grid: {
    //     xaxis: {
    //       lines: {
    //         show: false
    //       }
    //     },
    //     yaxis: {
    //       lines: {
    //         show: false
    //       }
    //     },
    //     padding: {
    //       left: 0,
    //       right: 0,
    //       top: 0,
    //       bottom: 0
    //     },
    //   },
    //   colors: ['#34c38f'],
    //   dataLabels: {
    //     enabled: false
    //   },
    //   yaxis: {
    //     axisBorder: {
    //       show: false
    //     },
    //     axisTicks: {
    //       show: false,
    //     },
    //     labels: {
    //       show: false,
    //       formatter: (val) => {
    //         return val;
    //       }
    //     }
    //   },
    //   xaxis: {
    //     axisBorder: {
    //       show: false
    //     },
    //     axisTicks: {
    //       show: false,
    //     },
    //     labels: {
    //       show: false,
    //       formatter: (val) => {
    //         return val;
    //       }
    //     }
    //   },
    // };


    this.getExplorationData(this.dataset_id,this.schema_id);
  }

  getExplorationData(datasetid,schemaid) {
    this.apiService.getExplorationData(datasetid,schemaid).subscribe(
      logs => this.successHandler(logs),
      error => this.errorHandler(error)
    )
  }

  continuousexploredata: any;
  categoricalexploredata: any;
  successHandler(logs) {
    if (logs.status_code == "200") {
      this.exploredData = logs.response;
      this.exploredData.forEach(obj => {
        let category: any = [];
    let plotarray: any = [];
    let colorarray: any = [];
    if (obj["Left Outlier Values"][1].length > 0) {
      obj["Left Outlier Values"][0].forEach((element, index) => {
        category.push(element);
        plotarray.push(obj["Left Outlier Values"][1][index]);
        colorarray.push('#f74242')
      });
    }
    obj["Plot Values"][0].forEach((element, index) => {
      category.push(element);
      plotarray.push(obj["Plot Values"][1][index]);
      colorarray.push('#34c38f')
    });
    if (obj["Right Outlier Values"][1].length > 0) {
      obj["Right Outlier Values"][0].forEach((element, index) => {
        category.push(element);
        plotarray.push(obj["Right Outlier Values"][1][index]);
        colorarray.push('#f74242')
      });
    }
obj.category=category;
obj.plotarray=plotarray;
obj.colorarray=colorarray;

      });
console.log(this.exploredData );

      var data = this.groupBy(this.exploredData, "IsinContinuous");
      this.continuousexploredata = data["true"];
      this.categoricalexploredata = data["false"];
      this.loaderdiv = false;
      this.finaldata = logs.response;
    }
    else {
      this.errorHandler(logs)
    }
  }

  groupBy(xs, key) {
    return xs.reduce(function (rv, x) {
      (rv[x[key]] = rv[x[key]] || []).push(x);
      return rv;
    }, {});
  };

  errorHandler(error) {
    this.loaderdiv = false;
    if (error.error_msg)
      this.toaster.error(error.error_msg, 'Error');
    else {
      this.toaster.error('Something went wrong', 'Error');
    }
  }

  modeltitle: any;
  hideboxplot = true;
  modalobj: any;
width="100%";
  centerModal(exlargeModal: any, obj) {
    this.classname="one-box";
    this.modalobj = obj;
    let category: any = [];
    let plotarray: any = [];
    let colorarray: any = [];
    if (obj["Left Outlier Values"][1].length > 0) {
      obj["Left Outlier Values"][0].forEach((element, index) => {
        category.push(element);
        plotarray.push(obj["Left Outlier Values"][1][index]);
        colorarray.push('#f74242')
      });
    }
    obj["Plot Values"][0].forEach((element, index) => {
      category.push(element);
      plotarray.push(obj["Plot Values"][1][index]);
      colorarray.push('#34c38f')
    });
    if (obj["Right Outlier Values"][1].length > 0) {
      obj["Right Outlier Values"][0].forEach((element, index) => {
        category.push(element);
        plotarray.push(obj["Right Outlier Values"][1][index]);
        colorarray.push('#f74242')
      });
    }
    this.modeltitle = obj["Column Name"];
    this.columnlabelChartexpand = {
      chart: {
        height: '500px',
         width: '100%',
        type: 'bar',
      
        toolbar: {
          show: false
      },
      selection: {
        enabled: true
      }
      },
      plotOptions: {
        bar: {
          distributed: true
        }
      },
      dataLabels: {
        enabled: false
      },
      colors: colorarray,
      series: [
        {
          data: plotarray
        }
      ],
      xaxis: {
        categories: category,
        position: 'bottom',
        title: {
          text: 'Histogarm'
        }
      },
      yaxis: {
        categories: plotarray,
        position: 'left',
        labels: {
            show: true,
          align: 'right',
          minWidth: 0,
          maxWidth: 160,
        },
        offsetX: 0,
        offsetY: 0,
  
    },
      legend: {
        show: false
      }

    };

    if (obj["open"] != null) {
      let outliers = [];
      if (obj["Outliers"].length > 0) {
        let leftoutlier = obj["Outliers"];
        leftoutlier.forEach(element => {
          outliers.push([0, element])
        });
      }

      let chart = new Chart({
        chart: {
          type: 'boxplot'
        },
        legend: {
          enabled: false
        },
        xAxis: {
          categories: [obj["Column Name"]],
          title: {
          }
        },
        yAxis: {
          title: {
            text: ''
          }
        },
        exporting: {
          enabled: false
        },
        series: [{
          name: 'Observations',
          type: 'boxplot',
          color: "#34c38f",
          data: [
            [obj["open"], obj["25%"], obj["50%"], obj["75%"], obj["close"]]
          ],
          tooltip: {
            headerFormat: ''
          }
        },
        {
          name: 'Outliers',
          color: "#34c38f",
          type: 'scatter',
          data: outliers,
          marker: {
            fillColor: '#34c38f',
            lineWidth: 1,
            lineColor: "#34c38f"
          },
          tooltip: {
            pointFormat: '{point.y}'
          },
        }]
      });
      this.chart = chart;
      this.hideboxplot = false
    }
    else {
      this.hideboxplot = true;
    }
    
    this.modalService.open(exlargeModal, { size: 'xl', windowClass: 'modal-holder', centered: true });
    setTimeout(() => {
      this.displayleftoutliers =true;
      this.displayrightoutliers =true;
    }, 10);

  }

  classname:any="one-box";
  displayoutliers(id) {
    if (id == "left") {
      this.displayleftoutliers = !this.displayleftoutliers;
    }
    else {
      this.displayrightoutliers = !this.displayrightoutliers;
    }
   if(this.displayleftoutliers && this.displayrightoutliers ){
     this.classname="one-box";
     this.width='100%'
   }
   else if((!this.displayleftoutliers && this.displayrightoutliers )||(this.displayleftoutliers && !this.displayrightoutliers )){
    this.classname="two-box";
    this.width='50%';
   }
   else if(!this.displayleftoutliers && !this.displayrightoutliers ){
    this.classname="three-box";
    this.width="33.3%";
   }

  //  setTimeout(() => {
    window.dispatchEvent(new Event('resize'));
  //  }, 0);
  }


  
}