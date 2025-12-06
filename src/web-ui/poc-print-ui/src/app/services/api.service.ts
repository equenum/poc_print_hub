import { HttpClient, HttpErrorResponse, HttpHeaders, HttpResponse } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { EnvService } from './env.service';
import { GenericApiResponse, PrinterStatusData, QueueStatusData, TenantData, TenantRoleRequest } from '../interfaces';
import { catchError, Observable, of } from 'rxjs';

@Injectable({providedIn: 'root'})
export class ApiService {
  private readonly httpClient = inject(HttpClient);
  private readonly envService = inject(EnvService);

  getQueueStatuses(tenantId: string, tenantToken: string): Observable<HttpResponse<QueueStatusData> | HttpResponse<undefined>> {
    return this.httpClient.get<QueueStatusData>(this.getFullUrl('queues/status'), 
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

  getPrinterStatus(tenantId: string, tenantToken: string): Observable<HttpResponse<PrinterStatusData> | HttpResponse<undefined>> {
    return this.httpClient.get<PrinterStatusData>(this.getFullUrl('printer/status'),
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

  getTenantRole(tenantId: string, tenantToken: string): Observable<HttpResponse<TenantData> | HttpResponse<undefined>> {
    var body: TenantRoleRequest = {
      tenantId: tenantId
    };
    
    return this.httpClient.post<TenantData>(this.getFullUrl('tenant/role'), body,
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

  sendCutPaper(tenantId: string, tenantToken: string): Observable<HttpResponse<GenericApiResponse> | HttpResponse<undefined>> {
    return this.httpClient.post<GenericApiResponse>(this.getFullUrl('printer/cut'), null,
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
