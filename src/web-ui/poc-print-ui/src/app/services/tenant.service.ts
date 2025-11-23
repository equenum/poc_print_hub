import { inject, Injectable } from '@angular/core';
import { ApiService } from './api.service';
import { TenantData } from '../interfaces';
import { lastValueFrom } from 'rxjs';

@Injectable({providedIn: 'root'})
export class TenantService {
  private readonly apiService = inject(ApiService);

  private authToken: string = '';
  private tenantData: TenantData | undefined;

  async authenticate(authTenantId: string, authToken: string): Promise<TenantData | undefined> {
    var tenantData = await lastValueFrom(this.apiService.getTenantRole(authTenantId, authToken));
    if (!tenantData) {
      return undefined;
    }

    this.tenantData = tenantData;
    this.authToken = authToken;

    return this.tenantData;
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
