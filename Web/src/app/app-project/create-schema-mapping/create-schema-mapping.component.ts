import { Component, HostListener, Input, OnInit, ViewChild } from '@angular/core';
import { Router } from '@angular/router';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';
import { DataTableDirective } from 'angular-datatables';
import { ToastrService } from 'ngx-toastr';
import { Subject } from 'rxjs';

import { SchemaMappingApiService } from '../schema-mapping-api.service';
@Component({
  selector: 'app-create-schema-mapping',
  templateUrl: './create-schema-mapping.component.html',
  styleUrls: ['./create-schema-mapping.component.scss']
})
export class CreateSchemaMappingComponent implements OnInit {
  @ViewChild(DataTableDirective, { static: false })
  datatableElement: DataTableDirective;
  dtOptions: DataTables.Settings = {};
  dtTrigger: Subject<any> = new Subject<any>();
  targetColumn: any = 0;
  constructor(public apiService: SchemaMappingApiService, public router: Router, public toaster: ToastrService, private modalService: NgbModal) { }
  @Input() public dataset_id: any;
  @Input() public title: any;
  @Input() public project_id: any;
  @Input() public schema_id: any;
  @Input() public project_name: any;
  loaderdiv = false;
  saveAs: any = {
    isPrivate: false,
    dataset_name: "",
    description: ""
  }
  selectdatetimeoption = "";
  filter: boolean = true;
  displaytitle = "false";
  columnattrList: any = [];
  datatypeList: any = [];
  datetimeoptionList: any = [];
  datasetSchema: any = [];
  Originaldata: any = [];
  displaydiv = false;
  animation = "progress-dark";
  dagsStatusRunning = false;
  theme = {
    'border-radius': '5px',
    'height': '40px',
    'background-color': ' rgb(34 39 54)',
    'border': '1px solid #32394e',
    'animation-duration': '20s'
  };

  @HostListener('window:resize', ['$event'])
  onResize(event) {
    if (this.datatableElement.dtInstance) {
      this.datatableElement.dtInstance.then((dtInstance: DataTables.Api) => {
        dtInstance.columns.adjust().draw();
      })
    }
  }

  checkuniquecolumnname(event, id) {
    if (event.target.value != "") {
      this.apiService.checkuniqueColumnName(event.target.value, this.schema_id).subscribe(
        logs => this.checkuniquesuccessHandler(logs, id),
        error => this.errorHandler(error)
      )
    }
    else {
      $("#td_" + id).removeClass("errorstatus");
      $(".changeerror_" + id).text('');
    }
  }

  checkuniquesuccessHandler(data, id) {
    if (data.status_code == '500') {
      $("#td_" + id).addClass("errorstatus");
      $(".changeerror_" + id).text(data.error_msg);
    }
    else {
      $("#td_" + id).removeClass("errorstatus");
      $(".changeerror_" + id).text('');
    }
  }

  ngOnInit(): void {
    this.dtOptions = {
      paging: false,
      scrollCollapse: true,
      info: false,
      scrollX: true,
      scrollY: "calc(100vh - 450px)",
    }
    this.displaydiv = true;
    this.getAllDagsStatus();
    this.getColumnAttributeList();
    this.getSchema(this.project_id, this.dataset_id, this.schema_id);
  }

  getAllDagsStatus() {
    this.apiService.getAllDagsStatus(this.project_id).subscribe(
      logs => this.dagsSuccessHandler(logs),
      error => this.errorHandler(error)
    )
  }

  dagsSuccessHandler(data) {
    if (data.status_code == "200") {
      if (data.response.cleanup_dag == 'True' || data.response.modeling_dag == 'True' || data.response.feature_dag == 'True') {
        this.dagsStatusRunning = true;
      }
    }
    else {
      this.errorHandler(data);
    }
  }

  getSchema(projectid, datasetid, schemaid) {
    this.apiService.getDatasetSchema(projectid, datasetid, schemaid).subscribe(
      logs => this.successHandler(logs),
      error => this.errorHandler(error)
    )
  }

  successHandler(logs) {
    this.datasetSchema = logs.response.data;
    this.Originaldata = logs.response.data;
    if(logs.response.feature_selection!=null){
      this.isFeatureSelected=true;
      this.selectedFeature=logs.response.feature_selection;
    }
    setTimeout(() => {
      if (!this.datatableElement.dtInstance) {
        this.dtTrigger.next();
        this.datatableElement.dtInstance.then((dtInstance: DataTables.Api) => {
          dtInstance.columns().every(function () {
            const that = this;
            $('#input_' + this.index("visible")).on('keyup change', function () {
              console.log(this['value']);
              if (that.search() !== this['value']) {
                that
                  .search(this['value'])
                  .draw();
              }
            });
          });
        });
      }
      if ($("tbody").find('.Target-selected').length > 0) {
        console.log("target column exist");
        this.targetColumn = 1;
        console.log(this.targetColumn);
      }
    }, 0);
    this.displaydiv = false;
  }

  isitemselected = false;
  selecteditem: any;
  selectedOption(item, i) {
    $(".featureoptios").removeClass('selected');
    $("#option_" + i).addClass("selected");
    this.selecteditem = item;
    this.isitemselected = true;
  }

  canceloption() {
    this.isitemselected = false;
    this.selecteditem = undefined;
  }

  isFeatureSelected = false;
  selectedFeature = "";
  saveoption() {
    this.isFeatureSelected = false;
    this.selectedFeature = "";
    if (this.selecteditem) {
      this.selectedFeature = this.selecteditem.name;
      this.datasetSchema.forEach((element, index) => {
        var data = this.selecteditem.column[element.column_name];
        console.log(element);
        console.log(data);
        if (data == "True") {
          $("#selectattr_" + index).val('Select')
        }
        // element.column_attribute='Select';
        if (data == "False") {
          $("#selectattr_" + index).val('Ignore')
        }
        // element.column_attribute='Ignore';
        this.isFeatureSelected = true;
      });
      this.modalService.dismissAll();
    }
    else {
      this.isitemselected = false;
      this.selecteditem = undefined;
    }
  }

  getColumnAttributeList() {
    this.apiService.getColumnAttributes().subscribe(
      logs => this.columnattributesSuccessHandler(logs),
      error => this.errorHandler(error)
    )
  }

  // getDataTypeList() {
  //   this.apiService.getDatatypeList().subscribe(
  //     logs => this.DatatypeSuccessHandler(logs),
  //     error => this.errorHandler(error)
  //   )
  // }

  // DatatypeSuccessHandler(data) {
  //   this.datatypeList = data.response.attribute_name;
  // }

  currentmodelId: any;
  DatatypeModal(dateModal: any, item, i) {
    console.log(item);
    this.currentmodelId = i;
    $("#datetimeformattooltip_" + i).prop("hidden", true);

    if (item == "timestamp")
      this.modalService.open(dateModal, { size: 'sm', windowClass: 'modal-holder', centered: true });
  }

  savetimestamp() {
    console.log(this.currentmodelId);
    console.log(this.selectdatetimeoption);
    if (this.selectdatetimeoption != "") {
      if (this.selectdatetimeoption != 'Custom') {
        $("#datetimeformat_" + this.currentmodelId).val(this.selectdatetimeoption);
        $("#datetimeformattooltip_" + this.currentmodelId).prop("hidden", false);
        this.currentmodelId = '';
        this.selectdatetimeoption = '';
        this.modalService.dismissAll();
      }
      else {
        var format = $("#custome-dateformate").val();
        if (format != "") {
          $("#datetimeformat_" + this.currentmodelId).val(format);
          $("#datetimeformattooltip_" + this.currentmodelId).prop("hidden", false);
          this.currentmodelId = '';
          this.selectdatetimeoption = '';
          this.modalService.dismissAll();
        }
        else {
          this.toaster.error("Please enter custom datetime format", "Error");
        }
      }
    }
    else {
      this.toaster.error("Please select any datetime format", "Error");
    }


  }

  featuresList: any;
  getFeatureSelection(schemarecommodate) {
    // var target=$('.Target-selected').prop('id').split('_')[1];
    // var target_col=$('.columnname_'+target).prop('id').split('_')[1];
    this.apiService.getfeatureSelection(this.dataset_id, this.schema_id, this.targetColumnName).subscribe(
      logs => this.SuccessFeatureSelection(logs, schemarecommodate),
      error => this.errorHandler(error)
    )
  }

  SuccessFeatureSelection(data, schemarecommodate) {
    if (data.status_code == "200" && this.startfeatureslection == true) {
      if (data.response != false) {
        this.featuresList = data.response;
        console.log(this.featuresList);
        this.displayselection = false;
        this.modalService.open(schemarecommodate, { size: 'xl', windowClass: 'modal-holder', centered: true });
        this.startfeatureslection = false;
        if (this.setFeatureSelectionInterval) {
          clearInterval(this.setFeatureSelectionInterval);
          this.setFeatureSelectionInterval = undefined;
        }
      }
      else {
        if (!this.setFeatureSelectionInterval) {
          this.startFeatureSelectionDags(schemarecommodate);
        }
      }
    }
    else {
      this.errorHandler(data);
    }
  }


  startFeatureSelectionDags(schemarecommodate) {
    this.apiService.startFeatureSelection(this.dataset_id, this.schema_id, this.targetColumnName, this.project_id).subscribe(
      logs => this.startSuccessHandlers(logs, schemarecommodate),
      error => this.errorHandler(error)
    )
  }

  setFeatureSelectionInterval: any;
  startSuccessHandlers(data, schemarecommodate) {
    if (data.status_code == "200") {
      this.setFeatureSelectionInterval = setInterval(() => {
        this.getFeatureSelection(schemarecommodate);
      }, 10000);
    }
    else {
      this.errorHandler(data);
    }
  }


  currentcontet = "";
  displaytooltip(tooltip, id) {
    this.currentcontet = $("#datetimeformat_" + id).val().toString();
    tooltip.open();
  }

  hidetooltip(tooltip) {
    tooltip.close();
  }

  columnattributesSuccessHandler(data) {
    this.columnattrList = data.response.column_attribute;
    this.datatypeList = data.response.datatype;
    this.datetimeoptionList = data.response.datetime_options;

  }

  errorHandler(error) {
    this.loaderdiv = false;
    if (error.error_msg)
      this.toaster.error(error.error_msg, 'Error');
    else {
      this.toaster.error('Something went wrong', 'Error');
    }
  }

  save() {
    if ($(".schema-mapping").find(".errorstatus").length > 0) {
      this.toaster.error('Please enter valid input', 'Error');
    }
    else {
      let savedata = [];
      this.loaderdiv = true;
      this.datasetSchema.forEach((element, index) => {
        var txt_column_name = $("#columnname_" + index).val();
        var txt_column_attribute = $("#selectattr_" + index + " :selected").val();
        var txt_datatype = $("#selectdatatype_" + index + " :selected").val();

        if(txt_column_name!=undefined && txt_column_attribute!=undefined && txt_datatype!=undefined){
          txt_column_name = txt_column_name == undefined ? '' : txt_column_name.toString();
          txt_column_attribute = txt_column_attribute == undefined ? '' : txt_column_attribute.toString();
          txt_datatype = txt_datatype == undefined ? '' : txt_datatype.toString();
          var date_format = $("#datetimeformat_" + index).val();
          date_format = date_format == undefined ? '' : date_format.toString();

        if (txt_column_name == this.Originaldata[index].change_column_name && txt_column_attribute == this.Originaldata[index].column_attribute && txt_datatype == this.Originaldata[index].data_type) {
        }
        else {
          if (txt_column_name != element.column_name) {
            if (txt_datatype == 'timestamp' && date_format == '') {
              this.toaster.error('Please select any datetime format', 'Error');
            }
            else {
              var schema = {
                change_column_name: txt_column_name,
                index: element.index,
                column_name: element.column_name,
                data_type: txt_datatype,
                date_format: date_format,
                column_attribute: txt_column_attribute
              }
              savedata.push(schema);
            }
          }
        }
      }
      });
      if (savedata.length > 0) {
        savedata.push(this.datasetSchema[0]);

        console.log(savedata);
        this.loaderdiv = false;

        this.apiService.saveDatasetSchema(this.dataset_id, this.project_id, this.schema_id, this.selectedFeature, { data: savedata }).subscribe(logs => this.savesuccessHandler(logs), error => this.errorHandler(error));

      } else {
        this.loaderdiv = false;
        this.toaster.error('Please enter valid input', 'Error');

      }
    }
  }

  // savaAs() {
  //   if ($(".schema-mapping").find(".errorstatus").length > 0) {
  //     this.toaster.error('Please enter valid input', 'Error');
  //   }
  //   else {
  //     this.loaderdiv = true;
  //     let savedata = [];
  //     this.datasetSchema.forEach((element, index) => {
  //       var txt_column_name = $("#columnname_" + index).val().toString();
  //       var txt_column_attribute = $("#selectattr_" + index + " :selected").val().toString();
  //       // if(txt_column_name=="" && txt_column_attribute==""){
  //       // }
  //       // else{
  //       //   if(txt_column_name!=element.column_name){
  //       var schema = {
  //         change_column_name: txt_column_name,
  //         column_name: element.column_name,
  //         data_type: element.data_type,
  //         column_attribute: txt_column_attribute
  //       }
  //       savedata.push(schema);
  //       //   }
  //       // }
  //     });
  //     // console.log(this.saveAs);
  //     this.apiService.saveasDatasetSchema(this.project_id, this.saveAs.dataset_name, this.saveAs.description, this.saveAs.isPrivate, "Save as", { data: savedata }).subscribe(logs => this.savesuccessHandler(logs), error => this.errorHandler(error));
  //   }
  // }

  savesuccessHandler(data) {
    this.loaderdiv = false;
    if (data.status_code == "200") {
      this.toaster.success(data.error_msg, "Success");
      this.reset();
    }
    else
      this.errorHandler(data);
  }

  reset() {
    let currentUrl = this.router.url;
    this.router.routeReuseStrategy.shouldReuseRoute = () => false;
    this.router.onSameUrlNavigation = 'reload';
    this.router.navigate([currentUrl]);

  }

  changeattrinute(value, i) {
    $("#tr_" + i).removeClass("Target-selected");
    if (value == "Target") {
      $("#tr_" + i).addClass("Target-selected");
    }
    if ($("tbody").find('.Target-selected').length > 0) {
      this.targetColumn = 1;
    }
    else {
      this.targetColumn = 0;
    }
  }

  checksame(columnname, newname, index) {
    $("#td_" + index).removeClass("errorstatus");
    if (columnname == newname)
      $("#td_" + index).addClass("errorstatus");
  }

  smallModal(smallDataModal: any) {
    this.modalService.open(smallDataModal, { size: 'sm', windowClass: 'modal-holder', centered: true });
  }

  displayfilter() {
    this.filter = !this.filter;
    $('.filter').val('').trigger('change');
  }

  startfeatureslection = false;
  displayselection = true;
  targetColumnName = '';
  startFeatureSelection(schemarecommodate: any) {
    if ($("tbody").find('.Target-selected').length > 0) {
      this.targetColumn = 1;
      var target = $('.Target-selected').prop('id').split('_')[1];
      this.targetColumnName = $('.columnname_' + target).prop('id').split('_')[1];
      this.startfeatureslection = true;
      this.getFeatureSelection(schemarecommodate);
    }
    else {
      this.toaster.error("Please select target column first", "Error");
      this.targetColumn = 0;
      this.targetColumnName = '';
    }
  }

  stopFeatureSelection() {
    this.startfeatureslection = false;
    if (this.setFeatureSelectionInterval) {
      clearInterval(this.setFeatureSelectionInterval);
      this.setFeatureSelectionInterval = undefined;
    }
  }
}