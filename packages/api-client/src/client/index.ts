/**
 * Generated API client.
 *
 * This file re-exports the orval-generated client.
 */

// Re-export all generated services (hooks, queries, mutations)
export * from "./generated/auth/auth.js";
// Skip enums - we have our own with labels in src/enums/
// export * from "./generated/enums/enums.js";
export * from "./generated/document-types/document-types.js";
export * from "./generated/health/health.js";
export * from "./generated/invitations/invitations.js";
export * from "./generated/organization-users/organization-users.js";
export * from "./generated/professionals/professionals.js";
export * from "./generated/screening-alerts/screening-alerts.js";
export * from "./generated/screening-documents/screening-documents.js";
export * from "./generated/screening-process/screening-process.js";
export * from "./generated/screening-public/screening-public.js";
export * from "./generated/screening-steps/screening-steps.js";
export * from "./generated/specialties/specialties.js";

// Re-export all models (interfaces, types)
export * from "./models/index.js";

// Re-export custom fetch
export { customFetch } from "./custom-fetch.js";

// Re-export case transformation utilities
export { toCamelCase, toSnakeCase } from "./case-transformer.js";
