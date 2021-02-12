import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
@Injectable({
  providedIn: 'root'
})
export class ProjectApiService {
  baseUrl = 'http://127.0.0.1:8000/mlaas/ingest/'
  baseUrlnew = 'http://127.0.0.1:8000/mlaas/';
  headers = new HttpHeaders({
    'Content-type': 'application/json',
  });
  user: any;
  constructor(private httpClient: HttpClient) { }

  getproject(): Observable<any> {
    this.user = JSON.parse(localStorage.getItem("currentUser"));
    var params = new HttpParams().set("user_name", this.user.username);
    return this.httpClient.get(this.baseUrl + "project/create/", { headers: this.headers, params });
  }

  saveproject(obj: FormData): Observable<any> {
    return this.httpClient.post<any>(this.baseUrl + "project/create/", obj);
  }

  deleteproject(id): Observable<any> {
    this.user = JSON.parse(localStorage.getItem("currentUser"));
    var params = new HttpParams().append("user_name", this.user.username).append('project_id', id);
    return this.httpClient.delete<any>(this.baseUrl + "project/delete/", { headers: this.headers, params });
  }

  getDataset(): Observable<any> {
    this.user = JSON.parse(localStorage.getItem("currentUser"));
    var params = new HttpParams().set("user_name", this.user.username);
    return this.httpClient.get(this.baseUrl + "dataset/create/", { headers: this.headers, params });
  }

  getActivityTimeline(): Observable<any> {
    this.user = JSON.parse(localStorage.getItem("currentUser"));
    var params = new HttpParams().set("user_name", this.user.username);
    return this.httpClient.get(this.baseUrlnew + "common/activity/", { headers: this.headers, params });
  }

  // mlaas/menu/
  savedataset(obj: FormData): Observable<any> {
    return this.httpClient.post<any>(this.baseUrl + "dataset/create/", obj);
  }

  deletedataset(id): Observable<any> {
    this.user = JSON.parse(localStorage.getItem("currentUser"));
    var params = new HttpParams().append("user_name", this.user.username).append('dataset_id', id);
    return this.httpClient.delete(this.baseUrl + "dataset/delete/", { headers: this.headers, params });
  }

  checkUniqueProjectName(obj): Observable<any> {
    this.user = JSON.parse(localStorage.getItem("currentUser"));
    var params = new HttpParams().append("user_name", this.user.username).append("project_name", obj)
    return this.httpClient.get(this.baseUrl + "project/exist/", { headers: this.headers, params });
  }

  checkUniqueDatasetName(obj): Observable<any> {
    this.user = JSON.parse(localStorage.getItem("currentUser"));
    var params = new HttpParams().append("user_name", this.user.username).append("dataset_name", obj)
    return this.httpClient.get(this.baseUrl + "dataset/exist/", { headers: this.headers, params });
  }
}