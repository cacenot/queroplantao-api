/**
 * Error handling utilities for API responses.
 */

/**
 * Standard error response from the API.
 */
export interface ApiError {
    code: string;
    message: string;
    details?: Record<string, unknown>;
}

/**
 * Type guard to check if an error is an ApiError.
 */
export function isApiError(error: unknown): error is ApiError {
    return (
        typeof error === "object" &&
        error !== null &&
        "code" in error &&
        "message" in error &&
        typeof (error as ApiError).code === "string" &&
        typeof (error as ApiError).message === "string"
    );
}

/**
 * Extract ApiError from a fetch response or thrown error.
 */
export async function extractApiError(response: Response): Promise<ApiError> {
    try {
        const body = await response.json();
        if (isApiError(body)) {
            return body;
        }
        return {
            code: "UNKNOWN_ERROR",
            message: body.detail || body.message || "An unknown error occurred",
        };
    } catch {
        return {
            code: "PARSE_ERROR",
            message: "Failed to parse error response",
        };
    }
}

/**
 * Custom error class for API errors with typed code.
 */
export class ApiClientError extends Error {
    public readonly code: string;
    public readonly statusCode: number;
    public readonly details?: Record<string, unknown>;

    constructor(error: ApiError, statusCode: number) {
        super(error.message);
        this.name = "ApiClientError";
        this.code = error.code;
        this.statusCode = statusCode;
        this.details = error.details;
    }

    /**
     * Check if this error matches a specific error code.
     */
    is(code: string): boolean {
        return this.code === code;
    }
}

/**
 * Type for error handler functions.
 */
export type ErrorHandler = (error: ApiClientError) => void;

/**
 * Create an error handler that handles specific error codes.
 */
export function createErrorHandler(
    handlers: Record<string, (error: ApiClientError) => void>,
    fallback?: ErrorHandler
): ErrorHandler {
    return (error: ApiClientError) => {
        const handler = handlers[error.code];
        if (handler) {
            handler(error);
        } else if (fallback) {
            fallback(error);
        }
    };
}
