# Módulo de Unidades (Units)

## Visão Geral

O módulo de unidades gerencia os locais físicos onde os profissionais realizam suas atividades. As unidades são os hospitais, clínicas, UPAs, etc. onde ocorrem plantões, vagas são criadas e o controle de ponto é realizado.

Cada unidade pertence a uma organização (isolamento multi-tenant) e pode opcionalmente estar vinculada a uma Company para fins legais/administrativos. Unidades podem ter múltiplos setores (UTI, Emergência, Centro Cirúrgico, etc.).

## Diagrama ER

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                              ESTRUTURA DE UNIDADES                                       │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                         │
│  ┌──────────────────┐                                                                   │
│  │   Organization   │                                                                   │
│  └──────────────────┘                                                                   │
│          │                                                                              │
│         1:N                                                                             │
│          ▼                                                                              │
│  ┌──────────────────┐           ┌──────────────────┐                                    │
│  │       Unit       │──N:1(opt)─│     Company      │                                    │
│  │ (Local de Trab.) │           │ (Entidade Legal) │                                    │
│  └──────────────────┘           └──────────────────┘                                    │
│          │                                                                              │
│         1:N                                                                             │
│          ▼                                                                              │
│  ┌──────────────────┐                                                                   │
│  │      Sector      │                                                                   │
│  │ (Setor/Depto)    │                                                                   │
│  └──────────────────┘                                                                   │
│                                                                                         │
│  ┌──────────────────────────────────────────────────────────────────────────────────┐   │
│  │                           GEOFENCING                                             │   │
│  │                                                                                  │   │
│  │  Unit: latitude, longitude, geofence_radius_meters                               │   │
│  │                    │                                                             │   │
│  │                    ▼                                                             │   │
│  │  Sector: latitude, longitude, geofence_radius_meters (override opcional)         │   │
│  │          Se NULL → herda da Unit                                                 │   │
│  │                                                                                  │   │
│  └──────────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                         │
│  ┌──────────────────────────────────────────────────────────────────────────────────┐   │
│  │                           USO EM OUTROS MÓDULOS                                  │   │
│  │                                                                                  │   │
│  │  Unit ◄── ProfessionalContract (local de trabalho do contrato)                   │   │
│  │  Unit ◄── Shift (futuro: plantão ocorre em uma unidade)                          │   │
│  │  Unit ◄── JobPosting (futuro: vaga é em uma unidade)                             │   │
│  │  Unit/Sector ◄── TimeRecord (futuro: ponto registrado no local)                  │   │
│  │                                                                                  │   │
│  └──────────────────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

## Enums

### UnitType
Tipos de unidades/estabelecimentos de saúde.

| Valor | Descrição |
|-------|-----------|
| HOSPITAL | Hospital |
| CLINIC | Clínica |
| UPA | Unidade de Pronto Atendimento |
| UBS | Unidade Básica de Saúde |
| EMERGENCY_ROOM | Pronto Socorro |
| LABORATORY | Laboratório |
| HOME_CARE | Home Care / Atendimento Domiciliar |
| SURGERY_CENTER | Centro Cirúrgico |
| DIALYSIS_CENTER | Centro de Diálise |
| IMAGING_CENTER | Centro de Imagem |
| MATERNITY | Maternidade |
| REHABILITATION | Centro de Reabilitação |
| OTHER | Outros |

## Tabelas

### units

Unidades/locais de trabalho onde profissionais atuam.

| Campo | Tipo | Nullable | Descrição |
|-------|------|----------|-----------|
| id | UUID (v7) | ❌ | Primary key |
| organization_id | UUID | ❌ | FK para organizations (multi-tenant) |
| company_id | UUID | ✅ | FK para companies (entidade legal) |
| name | VARCHAR(255) | ❌ | Nome da unidade |
| code | VARCHAR(50) | ✅ | Código interno (único por org) |
| description | VARCHAR(1000) | ✅ | Detalhes adicionais |
| unit_type | UnitType | ❌ | Tipo de unidade |
| email | VARCHAR(255) | ✅ | Email de contato |
| phone | VARCHAR(20) | ✅ | Telefone (E.164) |
| geofence_radius_meters | INTEGER | ✅ | Raio do geofence em metros (0-10000) |
| is_active | BOOLEAN | ❌ | Status ativo/inativo |
| **Endereço (AddressMixin)** | | | |
| address, number, complement, neighborhood, city, state_code, postal_code, latitude, longitude | | ✅ | |
| **Verificação (VerificationMixin)** | | | |
| verified_at | TIMESTAMP | ✅ | Quando foi verificado |
| verified_by | UUID | ✅ | FK para users |
| **Tracking (TrackingMixin)** | | | |
| created_by, updated_by | UUID | ✅ | FK para users |
| **Timestamps & Soft Delete** | | | |
| created_at, updated_at, deleted_at | TIMESTAMP | ✅* | |

**Constraints:**
- UNIQUE PARTIAL INDEX: `(organization_id, code) WHERE code IS NOT NULL AND deleted_at IS NULL`

**Índices:**
- `ix_units_organization_id` - listagem por organização
- `ix_units_unit_type` - filtro por tipo

### sectors

Setores/departamentos dentro de uma unidade.

| Campo | Tipo | Nullable | Descrição |
|-------|------|----------|-----------|
| id | UUID (v7) | ❌ | Primary key |
| unit_id | UUID | ❌ | FK para units |
| name | VARCHAR(255) | ❌ | Nome do setor (ex: "UTI Adulto") |
| code | VARCHAR(50) | ✅ | Código interno (único por unit) |
| description | VARCHAR(1000) | ✅ | Detalhes adicionais |
| latitude | FLOAT | ✅ | Override de latitude |
| longitude | FLOAT | ✅ | Override de longitude |
| geofence_radius_meters | INTEGER | ✅ | Override de raio (0-10000) |
| is_active | BOOLEAN | ❌ | Status ativo/inativo |
| **Tracking (TrackingMixin)** | | | |
| created_by, updated_by | UUID | ✅ | FK para users |
| **Timestamps & Soft Delete** | | | |
| created_at, updated_at, deleted_at | TIMESTAMP | ✅* | |

**Constraints:**
- UNIQUE PARTIAL INDEX: `(unit_id, code) WHERE code IS NOT NULL AND deleted_at IS NULL`

**Índices:**
- `ix_sectors_unit_id` - listagem por unidade

## Regras de Negócio

### Multi-Tenancy

1. Cada unidade pertence a uma organização específica (`organization_id` obrigatório)
2. Unidades são isoladas por organização
3. O código da unidade é único dentro da organização

### Hierarquia Unit → Sector

1. Uma unidade pode ter múltiplos setores
2. Setores herdam geolocalização da unidade pai se não especificado
3. O código do setor é único dentro da unidade

### Geofencing

1. `latitude`/`longitude` definem o ponto central do geofence
2. `geofence_radius_meters` define o raio de validação para ponto
3. Setor pode sobrescrever geolocalização da Unit (campus grandes)
4. Propriedades `effective_*` no Sector retornam valor próprio ou herdado

### Vinculação a Company

1. Uma Unit pode opcionalmente ter um `company_id`
2. Útil quando a unidade tem uma entidade legal diferente da organização
3. Exemplo: Terceirizadora gerencia múltiplas unidades de diferentes hospitais

## Arquivos de Implementação

```
src/modules/units/
├── __init__.py
├── domain/
│   ├── __init__.py
│   └── models/
│       ├── __init__.py
│       ├── enums.py          # UnitType
│       ├── unit.py           # Unit model
│       └── sector.py         # Sector model
├── infrastructure/
│   ├── __init__.py
│   └── repositories/
│       └── __init__.py
├── presentation/
│   └── __init__.py
└── use_cases/
    └── __init__.py
```

## Mixins Utilizados

| Mixin | Campos | Usado em |
|-------|--------|----------|
| PrimaryKeyMixin | id (UUID v7) | Unit, Sector |
| TimestampMixin | created_at, updated_at | Unit, Sector |
| SoftDeleteMixin | deleted_at | Unit, Sector |
| TrackingMixin | created_by, updated_by | Unit, Sector |
| AddressMixin | address, ..., latitude, longitude | Unit |
| VerificationMixin | verified_at, verified_by | Unit |

## Fluxos Principais

### Fluxo de Cadastro de Unidade

```
1. Organização cria Unit (nome, tipo, endereço)
2. [Opcional] Vincula a uma Company existente
3. [Opcional] Define geofence para validação de ponto
4. Adiciona setores conforme necessário
5. Unit pode ser usada em contratos, plantões, vagas
```

### Fluxo de Geolocalização

```
1. Unit define latitude/longitude/raio do geofence
2. Ao criar Sector:
   a. Se lat/lng NULL → herda da Unit (mesmo local)
   b. Se lat/lng definido → override (local diferente)
3. Validação de ponto usa effective_latitude/longitude/geofence_radius
```
