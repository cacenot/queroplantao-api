/**
 * @queroplantao/api-client
 *
 * TypeScript API client for Quero Plantão API with React Query hooks.
 *
 * @example
 * ```typescript
 * import { useListProfessionals } from '@queroplantao/api-client';
 * import { ProfessionalType, ProfessionalTypeLabels } from '@queroplantao/api-client/enums';
 *
 * function ProfessionalsList() {
 *   const { data, isLoading } = useListProfessionals({ page: 1, pageSize: 10 });
 *   return <div>{data?.items.map(p => <div key={p.id}>{p.fullName}</div>)}</div>;
 * }
 * ```
 */

// Re-export generated client (services, hooks, models)
// Note: This also exports enum types from models - use @queroplantao/api-client/enums
// for enums with PT-BR labels
export * from "./client";

// Re-export i18n utilities (error codes and messages)
export * from "./i18n";

// Re-export utilities
export * from "./utils";

// Note: Enums with labels are available via '@queroplantao/api-client/enums'
// They are not re-exported here to avoid conflicts with generated model enums
