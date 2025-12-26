import { Component, inject, signal } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { NotificationMessage, PrinterStatusData, QueueStatusData, SelectOption, TenantData } from './interfaces';
import { ApiService } from './services/api.service';
import { TenantService } from './services/tenant.service';
import { ToastrService } from 'ngx-toastr';
import { MessageBodyType, TenantStatus } from './consts';
import { HttpStatusCode } from '@angular/common/http';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, FormsModule, CommonModule],
  templateUrl: './app.html'
})
export class App {
  public readonly dataPlaceholder = 'N/A';
  public readonly tenantAuthenticationTooltip = 'Tenant not authenticated';
  public readonly tenantAuthorizationTooltip = 'Tenant not authorized';

  private readonly apiService = inject(ApiService);
  private readonly tenantService = inject(TenantService);
  private readonly toastrService = inject(ToastrService);

  readonly bodyTypeOptions: SelectOption[] = [
    { value: MessageBodyType[MessageBodyType.PlainText], displayName: 'Text' },
    { value: MessageBodyType[MessageBodyType.KeyValue], displayName: 'Key-Value' }
  ];

  readonly feedSelectorTypeOptions: SelectOption[] = [
    { value: 'slider', displayName: 'Slider' },
    { value: 'custom', displayName: 'Custom' }
  ];

  // control inputs
  selectedBodyType = signal<string>(MessageBodyType[MessageBodyType.PlainText]);
  selectedFeedSelectorType = signal<string>('slider');
  selectedFeedTimes = signal<number>(5);
  selectedFeedTimesRange = signal<number>(25);
  messageTitle = signal<string>('');
  messageBody = signal<string>('');

  // tenant auth
  isTenantAuthenticated = signal<boolean>(false);
  isTenantAuthInProgress = signal<boolean>(false);

  tenantId = signal<string>('');
  tenantToken = signal<string>('');

  // dashboard status
  isQueueStatusLoaded = signal<boolean>(false);
  isPrinterStatusLoaded = signal<boolean>(false);
  isQueueStatusReloadInProgress = signal<boolean>(false);
  isPrinterStatusReloadInProgress = signal<boolean>(false);

  // dashboard data
  queueStatusData: QueueStatusData | undefined;
  printerStatusData: PrinterStatusData | undefined;
  tenantData: TenantData | undefined;

  // command statuses
  isCutPaperInProgress = signal<boolean>(false);
  isFeedPaperInProgress = signal<boolean>(false);
  isPublishMessageInProgress = signal<boolean>(false);
  isRepublishMessagesInProgress = signal<boolean>(false);

  async onTenantAuthSave(): Promise<void> {
    this.isTenantAuthInProgress.set(true);

    var tenantDataBundle = await this.tenantService.authenticate(
      this.tenantId().trim(),
      this.tenantToken().trim()
    );

    if (tenantDataBundle.status != TenantStatus.Authenticated) {
      this.isTenantAuthInProgress.set(false);

      var message = tenantDataBundle.status == TenantStatus.NotFound 
        ? 'Tenant not found' 
        : 'Tenant data fetch error';

      this.toastrService.error(`Authentication: ${message}`);
      return;
    }

    this.tenantData = tenantDataBundle.data;
    this.isTenantAuthenticated.set(true);
    this.isTenantAuthInProgress.set(false);
    this.tenantId.set('');
    this.tenantToken.set('');

    this.toastrService.success('Authentication: Succeeded');

    // reset dashboard data and status
    this.queueStatusData = undefined;
    this.printerStatusData = undefined;
    this.isQueueStatusLoaded.set(false);
    this.isPrinterStatusLoaded.set(false);

    // if user is Admin, load dashboard data
    if (this.tenantData?.role.toLowerCase() == 'admin') {
      this.apiService.getQueueStatuses(this.tenantService.tenantId, this.tenantService.tenantToken)
        .subscribe((response) => {
          this.queueStatusData = response.body || undefined;
          this.isQueueStatusLoaded.set(true);
        });

      this.apiService.getPrinterStatus(this.tenantService.tenantId, this.tenantService.tenantToken)
        .subscribe((response) => {
          this.printerStatusData = response.body || undefined;
          this.isPrinterStatusLoaded.set(true);
        });
    }
  }

  onDashboardReload(): void {
    this.queueStatusData = undefined;
    this.printerStatusData = undefined;
    this.isQueueStatusReloadInProgress.set(true);
    this.isPrinterStatusReloadInProgress.set(true);

    this.apiService.getQueueStatuses(this.tenantService.tenantId, this.tenantService.tenantToken)
      .subscribe((response) => {
        this.queueStatusData = response.body || undefined;
        this.isQueueStatusReloadInProgress.set(false);
      });

    this.apiService.getPrinterStatus(this.tenantService.tenantId, this.tenantService.tenantToken)
      .subscribe((response) => {
        this.printerStatusData = response.body || undefined;
        this.isPrinterStatusReloadInProgress.set(false);
      });
  }

  onCutPaper(): void {
    this.isCutPaperInProgress.set(true);
    
    this.apiService.sendCutPaper(this.tenantService.tenantId, this.tenantService.tenantToken)
      .subscribe((response) => {
        if (response.status != HttpStatusCode.Ok as number) {
          this.toastrService.error('Cut paper: Failed');
          this.isCutPaperInProgress.set(false);
          return;
        }

        this.toastrService.success('Cut paper: Succeeded');
        this.isCutPaperInProgress.set(false);
      });
  }

  onFeedPaper(): void {
    if (this.selectedFeedSelectorType()) {
      const customNTimes = this.selectedFeedTimes();
      if (customNTimes < 5 || customNTimes > 255) {
        this.toastrService.error('Feed paper: Invalid input');
        return;
      }
    }

    this.isFeedPaperInProgress.set(true);

    const nTimes: number = this.selectedFeedSelectorType() == 'slider' 
      ? this.selectedFeedTimesRange() 
      : this.selectedFeedTimes();
    
    this.apiService.sendFeedPaper(this.tenantService.tenantId, this.tenantService.tenantToken, nTimes)
      .subscribe((response) => {
        if (response.status != HttpStatusCode.Ok as number) {
          this.toastrService.error('Feed paper: Failed');
          this.isFeedPaperInProgress.set(false);
          return;
        }

        this.toastrService.success('Feed paper: Succeeded');
        this.isFeedPaperInProgress.set(false);
      });
  }

  onResetFeedPaperForm(): void {
    this.selectedFeedSelectorType.set('slider');
    this.selectedFeedTimes.set(5);
    this.selectedFeedTimesRange.set(25);
  }

  onPublishMessages(): void {
    const messageBody: string = this.messageBody();

    if (this.selectedBodyType() == MessageBodyType[MessageBodyType.KeyValue]) {
      try {
        const prettyJson: string = JSON.stringify(JSON.parse(messageBody), null, 2);
        this.messageBody.set(prettyJson);
      } catch {
        this.toastrService.error('Publish message: Invalid message body');
        return;
      }
    }

    const message: NotificationMessage = {
      id: undefined,
      title: this.messageTitle(),
      body: messageBody,
      bodyType: this.selectedBodyType(),
      origin: undefined,
      timestamp: new Date().toISOString()
    };

    this.isPublishMessageInProgress.set(true);
    
    this.apiService.publishMessage(this.tenantService.tenantId, this.tenantService.tenantToken, message)
      .subscribe((response) => {
        if (response.status != HttpStatusCode.Ok as number) {
          this.toastrService.error('Publish message: Failed');
          this.isPublishMessageInProgress.set(false);
          return;
        }

        this.toastrService.success('Publish message: Succeeded');
        this.isPublishMessageInProgress.set(false);

        this.reloadQueueStatusDashboard();
      });
  }

  onResetPublishMessageForm(): void {
    this.selectedBodyType = signal<string>(MessageBodyType[MessageBodyType.PlainText]);
    this.messageTitle.set('');
    this.messageBody.set('');
  }

  onRepublishMessages(): void {
    this.isRepublishMessagesInProgress.set(true);
    
    this.apiService.republishMessages(this.tenantService.tenantId, this.tenantService.tenantToken)
      .subscribe((response) => {
        if (response.status != HttpStatusCode.Ok as number) {
          this.toastrService.error('Republish messages: Failed');
          this.isRepublishMessagesInProgress.set(false);
          return;
        }

        this.toastrService.success('Republish messages: Succeeded');
        this.isRepublishMessagesInProgress.set(false);

        this.reloadQueueStatusDashboard();
      });
  }

  reloadQueueStatusDashboard(): void {
    if (this.tenantData?.role.toLowerCase() == 'admin') {
      this.queueStatusData = undefined;
      this.isQueueStatusLoaded.set(false);

      this.apiService.getQueueStatuses(this.tenantService.tenantId, this.tenantService.tenantToken)
        .subscribe((response) => {
          this.queueStatusData = response.body || undefined;
          this.isQueueStatusLoaded.set(true);
        });
    }
  }

  isTenantSaveButtonDisabled(): boolean {
    return !this.hasValue(this.tenantId()) || !this.hasValue(this.tenantToken());
  }

  isTenantAuthorized(allowedRoles: string[]): boolean {
    if (!this.isTenantAuthenticated() || !this.tenantData) {
      return false;
    }

    return allowedRoles.some(
      role => role.toLowerCase() == this.tenantData?.role.toLowerCase()
    );
  }

  isMessagePublishingDisabled(): boolean {
    return !this.hasValue(this.messageTitle()) || !this.hasValue(this.messageBody());
  }

  isFeedPaperDisabled(): boolean {
    if (this.selectedFeedSelectorType() == 'custom') {
      const customNTimes = this.selectedFeedTimes();
      return customNTimes < 5 || customNTimes > 255
    }

    return false;
  }

  getTenantAuthSaveTooltip(): string {
    if (!this.hasValue(this.tenantId()) || !this.hasValue(this.tenantToken())) {
      return 'Tenant id and token required';
    }

    return '';
  }

  getTenantAuthTooltip(allowedRoles: string[]): string {
    if (!this.isTenantAuthenticated()) {
      return this.tenantAuthenticationTooltip;
    }

    if (!this.isTenantAuthorized(allowedRoles)) {
      return this.tenantAuthorizationTooltip;
    }

    return '';
  }

  getPublishMessageTooltip(allowedRoles: string[]): string {
    if (!this.isTenantAuthenticated()) {
      return this.tenantAuthenticationTooltip;
    }

    if (!this.isTenantAuthorized(allowedRoles)) {
      return this.tenantAuthorizationTooltip;
    }

    if (!this.hasValue(this.messageTitle()) || !this.hasValue(this.messageBody())) {
      return 'Message title and body required';
    }

    return '';
  }

  getFeedPaperTooltip(allowedRoles: string[]): string {
    if (!this.isTenantAuthenticated()) {
      return this.tenantAuthenticationTooltip;
    }

    if (!this.isTenantAuthorized(allowedRoles)) {
      return this.tenantAuthorizationTooltip;
    }

    const customNTimes = this.selectedFeedTimes();
    if (this.selectedFeedSelectorType() == 'custom' && (customNTimes < 5 || customNTimes > 255)) {
      return 'n-times must be between 5 to 255';
    }

    return '';
  }

  getDashboardReloadTooltip(allowedRoles: string[]): string {
    if (!this.isTenantAuthenticated()) {
      return this.tenantAuthenticationTooltip;
    }

    if (!this.isTenantAuthorized(allowedRoles)) {
      return this.tenantAuthorizationTooltip;
    }

    return '';
  }

  getBodyTypePlaceholder(): string {
    switch (this.selectedBodyType()) {
      case MessageBodyType[MessageBodyType.PlainText]:
        return 'Enter message text';
      case MessageBodyType[MessageBodyType.KeyValue]:
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
      ? this.getStatusMesage(this.printerStatusData.isOnline)
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
          return this.getStatusMesage(this.queueStatusData.print.isOnline);
        case 'error':
          return this.getStatusMesage(this.queueStatusData.deadLetter.isOnline);
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

  getFullTenantId(): string {
    if (this.tenantData) {
      return this.tenantData.tenantId
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

  getStatusMesage(isOnline: boolean): string {
    return isOnline ? 'Online' : 'Offline';
  }

  hasValue(value: string): boolean {
    return value !== null && value !== undefined && value.trim().length > 0;
  }
}
