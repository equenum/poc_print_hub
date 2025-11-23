import { HttpClient, HttpHeaders, HttpParams } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { EnvService } from './env.service';
import { PrinterStatusData, QueueStatusData, TenantData, TenantRoleRequest } from '../interfaces';
import { Observable } from 'rxjs';

@Injectable({providedIn: 'root'})
export class ApiService {
  private readonly httpClient = inject(HttpClient);
  private readonly envService = inject(EnvService);

  getQueueStatuses(tenantId: string, tenantToken: string): Observable<QueueStatusData> {
    return this.httpClient.get<QueueStatusData>(this.getFullUrl('queues/status'), 
      { headers: this.buildHeaders(tenantId, tenantToken) }
    );
  }

  getPrinterStatus(tenantId: string, tenantToken: string): Observable<PrinterStatusData> {
    return this.httpClient.get<PrinterStatusData>(this.getFullUrl('printer/status'),
      { headers: this.buildHeaders(tenantId, tenantToken) }
    );
  }

  getTenantRole(tenantId: string, tenantToken: string): Observable<TenantData> {
    var body: TenantRoleRequest = {
      tenantId: tenantId
    };
    
    return this.httpClient.post<TenantData>(this.getFullUrl('tenant/role'), body,
      { headers: this.buildHeaders(tenantId, tenantToken)}
    );
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
