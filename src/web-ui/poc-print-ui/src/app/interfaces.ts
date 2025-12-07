import { TenantStatus } from "./consts";

export interface EnvConfig {
    isProduction: boolean;
    apiUrl: string;
    tenantIdHeader: string;
    tenantTokenHeader: string;
    messageOriginName: string;
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

export interface TenantDataBundle {
    data: TenantData | undefined;
    status: TenantStatus;
}

export interface TenantRoleRequest {
    tenantId: string;
}

export interface FeedPaperRequest {
    nTimes: number;
}

export interface GenericApiResponse {
    message: string;
    errors: string;
}

export interface NotificationMessage {
    id: string | undefined;
    title: string;
    body: string;
    bodyType: string;
    origin: string | undefined;
    timestamp: string;
}

export interface PublishMessageResponse {
    messageId: string;
}