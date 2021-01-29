import { Injectable } from '@angular/core';
import {HttpClient,HttpHeaders, HttpParams } from '@angular/common/http';
import  { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class SchemaMappingApiService {

   baseUrl = 'http://127.0.0.1:8000/mlaas/'
   headers = new HttpHeaders ({
     'Content-type': 'application/json',
   });
   user:any;
   
  constructor( private httpClient : HttpClient) { 

  }
  
  getDataDetails(obj,dataset_id):Observable<any>{
    var params=new HttpParams().append("dataset_id",dataset_id)
    return this.httpClient.post(this.baseUrl+"ingest/data_detail/",obj,{headers:this.headers,params});
  }

 
  getColumnList(dataset_id):Observable<any>{
    var params=new HttpParams().append("dataset_id",dataset_id)
    return this.httpClient.get(this.baseUrl+"ingest/data_detail/column_list/",{headers:this.headers,params});
  }

  getColumnAttributes():Observable<any>{
    return this.httpClient.get(this.baseUrl+"dataset_schema/column_attribute_list/",{headers:this.headers});
  }

  getDatatypeList():Observable<any>{
    return this.httpClient.get(this.baseUrl+"dataset_schema/datatype_list/",{headers:this.headers});
  }

  getDatasetSchema(dataset_id):Observable<any>{
    var params=new HttpParams().append("project_id",dataset_id)
    return this.httpClient.get(this.baseUrl+"ingest/dataset_schema/",{headers:this.headers,params});
  }
  
  saveDatasetSchema(dataset_id,project_id,obj):Observable<any>{
    var params=new HttpParams().append("dataset_id",dataset_id).append("project_id",project_id)
    return this.httpClient.post(this.baseUrl+"ingest/dataset_schema/",obj,{headers:this.headers,params});
  }
}
