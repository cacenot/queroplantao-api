/**
 * API client configuration utilities.
 */

/**
 * Configuration options for the API client.
 */
export interface ApiClientConfig {
    /**
     * Base URL of the API (e.g., "https://api.queroplantao.com.br")
     */
    baseUrl: string;

    /**
     * Function to get the current auth token.
     * Called before each request.
     */
    getToken?: () => string | null | Promise<string | null>;

    /**
     * Current organization ID for multi-tenant requests.
     */
    organizationId?: string;

    /**
     * Custom headers to include in all requests.
     */
    headers?: Record<string, string>;

    /**
     * Request timeout in milliseconds.
     * @default 30000
     */
    timeout?: number;
}

let globalConfig: ApiClientConfig = {
    baseUrl: "",
};

/**
 * Configure the global API client settings.
 * Call this once at app initialization.
 *
 * @example
 * ```typescript
 * import { configureApiClient } from '@queroplantao/api-client';
 *
 * configureApiClient({
 *   baseUrl: 'https://api.queroplantao.com.br',
 *   getToken: () => localStorage.getItem('token'),
 *   organizationId: currentOrgId,
 * });
 * ```
 */
export function configureApiClient(config: ApiClientConfig): void {
    globalConfig = { ...globalConfig, ...config };
}

/**
 * Get the current API client configuration.
 */
export function getApiClientConfig(): ApiClientConfig {
    return globalConfig;
}

/**
 * Update organization ID for multi-tenant requests.
 */
export function setOrganizationId(organizationId: string | undefined): void {
    globalConfig.organizationId = organizationId;
}

/**
 * Build headers for API requests.
 * Includes auth token and organization ID if configured.
 */
export async function buildRequestHeaders(): Promise<Record<string, string>> {
    const headers: Record<string, string> = {
        "Content-Type": "application/json",
        ...globalConfig.headers,
    };

    if (globalConfig.getToken) {
        const token = await globalConfig.getToken();
        if (token) {
            headers["Authorization"] = `Bearer ${token}`;
        }
    }

    if (globalConfig.organizationId) {
        headers["X-Organization-Id"] = globalConfig.organizationId;
    }

    return headers;
}

/**
 * Build full URL for an API endpoint.
 */
export function buildUrl(path: string): string {
    const baseUrl = globalConfig.baseUrl.replace(/\/$/, "");
    const cleanPath = path.startsWith("/") ? path : `/${path}`;
    return `${baseUrl}${cleanPath}`;
}
