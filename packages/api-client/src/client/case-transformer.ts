/**
 * Case transformation utilities for converting between snake_case (API)
 * and camelCase (TypeScript client).
 *
 * Uses the `humps` library for automatic key transformation while preserving
 * values (enums, UUIDs, dates, etc.) unchanged.
 */

import { camelizeKeys, decamelizeKeys } from "humps";

/**
 * Convert object keys from snake_case to camelCase.
 *
 * - Transforms only keys, not values
 * - Preserves enum values (e.g., "MEDICAL_DOCTOR")
 * - Preserves UUIDs, dates, and other string values
 * - Works recursively on nested objects and arrays
 *
 * @param obj - Object to transform
 * @returns Object with camelCase keys
 *
 * @example
 * ```typescript
 * toCamelCase({ full_name: "Dr. João", professional_type: "MEDICAL_DOCTOR" })
 * // => { fullName: "Dr. João", professionalType: "MEDICAL_DOCTOR" }
 * ```
 */
export function toCamelCase<T = any>(obj: any): T {
    if (obj === null || obj === undefined) {
        return obj;
    }
    return camelizeKeys(obj) as T;
}

/**
 * Convert object keys from camelCase to snake_case.
 *
 * - Transforms only keys, not values
 * - Preserves enum values (e.g., "MEDICAL_DOCTOR")
 * - Preserves UUIDs, dates, and other string values
 * - Works recursively on nested objects and arrays
 *
 * @param obj - Object to transform
 * @returns Object with snake_case keys
 *
 * @example
 * ```typescript
 * toSnakeCase({ fullName: "Dr. João", professionalType: "MEDICAL_DOCTOR" })
 * // => { full_name: "Dr. João", professional_type: "MEDICAL_DOCTOR" }
 * ```
 */
export function toSnakeCase<T = any>(obj: any): T {
    if (obj === null || obj === undefined) {
        return obj;
    }
    return decamelizeKeys(obj) as T;
}
