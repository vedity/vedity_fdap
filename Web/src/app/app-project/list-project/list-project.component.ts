import { Component, OnInit, ViewChild } from '@angular/core';
import { Router } from '@angular/router';
import { Observable, Subject } from 'rxjs';
import { HttpClient, HttpParams } from '@angular/common/http';
import { DataTableDirective } from 'angular-datatables';
import { ProjectApiService } from '../project-api.service';
import { ToastrService } from 'ngx-toastr';
import Swal from 'sweetalert2';
import { timeout } from 'rxjs/operators';
import { NgbTabChangeEvent } from '@ng-bootstrap/ng-bootstrap';

@Component({
  selector: 'app-list-project',
  templateUrl: './list-project.component.html',
  styleUrls: ['./list-project.component.scss']
})
export class ListProjectComponent implements OnInit {

  @ViewChild(DataTableDirective, { static: false })
  datatableElement: DataTableDirective;
  dtOptions: DataTables.Settings = {};
  // active = 1;
  dtTrigger: Subject<any> = new Subject<any>();
  filter: boolean = true;
  constructor(public router: Router, public http: HttpClient, public apiService: ProjectApiService, public toaster: ToastrService) { }
  transactions: any = [];

  ngOnInit(): void {
    this.getproject();
  }

  getproject() {
    this.apiService.getproject().subscribe(
      logs => this.successHandler(logs),
      error => this.errorHandler(error)
    );
  }

  successHandler(data) {
    if (data.status_code == "200") {
      this.transactions = data.response;
    }
    else{
      this.transactions=[]
    }
    //console.log(this.datatableElement.dtInstance);
    if(!this.datatableElement.dtInstance){
      this.dtTrigger.next();
    this.datatableElement.dtInstance.then((dtInstance: DataTables.Api) => {
      dtInstance.columns().every(function () {
        const that = this;
        $('input', this.header()).on('keyup change', function () {
          if (that.search() !== this['value']) {
            that
              .search(this['value'])
              .draw();
          }
        });
        $('select', this.header()).on('change', function () {
          if (that.search() !== this['value']) {
            that
              .search(this['value'])
              .draw();
          }
        });
      });
    });
    }
    else{
      this.rendered();
      this.dtTrigger.next();

    }
  }

  errorHandler(error) {
    console.log(error);
    if (error.error_msg)
      this.toaster.error(error.error_msg, 'Error');
    else {
      console.log(error);
      this.toaster.error('Something went wrong', 'Error');
    }
  }

  rendered() {

    this.datatableElement.dtInstance.then((dtInstance: DataTables.Api) => {
      dtInstance.columns().every(function () {
        const that = this;
        $('input', this.header()).on('keyup change', function () {
          if (that.search() !== this['value']) {
            that
              .search(this['value'])
              .draw();
          }
        });
        $('select', this.header()).on('change', function () {
          if (that.search() !== this['value']) {
            that
              .search(this['value'])
              .draw();
          }
        });
      });
      dtInstance.destroy();
    });


  }


  confirm(id) {
    Swal.fire({
      title: 'Are you sure?',
      text: 'You won\'t be able to revert this!',
      icon: 'warning',
      showCancelButton: true,
      confirmButtonColor: '#34c38f',
      cancelButtonColor: '#f46a6a',
      confirmButtonText: 'Yes, delete it!'
    }).then(result => {

      if (result.value) {
        this.apiService.deleteproject(id).subscribe(
          logs => {
            if (logs.status_code=="200") {
              Swal.fire('Deleted!', logs.error_msg, 'success');
              this.getproject();
            }
           else{
            Swal.fire('Not Deleted!', logs.error_msg, 'error')
           }
            //this.rendered();

            // setTimeout(() => {
            //   this.dtTrigger.next();

            // }, 1000);
          },
          error => Swal.fire('Not Deleted!', 'Something went wrong', 'error')
        )

      }
    });
  }

  displayfilter() {
    this.filter = !this.filter;
    console.log(this.filter);
    $('.filter').val('').trigger('change');
  }

}