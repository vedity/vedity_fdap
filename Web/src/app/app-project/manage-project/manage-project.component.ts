import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';

@Component({
  selector: 'app-manage-project',
  templateUrl: 'manage-project.component.html',
  styleUrls: ['./manage-project.component.scss']
})
export class ManageProjectComponent implements OnInit {
active=1;
classname="";
  constructor(public router:Router) { }

  ngOnInit() {
  }

  create() {
    this.router.navigate(['create']);
  }

  toggleTimeline(){
    if(this.classname=="")
    this.classname="red";
    else
    this.classname="";
  }
}
