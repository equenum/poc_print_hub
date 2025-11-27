import { Component, inject, signal } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { PrinterStatusData, QueueStatusData, SelectOption, TenantData } from './interfaces';
import { ApiService } from './services/api.service';
import { TenantService } from './services/tenant.service';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, FormsModule, CommonModule],
  templateUrl: './app.html'
})
export class App {
  public readonly dataPlaceholder = 'N/A';

  private readonly apiService = inject(ApiService);
  private readonly tenantService = inject(TenantService);

  readonly bodyTypeOptions: SelectOption[] = [
    { value: 'text', displayName: 'Text' },
    { value: 'keyvalue', displayName: 'Key-Value' }
  ];

  readonly feedSelectorTypeOptions: SelectOption[] = [
    { value: 'slider', displayName: 'Slider' },
    { value: 'custom', displayName: 'Custom' }
  ];

  // control inputs
  selectedBodyType = signal<string>('text');
  selectedFeedSelectorType = signal<string>('slider');
  selectedFeedTimes = signal<number>(5);

  // tenant auth
  isTenantAuthenticated = signal<boolean>(false);
  isTenantAuthInProgress = signal<boolean>(false);

  tenantId = signal<string>('');
  tenantToken = signal<string>('');

  // dashboard status
  isQueueStatusLoaded = signal<boolean>(false);
  isPrinterStatusLoaded = signal<boolean>(false);

  // dashboard data
  queueStatusData: QueueStatusData | undefined;
  printerStatusData: PrinterStatusData | undefined;
  tenantData: TenantData | undefined;

  async onTenantAuthSave(): Promise<void> {
    this.isTenantAuthInProgress.set(true);

    var tenantData = await this.tenantService.authenticate(
      this.tenantId().trim(), 
      this.tenantToken().trim()
    );
    
    if (!tenantData) {
      // show error toast: ngx-toastr
      this.isTenantAuthInProgress.set(false);
      return;
    }

    this.tenantData = tenantData;
    this.isTenantAuthenticated.set(true);
    this.isTenantAuthInProgress.set(false);
    this.tenantId.set('');
    this.tenantToken.set('');

    // show success toast: ngx-toastr

    // reset dashboard data and status
    this.queueStatusData = undefined;
    this.printerStatusData = undefined;
    this.isQueueStatusLoaded.set(false);
    this.isPrinterStatusLoaded.set(false);

    // if user is Admin, load dashboard data
    if (this.tenantData?.role.toLowerCase() == 'admin') {
      this.apiService.getQueueStatuses(this.tenantService.tenantId, this.tenantService.tenantToken)
        .subscribe((data) => {
          this.queueStatusData = data;
          this.isQueueStatusLoaded.set(true);
      });

      this.apiService.getPrinterStatus(this.tenantService.tenantId, this.tenantService.tenantToken)
        .subscribe((data) => {
          this.printerStatusData = data;
          this.isPrinterStatusLoaded.set(true);
      });
    }
  }

  isTenantSaveButtonDisabled(): boolean {
    return this.tenantId().length == 0 || this.tenantToken().length == 0;
  }

  isTenantAuthorized(allowedRoles: string[]): boolean {
    if (!this.isTenantAuthenticated() || !this.tenantData) {
      return false;
    }

    return allowedRoles.some(
      role => role.toLowerCase() == this.tenantData?.role.toLowerCase()
    );
  }

  getBodyTypePlaceholder(): string {
    switch (this.selectedBodyType()) {
      case 'text':
        return 'Enter message text';
      case 'keyvalue':
        return 'Enter JSON message, e.g., { "key": "value" }';
      default:
        return 'Enter message text';
    }
  }

  getPrinterName(): string {
    return this.printerStatusData
      ? this.printerStatusData.name 
      : this.dataPlaceholder;
  }

  getPrinterStatus(): string {
    return this.printerStatusData
      ? this.getQueueStatusMesage(this.printerStatusData.isOnline) 
      : this.dataPlaceholder;
  }

  getPrinterPaperStatus(): string {
    return this.printerStatusData
      ? this.printerStatusData.paperStatus 
      : this.dataPlaceholder;
  }

  getQueueStatus(name: string): string {
    if (this.queueStatusData) {
      switch (name) {
        case 'print':
          return this.getQueueStatusMesage(this.queueStatusData.print.isOnline);
        case 'error':
          return this.getQueueStatusMesage(this.queueStatusData.deadLetter.isOnline);
        default:
          return this.dataPlaceholder;
      }
    }

    return this.dataPlaceholder;
  }

  getQueueCount(name: string): string {
    if (this.queueStatusData) {
      switch (name) {
        case 'print':
          return this.queueStatusData.print.count.toString();
        case 'error':
          return this.queueStatusData.deadLetter.count.toString();
        default:
          return this.dataPlaceholder;
      }
    }

    return this.dataPlaceholder;
  }

  getTenantId(): string {
    if (this.tenantData) {
      return this.tenantData.tenantId.length >= 10
        ? `${this.tenantData.tenantId.slice(0, 10)}...` 
        : this.tenantData.tenantId
    }

    return this.dataPlaceholder;
  }

  getTenantRole(): string {
    if (!this.tenantData) {
      return this.dataPlaceholder;
    }

    switch (this.tenantData.role) {
      case 'ADMIN':
        return 'Admin';
      case 'USER':
        return 'User';
      default:
        return this.dataPlaceholder;
    }
  }

  getQueueStatusMesage(isOnline: boolean): string {
    return isOnline ? 'Online' : 'Offline';
  }
}
