/**
 * Pagination utilities for working with PaginatedResponse.
 */

/**
 * Paginated response from the API.
 * Matches the backend PaginatedResponse schema.
 */
export interface PaginatedResponse<T> {
    items: T[];
    total: number;
    page: number;
    page_size: number;
    total_pages: number;
    has_next: boolean;
    has_previous: boolean;
}

/**
 * Pagination parameters for list endpoints.
 */
export interface PaginationParams {
    page?: number;
    pageSize?: number;
}

/**
 * Convert pagination params to query string format.
 */
export function toPaginationQuery(params: PaginationParams): Record<string, string> {
    const query: Record<string, string> = {};
    if (params.page !== undefined) {
        query.page = String(params.page);
    }
    if (params.pageSize !== undefined) {
        query.page_size = String(params.pageSize);
    }
    return query;
}

/**
 * Get next page params from a paginated response.
 * Returns undefined if there's no next page (for useInfiniteQuery).
 */
export function getNextPageParam<T>(lastPage: PaginatedResponse<T>): number | undefined {
    return lastPage.has_next ? lastPage.page + 1 : undefined;
}

/**
 * Get previous page params from a paginated response.
 * Returns undefined if there's no previous page (for useInfiniteQuery).
 */
export function getPreviousPageParam<T>(firstPage: PaginatedResponse<T>): number | undefined {
    return firstPage.has_previous ? firstPage.page - 1 : undefined;
}

/**
 * Flatten pages from useInfiniteQuery into a single array.
 */
export function flattenPages<T>(pages: PaginatedResponse<T>[] | undefined): T[] {
    if (!pages) return [];
    return pages.flatMap((page) => page.items);
}

/**
 * Get total count from paginated response.
 */
export function getTotalFromPages<T>(pages: PaginatedResponse<T>[] | undefined): number {
    if (!pages || pages.length === 0) return 0;
    return pages[0].total;
}
