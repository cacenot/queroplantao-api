# API Client Package

TypeScript API client for the Quero Plantão API with React Query hooks.

## Installation

```bash
npm install @queroplantao/api-client
```

## Setup

Configure the client at app initialization:

```typescript
import { configureApiClient } from '@queroplantao/api-client';

configureApiClient({
  baseUrl: 'https://api.queroplantao.com.br',
  getToken: () => localStorage.getItem('authToken'),
  organizationId: currentOrgId,
});
```

## Usage

### React Query Hooks

```typescript
import { useListProfessionals, useGetProfessional, useCreateProfessional } from '@queroplantao/api-client';

function ProfessionalsList() {
  const { data, isLoading } = useListProfessionals({ page: 1, page_size: 10 });

  if (isLoading) return <Spinner />;

  return (
    <ul>
      {data?.items.map((professional) => (
        <li key={professional.id}>{professional.full_name}</li>
      ))}
    </ul>
  );
}
```

### Enums with Labels

Import enums with PT-BR labels from the `enums` subpath:

```typescript
import { 
  ProfessionalType, 
  ProfessionalTypeLabels,
  getProfessionalTypeLabel,
  CouncilType,
} from '@queroplantao/api-client/enums';

// Get label for display
const label = ProfessionalTypeLabels[ProfessionalType.DOCTOR]; // "Médico"

// Or use the helper function
const label2 = getProfessionalTypeLabel(ProfessionalType.DOCTOR); // "Médico"

// Use in select component
const options = Object.values(ProfessionalType).map((value) => ({
  value,
  label: ProfessionalTypeLabels[value],
}));
```

### Error Handling

```typescript
import { ApiClientError, createErrorHandler } from '@queroplantao/api-client';
import { ErrorCodes, getErrorMessage } from '@queroplantao/api-client/i18n';

const handleError = createErrorHandler({
  [ErrorCodes.PROFESSIONAL_CPF_ALREADY_EXISTS]: () => {
    toast.error('Este CPF já está cadastrado');
  },
  [ErrorCodes.PROFESSIONAL_EMAIL_ALREADY_EXISTS]: () => {
    toast.error('Este email já está cadastrado');
  },
}, (error) => {
  // Fallback for unknown errors
  toast.error(getErrorMessage(error.code));
});

try {
  await createProfessional(data);
} catch (error) {
  if (error instanceof ApiClientError) {
    handleError(error);
  }
}
```

### Pagination Utilities

```typescript
import { 
  PaginatedResponse,
  flattenPages,
  getNextPageParam,
  getTotalFromPages,
} from '@queroplantao/api-client';

// For infinite queries (manual setup)
const allItems = flattenPages(data?.pages);
const total = getTotalFromPages(data?.pages);
```

## Exports

| Path | Contents |
|------|----------|
| `@queroplantao/api-client` | Main entry: hooks, models, utilities |
| `@queroplantao/api-client/enums` | Enums with PT-BR labels |
| `@queroplantao/api-client/i18n` | Error codes and messages |

## Development

### Generate Client

First, ensure the API is running locally:

```bash
# In the API project root
make run
```

Then generate the client:

```bash
# Generate everything
make client-all

# Or individually:
make client-enums    # TypeScript enums from Python
make client-errors   # Error codes and i18n messages
make client-generate # API client from OpenAPI
```

### Build

```bash
cd packages/api-client
pnpm install
pnpm run build
```
