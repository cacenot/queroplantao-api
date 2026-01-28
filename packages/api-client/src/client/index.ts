/**
 * Generated API client.
 *
 * This file re-exports the orval-generated client.
 */

// Re-export all generated services (hooks, queries, mutations)
export * from "./generated/auth/auth";
// Skip enums - we have our own with labels in src/enums/
// export * from "./generated/enums/enums";
export * from "./generated/health/health";
export * from "./generated/invitations/invitations";
export * from "./generated/organization-users/organization-users";
export * from "./generated/professionals/professionals";
export * from "./generated/screening/screening";
export * from "./generated/screening-public/screening-public";
export * from "./generated/specialties/specialties";

// Re-export all models (interfaces, types)
export * from "./models";

// Re-export custom fetch
export { customFetch } from "./custom-fetch";

export const CLIENT_VERSION = "1.1.2";
