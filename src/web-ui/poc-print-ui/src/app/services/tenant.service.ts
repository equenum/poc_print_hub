import { inject, Injectable } from '@angular/core';
import { ApiService } from './api.service';
import { TenantData, TenantDataBundle } from '../interfaces';
import { lastValueFrom } from 'rxjs';
import { TenantStatus } from '../consts';
import { HttpStatusCode } from '@angular/common/http';

@Injectable({providedIn: 'root'})
export class TenantService {
  private readonly apiService = inject(ApiService);

  private authToken: string = '';
  private tenantData: TenantData | undefined;

  async authenticate(authTenantId: string, authToken: string): Promise<TenantDataBundle> {
    var tenantResponse = await lastValueFrom(this.apiService.getTenantRole(authTenantId, authToken));

    if (tenantResponse && tenantResponse.body) {
      if (tenantResponse.status == HttpStatusCode.Ok as number) {
        this.tenantData = tenantResponse.body;
        this.authToken = authToken;

        return {
          data: this.tenantData,
          status: TenantStatus.Authenticated
        };
      }

      if (tenantResponse.status == HttpStatusCode.NotFound as number || tenantResponse.status == HttpStatusCode.Unauthorized as number) {
        return {
          data: undefined,
          status: TenantStatus.NotFound
        };
      }
    }

    return {
      data: undefined,
      status: TenantStatus.NonAuthenticated
    };
  }

  get tenantId(): string {
    return this.tenantData ? this.tenantData.tenantId : '';
  }

  get tenantrole(): string {
    return this.tenantData ? this.tenantData.role : '';
  }

  get tenantToken(): string {
    return this.authToken;
  }

  get isAuthenticated(): boolean {
    if (
      this.tenantData 
      && this.hasValue(this.tenantData.tenantId) 
      && this.hasValue(this.tenantData.role)
    ) {
      return true;
    }

    return false;
  }

  private hasValue(value: string): boolean {
    return value !== null && value !== undefined && value.trim().length > 0;
  }
}
