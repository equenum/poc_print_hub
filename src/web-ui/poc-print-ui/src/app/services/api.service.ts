import { HttpClient, HttpErrorResponse, HttpHeaders, HttpResponse } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { EnvService } from './env.service';
import * as Interfaces from '../interfaces';
import { catchError, Observable, of } from 'rxjs';

@Injectable({providedIn: 'root'})
export class ApiService {
  private readonly httpClient = inject(HttpClient);
  private readonly envService = inject(EnvService);

  getQueueStatuses(tenantId: string, tenantToken: string):
    Observable<HttpResponse<Interfaces.QueueStatusData> | HttpResponse<undefined>> {
      return this.httpClient.get<Interfaces.QueueStatusData>(this.getFullUrl('queues/status'), 
        {
          headers: this.buildHeaders(tenantId, tenantToken), 
          observe: 'response' as const 
        }
      ).pipe(catchError((error: HttpErrorResponse) => {
        return of(new HttpResponse({
          body: undefined,
          status: error.status,
          statusText: error.statusText
        }));
      }));
  }

  getPrinterStatus(tenantId: string, tenantToken: string): 
    Observable<HttpResponse<Interfaces.PrinterStatusData> | HttpResponse<undefined>> {
      return this.httpClient.get<Interfaces.PrinterStatusData>(this.getFullUrl('printer/status'),
        { 
          headers: this.buildHeaders(tenantId, tenantToken),
          observe: 'response' as const  
        }
      ).pipe(catchError((error: HttpErrorResponse) => {
        return of(new HttpResponse({
          body: undefined,
          status: error.status,
          statusText: error.statusText
        }));
      }));
  }

  getTenantRole(tenantId: string, tenantToken: string):
    Observable<HttpResponse<Interfaces.TenantData> | HttpResponse<undefined>> {
      var body: Interfaces.TenantRoleRequest = {
        tenantId: tenantId
      };
      
      return this.httpClient.post<Interfaces.TenantData>(this.getFullUrl('tenant/role'), body,
        { 
          headers: this.buildHeaders(tenantId, tenantToken),
          observe: 'response' as const
        }
      ).pipe(catchError((error: HttpErrorResponse) => {
        return of(new HttpResponse({
          body: undefined,
          status: error.status,
          statusText: error.statusText
        }));
      }));
  }

  sendCutPaper(tenantId: string, tenantToken: string):
    Observable<HttpResponse<Interfaces.GenericApiResponse> | HttpResponse<undefined>> {
      return this.httpClient.post<Interfaces.GenericApiResponse>(this.getFullUrl('printer/cut'), null,
        { 
          headers: this.buildHeaders(tenantId, tenantToken),
          observe: 'response' as const
        }
      ).pipe(catchError((error: HttpErrorResponse) => {
        return of(new HttpResponse({
          body: undefined,
          status: error.status,
          statusText: error.statusText
        }));
      }));
  }

  sendFeedPaper(tenantId: string, tenantToken: string, nTimes: number): Observable<HttpResponse<GenericApiResponse> | HttpResponse<undefined>> {
    var body: FeedPaperRequest = {
      nTimes: nTimes
    };

    return this.httpClient.post<GenericApiResponse>(this.getFullUrl('printer/feed'), body,
      { 
        headers: this.buildHeaders(tenantId, tenantToken),
        observe: 'response' as const
      }
    ).pipe(catchError((error: HttpErrorResponse) => {
      return of(new HttpResponse({
        body: undefined,
        status: error.status,
        statusText: error.statusText
      }));
    }));
  }

  private getFullUrl(relativePath: string): string {
    return `${this.envService.apiUrl}/${relativePath}`;
  }

  private buildHeaders(tenantId: string, tenantToken: string): HttpHeaders {
    var headers = new HttpHeaders();

    headers = headers.set(this.envService.tenantIdHeader, tenantId);
    headers = headers.set(this.envService.tenantTokenHeader, tenantToken);

    return headers;
  }
}
