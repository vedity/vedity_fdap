import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { PerfectScrollbarModule } from 'ngx-perfect-scrollbar';
import { PERFECT_SCROLLBAR_CONFIG } from 'ngx-perfect-scrollbar';
import { PerfectScrollbarConfigInterface } from 'ngx-perfect-scrollbar';
import { NgbNavModule, NgbDropdownModule, NgbModalModule, NgbTooltipModule } from '@ng-bootstrap/ng-bootstrap';
import {DragDropModule} from '@angular/cdk/drag-drop';

import { NgApexchartsModule } from 'ng-apexcharts';
import { NgxChartistModule } from 'ngx-chartist';
import { ChartsModule } from 'ng2-charts';
import { NgxEchartsModule } from 'ngx-echarts';
import { WidgetModule } from '../shared/widget/widget.module';
import { UIModule } from '../shared/ui/ui.module';
import { FullCalendarModule } from '@fullcalendar/angular';
import { LoaderService } from '../core/services/loader.service';
import { HTTP_INTERCEPTORS } from '@angular/common/http';
import { LoaderInterceptorService } from '../core/services/interceptors/loader-interceptor.service';
import { AppModelingRoutingModule } from './app-modeling-routing.module';
import { DataTablesModule } from 'angular-datatables';
import { NgxSkeletonLoaderModule } from 'ngx-skeleton-loader';
import { NgSelectModule } from '@ng-select/ng-select';
import { ChartModule,HIGHCHARTS_MODULES } from 'angular-highcharts';
import * as more from 'highcharts/highcharts-more.src';
import * as exporting from 'highcharts/modules/exporting.src';
import * as theme from 'highcharts/themes/dark-unica.src';
import { ModelingTypeComponent } from './modeling-type/modeling-type.component';
import { ModelingViewDetailComponent } from './modeling-view-detail/modeling-view-detail.component';
import { ModelingLearningCurveComponent } from './modeling-learning-curve/modeling-learning-curve.component';
import { ModelingFeatureImportanceComponent } from './modeling-feature-importance/modeling-feature-importance.component';
import { ModelingPerformanceMatricsComponent } from './modeling-performance-matrics/modeling-performance-matrics.component';
import { ModelingModalSummaryComponent } from './modeling-modal-summary/modeling-modal-summary.component';
import { ModelingActualPredictionComponent } from './modeling-actual-prediction/modeling-actual-prediction.component';
import { ModelingConfusionMatricsComponent } from './modeling-confusion-matrics/modeling-confusion-matrics.component';
import { ModelingComparisonGraphComponent } from './modeling-comparison-graph/modeling-comparison-graph.component';
import { ModelingComparisonGridComponent } from './modeling-comparison-grid/modeling-comparison-grid.component';
import { ModelingComparisonDetailComponent } from './modeling-comparison-detail/modeling-comparison-detail.component';
import { ModelingErrorDetailComponent } from './modeling-error-detail/modeling-error-detail.component';
import { GoogleChartsModule,ScriptLoaderService } from 'angular-google-charts';


const DEFAULT_PERFECT_SCROLLBAR_CONFIG: PerfectScrollbarConfigInterface = {
  suppressScrollX: true,
  wheelSpeed: 0.3
};
@NgModule({
  declarations: [
    ModelingTypeComponent,
    ModelingErrorDetailComponent,
    ModelingViewDetailComponent,
    ModelingLearningCurveComponent,
    ModelingFeatureImportanceComponent,
    ModelingPerformanceMatricsComponent,
    ModelingModalSummaryComponent,
    ModelingActualPredictionComponent,
    ModelingConfusionMatricsComponent,
    ModelingComparisonDetailComponent,
    ModelingComparisonGraphComponent,
    ModelingComparisonGridComponent
  ],
  imports: [
    CommonModule,
    FormsModule,
    NgbDropdownModule,
    NgbModalModule,
    AppModelingRoutingModule,
    NgApexchartsModule,
    ChartsModule,
    NgxChartistModule,
    NgxEchartsModule,
    GoogleChartsModule,
    NgSelectModule,
    ReactiveFormsModule,
    DataTablesModule,
    UIModule,
    WidgetModule,
    ChartModule,
    
    FullCalendarModule,
    NgbNavModule,
    NgbTooltipModule,
    PerfectScrollbarModule,
    NgxSkeletonLoaderModule.forRoot(),
    NgbNavModule,
    DragDropModule
  ],
  providers: [
    {
      provide: PERFECT_SCROLLBAR_CONFIG,
      useValue: DEFAULT_PERFECT_SCROLLBAR_CONFIG,
      
    },  { provide: HIGHCHARTS_MODULES, useFactory: () => [ more, exporting ,theme] },
    LoaderService,
    ScriptLoaderService,
    { provide: HTTP_INTERCEPTORS, useClass: LoaderInterceptorService, multi: true }
  ]
})

export class AppModelingModule { }