# Quero Plantão - Documento de Contexto

## 1. Visão Geral do Sistema

**Quero Plantão** é uma plataforma SaaS para busca e publicação de vagas de plantões médicos. O sistema conecta médicos em busca de oportunidades de trabalho com gestores de escala de hospitais, clínicas e consultórios.

### 1.1 Analogias

- **Indeed/Glassdoor**: Busca e publicação de vagas
- **Uber**: Sistema de matching entre disponibilidade do médico e necessidade do gestor

---

## 2. Documentação por Módulo

A documentação detalhada de cada módulo está em arquivos separados:

| Módulo | Arquivo | Status |
|--------|---------|--------|
| **Autenticação e Autorização** | [AUTH_MODULE.md](modules/AUTH_MODULE.md) | ✅ Implementado |
| **Profissionais** | [PROFESSIONALS_MODULE.md](modules/PROFESSIONALS_MODULE.md) | ✅ Implementado |
| **Organizações** | [ORGANIZATIONS_MODULE.md](modules/ORGANIZATIONS_MODULE.md) | ✅ Implementado |
| **Escalas e Plantões** | modules/SHIFTS_MODULE.md | 🔜 Planejado |
| **Vagas e Candidaturas** | modules/JOB_POSTINGS_MODULE.md | 🔜 Planejado |
| **Disponibilidade e Matching** | modules/MATCHING_MODULE.md | 🔜 Planejado |
| **Ponto e Pagamentos** | modules/PAYMENTS_MODULE.md | 🔜 Planejado |
| **Notificações** | modules/NOTIFICATIONS_MODULE.md | 🔜 Planejado |

---

## 3. Personas

### 3.1 Profissional de Saúde (Professional)
- Busca vagas de plantões
- Publica seus horários disponíveis (escala reversa)
- Bate ponto via geolocalização
- Visualiza recebimentos
- Pode atuar também como gestor
- Tipos: Médico, Enfermeiro, Técnico de Enfermagem, etc.

### 3.2 Gestor de Escala (Scale Manager)
- Gerencia escalas de plantões
- Cria plantões com horários, valores e especialidades
- Publica anúncios de vagas
- Controla entrada/saída dos médicos
- Visualiza pagamentos devidos

---

## 4. Conceitos do Domínio

### 4.1 Hierarquia Organizacional

```
Organização (Organization)
    └── Unidade (Unit) - Ex: Hospital X, Clínica Y, Ala Sul
            └── Setor (Sector) - Ex: UTI, Sala de Emergência, Cardiologia
                    └── Escala (Schedule)
                            └── Plantão (Shift)
                                    └── Anúncio de Vaga (Job Posting)
```

### 4.2 Definições

| Termo | Descrição |
|-------|-----------|
| **Organization** | Entidade principal (hospital, rede de clínicas, etc.) |
| **Unit** | Local físico dentro da organização (filial, ala, prédio) |
| **Sector** | Subdivisão da unidade (sala, especialidade, departamento) |
| **Schedule** | Agenda de plantões de um setor específico |
| **Shift** | Plantão individual com horário, valor e especialidade |
| **Job Posting** | Anúncio público de vaga derivado de um plantão |
| **Availability** | Horários disponíveis informados pelo médico (escala reversa) |
| **Time Record** | Registro de ponto (entrada/saída) com geolocalização |

---

## 5. Diagrama ER (Visão Geral)

### 5.1 Autenticação & Permissões

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                    AUTENTICAÇÃO & PERMISSÕES                            │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                         │
│  ┌──────────┐      ┌──────────────────┐      ┌──────────┐      ┌───────────────────┐   │
│  │   User   │──N:N─│   user_roles     │──N:1─│   Role   │──1:N─│ role_permissions  │   │
│  └──────────┘      └──────────────────┘      └──────────┘      └───────────────────┘   │
│       │                                                                │               │
│       │            ┌──────────────────────┐                            │               │
│       └─────N:N────│  user_permissions    │──N:1───────────────────────┘               │
│                    └──────────────────────┘                     ┌────────────┐         │
│                                                                 │ Permission │         │
│                                                                 └────────────┘         │
└─────────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                              ESTRUTURA ORGANIZACIONAL (Multi-Tenant)                    │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                         │
│  ┌──────────────┐◄─────────────────────┐                                                │
│  │ Organization │ (self-ref: parent_id)│                                                │
│  └──────────────┘──────────────────────┘                                                │
│         │                                                                               │
│    ┌────┴────┬────────────────┐                                                         │
│   1:N       1:N              N:1                                                        │
│    │         │                │                                                         │
│    ▼         ▼                ▼                                                         │
│  ┌────────────────┐  ┌────────────────────────┐  ┌───────────┐                          │
│  │ Organization   │  │ OrganizationProfessional│  │  Company  │                          │
│  │    Member      │  │     (multi-tenant)      │  │           │                          │
│  └────────────────┘  └────────────────────────┘  └───────────┘                          │
│         │                     │                        │                                │
│        N:1                   1:N                      1:N                               │
│         │                     │                        │                                │
│    ┌──────────┐       ┌───────────────────┐     ┌───────────┐                           │
│    │   User   │       │ ProfessionalQualif │     │   Bank    │                           │
│    └──────────┘       └───────────────────┘     │  Account  │                           │
│                              │                  └───────────┘                           │
│                         ┌────┴────┐                                                     │
│                        1:N       1:N                                                    │
│                         │         │                                                     │
│            ┌────────────────┐  ┌───────────────────┐                                    │
│            │ProfSpecialty   │  │ProfEducation      │                                    │
│            └────────────────┘  └───────────────────┘                                    │
│                   │                                                                     │
│                  N:1                                                                    │
│                   │                                                                     │
│            ┌───────────┐                                                                │
│            │ Specialty │                                                                │
│            └───────────┘                                                                │
└─────────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                    PLANTÕES & VAGAS (🔜 Planejado)                      │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                         │
│  ┌────────────┐      ┌─────────┐      ┌─────────────┐                                   │
│  │  Schedule  │──1:N─│  Shift  │──0:1─│ Job Posting │                                   │
│  └────────────┘      └─────────┘      └─────────────┘                                   │
│                           │                  │                                          │
│                          1:N                N:N                                         │
│                           │                  │                                          │
│                    ┌─────────────┐    ┌──────────────────┐                              │
│                    │ Time Record │    │ Job Application  │                              │
│                    └─────────────┘    └──────────────────┘                              │
│                           │                  │                                          │
│                          N:1                N:1                                         │
│                           │                  │                                          │
│                           └────────┬─────────┘                                          │
│                                    │                                                    │
│                         ┌──────────────────────────┐                                    │
│                         │ OrganizationProfessional │                                    │
│                         └──────────────────────────┘                                    │
└─────────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                 MATCHING & DISPONIBILIDADE (🔜 Planejado)               │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                         │
│  ┌──────────────────────────┐      ┌──────────────┐      ┌─────────────┐                │
│  │ OrganizationProfessional │──1:N─│ Availability │──N:N─│ Job Posting │──> Match Score │
│  └──────────────────────────┘      └──────────────┘      └─────────────┘                │
│                                                                                         │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 6. Esquema de Tabelas

> **Nota:** O esquema detalhado de cada módulo está nos documentos específicos:
> - [AUTH_MODULE.md](modules/AUTH_MODULE.md) - Tabelas: users, permissions, roles, role_permissions, user_roles, user_permissions
> - [PROFESSIONALS_MODULE.md](modules/PROFESSIONALS_MODULE.md) - Tabelas: specialties, organization_professionals, professional_qualifications, professional_specialties, professional_educations, professional_documents, professional_companies
> - [ORGANIZATIONS_MODULE.md](modules/ORGANIZATIONS_MODULE.md) - Tabelas: organizations, organization_members, companies, banks, bank_accounts

Os demais módulos (Shifts, Job Postings, etc.) serão documentados conforme forem implementados.

---

## 7. Regras de Negócio

### 7.1 Autenticação e Autorização

1. **Firebase Auth** é usado apenas para autenticação (login/logout)
2. **Roles e Permissions** são gerenciadas internamente na API
3. Um usuário pode ter múltiplas roles (médico + gestor)
4. Permissions podem vir de:
   - Roles atribuídas ao usuário
   - Permissions standalone atribuídas diretamente
5. A lista final de permissions é a união de todas as fontes

### 7.2 Geolocalização e Ponto

1. O **geofence** é configurado por Unit ou Sector
2. Se o Sector não tem coordenadas, herda da Unit
3. O check-in/out só é válido se estiver dentro do raio configurado
4. O cálculo de pagamento é: `(worked_minutes / 60) * hourly_rate`
5. O tempo trabalhado pode ser menor ou maior que o definido no plantão

### 7.3 Plantões e Vagas

1. Plantões podem pertencer a uma Schedule ou serem avulsos
2. Vagas (Job Postings) podem ser criadas a partir de um Shift ou avulsas
3. Um Shift pode ter no máximo uma Job Posting ativa
4. Múltiplos Shifts podem ter o mesmo horário na mesma Schedule

### 7.4 Matching

1. O matching ocorre entre Professional Availabilities e Job Postings
2. O score considera: horário, especialidade, localização, valor e tipo de profissional
3. Matches são a principal fonte de monetização

### 7.5 Profissionais e Multi-Tenancy

1. Profissionais são **isolados por organização** (multi-tenant)
2. Cada organização mantém seus próprios registros de profissionais
3. A mesma pessoa (CPF) pode existir em múltiplas organizações com dados diferentes
4. Organizações **não podem** acessar profissionais de outras organizações
5. Um profissional pode ter múltiplas qualificações (CRM em 2 estados, ou CRM + COREN)
6. Especialidades podem ter status de residência para profissionais em formação
7. O campo `is_generalist` na especialidade identifica profissionais sem especialização
8. Documentos (diplomas, RQEs, contratos) são vinculados ao profissional, podendo ter associação opcional com qualificação ou especialidade

---

## 8. Fluxos Principais

### 8.1 Fluxo do Gestor

```
1. Criar Organization
2. Cadastrar profissionais na organização
3. Adicionar membros (ADMIN, MANAGER, SCHEDULER, VIEWER)
4. Criar Schedules (futuro: em Sectors)
5. Criar Shifts nas Schedules (ou avulsos)
6. Publicar Job Postings a partir dos Shifts
7. Receber candidaturas
8. Aceitar/Rejeitar candidatos
9. Acompanhar check-in/out
10. Aprovar pagamentos
```

### 8.2 Fluxo do Profissional

```
1. Ser cadastrado por uma organização
2. Ter perfil completado (dados pessoais, qualificações, especialidades)
3. Definir disponibilidade (escala reversa)
4. Buscar vagas / Receber matches
5. Candidatar-se às vagas
6. Ser aceito/rejeitado
7. Fazer check-in no plantão (geolocalização)
8. Fazer check-out
9. Visualizar pagamentos
```

### 8.3 Fluxo de Cadastro (Escalista)

```
1. Escalista cria organização
2. Escalista cadastra profissional com dados básicos na organização
3. Escalista pode adicionar qualificações, especialidades e documentos
4. Profissional pode receber convite para acessar a plataforma (futuro)
```

---

## 9. Considerações Técnicas

### 9.1 Stack Tecnológica

- **Backend**: Python (FastAPI) com SQLModel
- **Database**: PostgreSQL com UUID v7
- **ORM**: SQLModel (SQLAlchemy 2.0 + Pydantic)
- **Auth**: Firebase Authentication
- **Migrations**: Alembic
- **Cache**: Redis
- **Queue**: RabbitMQ
- **Mobile**: React Native / Flutter

### 9.2 Padrões de Código

- **Mixins** para reuso: `PrimaryKeyMixin`, `TimestampMixin`, `SoftDeleteMixin`, `TrackingMixin`, `AddressMixin`, `VerificationMixin`
- **UUID v7** para primary keys (ordenação temporal)
- **TYPE_CHECKING** para evitar imports circulares
- **Soft Delete** apenas onde fizer sentido (organization_professionals, organizations)
- **Multi-Tenancy** por organização para dados de profissionais

### 9.3 Extensões PostgreSQL

```sql
CREATE EXTENSION IF NOT EXISTS postgis;      -- Busca geográfica
CREATE EXTENSION IF NOT EXISTS pg_trgm;      -- Full-text search
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";  -- UUID (fallback)
```

---

## 10. Próximos Passos

1. [x] Definir models do módulo Auth
2. [x] Definir models do módulo Professionals
3. [x] Definir models do módulo Organizations
4. [x] Gerar migrations com Alembic
5. [ ] Implementar módulo Shifts/Schedules
6. [ ] Implementar módulo Job Postings
7. [ ] Criar schemas Pydantic para APIs
8. [ ] Implementar repositórios
9. [ ] Desenvolver casos de uso
10. [ ] Implementar sistema de matching
11. [ ] Desenvolver app mobile

---

## 11. Glossário

| Termo EN | Termo PT | Descrição |
|----------|----------|-----------|
| Organization | Organização | Entidade principal (hospital, clínica) |
| Unit | Unidade | Local físico (ala, filial, prédio) - 🔜 Planejado |
| Sector | Setor | Subdivisão (sala, departamento) - 🔜 Planejado |
| Schedule | Escala | Agenda de plantões |
| Shift | Plantão | Turno de trabalho individual |
| Job Posting | Vaga/Anúncio | Publicação de oportunidade |
| OrganizationProfessional | Profissional | Profissional vinculado a uma organização |
| Qualification | Qualificação | Registro em conselho profissional |
| Council | Conselho | Órgão regulador (CRM, COREN, etc.) |
| Specialty | Especialidade | Área de atuação do profissional |
| RQE | RQE | Registro de Qualificação de Especialista |
| Residency | Residência | Formação especializada (R1, R2, R3...) |
| Availability | Disponibilidade | Horários livres do profissional |
| Time Record | Registro de Ponto | Check-in/out do plantão |
| Match | Correspondência | Compatibilidade entre profissional e vaga |
| Geofence | Cerca Virtual | Área permitida para ponto |
| Multi-Tenant | Multi-Inquilino | Isolamento de dados por organização |
