/**
 * Custom fetch function for orval-generated client.
 *
 * This function wraps the native fetch with:
 * - Authentication headers
 * - Organization ID header (multi-tenant)
 * - Error handling with typed ApiClientError
 * - Timeout support
 */

import {
    buildRequestHeaders,
    buildUrl,
    getApiClientConfig,
} from "../utils/client-config.js";
import { ApiClientError, extractApiError } from "../utils/errors.js";
import { toCamelCase, toSnakeCase } from "./case-transformer.js";

/**
 * Request options for customFetch.
 */
export interface CustomFetchOptions extends RequestInit {
    /**
     * Override the base URL for this request.
     */
    baseUrl?: string;
}

/**
 * Custom fetch function that integrates with API client configuration.
 *
 * @param url - The URL path (will be prefixed with baseUrl)
 * @param options - Fetch options
 * @returns The response data
 */
export async function customFetch<T>(
    url: string,
    options: CustomFetchOptions = {}
): Promise<T> {
    const config = getApiClientConfig();
    const { baseUrl: overrideBaseUrl, ...fetchOptions } = options;

    // Build full URL
    const fullUrl = overrideBaseUrl
        ? `${overrideBaseUrl}${url}`
        : buildUrl(url);

    // Build headers
    const configHeaders = await buildRequestHeaders();
    const headers = new Headers({
        ...configHeaders,
        ...(fetchOptions.headers as Record<string, string>),
    });

    // Transform request body to snake_case if present
    let transformedBody = fetchOptions.body;
    if (fetchOptions.body && typeof fetchOptions.body === "string") {
        try {
            const parsedBody = JSON.parse(fetchOptions.body);
            transformedBody = JSON.stringify(toSnakeCase(parsedBody));
        } catch {
            // If not JSON, keep original body
            transformedBody = fetchOptions.body;
        }
    }

    // Setup abort controller for timeout
    const controller = new AbortController();
    const timeout = config.timeout ?? 30000;
    const timeoutId = setTimeout(() => controller.abort(), timeout);

    try {
        const response = await fetch(fullUrl, {
            ...fetchOptions,
            body: transformedBody,
            headers,
            signal: controller.signal,
        });

        clearTimeout(timeoutId);

        // Handle non-OK responses
        if (!response.ok) {
            const apiError = await extractApiError(response);
            throw new ApiClientError(apiError, response.status);
        }

        // Handle empty responses (204 No Content)
        if (response.status === 204) {
            return {
                data: undefined,
                status: response.status,
                headers: response.headers,
            } as T;
        }

        // Parse JSON response and transform to camelCase
        const data = await response.json();
        return {
            data: toCamelCase(data),
            status: response.status,
            headers: response.headers,
        } as T;
    } catch (error) {
        clearTimeout(timeoutId);

        // Re-throw ApiClientError as-is
        if (error instanceof ApiClientError) {
            throw error;
        }

        // Handle abort/timeout
        if (error instanceof DOMException && error.name === "AbortError") {
            throw new ApiClientError(
                { code: "TIMEOUT", message: `Request timed out after ${timeout}ms` },
                408
            );
        }

        // Handle network errors
        if (error instanceof TypeError) {
            throw new ApiClientError(
                { code: "NETWORK_ERROR", message: "Network request failed" },
                0
            );
        }

        // Unknown error
        throw new ApiClientError(
            { code: "UNKNOWN_ERROR", message: String(error) },
            0
        );
    }
}

export default customFetch;
