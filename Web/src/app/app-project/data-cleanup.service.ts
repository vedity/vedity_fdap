import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from 'src/environments/environment';
@Injectable({
  providedIn: 'root'
})
export class DataCleanupApiService 
{
  baseUrl = environment.baseUrl;
  headers = new HttpHeaders({
    'Content-type': 'application/json',
  });
  user: any;
  constructor(private httpClient: HttpClient) { }

  getOperation(): Observable<any> {
    return this.httpClient.get(this.baseUrl + "preprocess/cleanup/master_operation/", { headers: this.headers });
  } 
  
  getColumnList(schema_id): Observable<any> {
    var params = new HttpParams().append("schema_id", schema_id)
    return this.httpClient.get(this.baseUrl + "preprocess/cleanup/get_col_name/", { headers: this.headers, params });
  }

  getColumnviseOperations(obj): Observable<any> {
    return this.httpClient.post(this.baseUrl + "preprocess/cleanup/operation/",obj, { headers: this.headers });
  }

  getScalingOperations(){
    return this.httpClient.get(this.baseUrl + "preprocess/cleanup/scaling/type/", { headers: this.headers });
  } 
  
  getHoldoutList(){
    return this.httpClient.get(this.baseUrl + "preprocess/cleanup/holdout/", { headers: this.headers });
  }

  saveOperations(schema_id,dataset_id,project_id,data){
    var params = new HttpParams().append("schema_id", schema_id).append("dataset_id", dataset_id).append("project_id", project_id)
    return this.httpClient.post(this.baseUrl + "preprocess/cleanup/save/", data,{ headers: this.headers, params });
  }

  savescalingOpertion(data){

    var params = new HttpParams().append("schema_id", data.schema_id)
    .append("dataset_id", data.dataset_id)
    .append("project_id", data.project_id)
    .append("user_name", data.user_name)
    .append("scaling_op", data.scaling_op)
    .append("split_method",data.split_method)
    .append("cv", data.cv)
    .append("valid_ratio", data.valid_ratio)
    .append("test_ratio",  data.test_ratio)
    .append("random_state",data.random_state)
    let obj={}
    return this.httpClient.post(this.baseUrl + "preprocess/cleanup/scaling/",obj,{ headers: this.headers,params});
  }
}