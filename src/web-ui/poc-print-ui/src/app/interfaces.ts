export interface EnvConfig {
    isProduction: boolean;
    apiUrl: string;
    tenantIdHeader: string;
    tenantTokenHeader: string;
}

export interface SelectOption {
  value: string;
  displayName: string;
}

export interface QueueStatus {
    isOnline: boolean;
    count: number;
}

export interface QueueStatusData {
    print: QueueStatus;
    deadLetter: QueueStatus;
}

export interface PrinterStatusData {
    name: string;
    isOnline: boolean;
    paperStatus: string;
}

export interface TenantData {
    tenantId: string;
    role: string;
}

export interface TenantRoleRequest {
    tenantId: string;
}
