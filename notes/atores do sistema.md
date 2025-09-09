#### Atores do Sistema

- Administrador
- Usuário(Advogado)
- Cliente
- Vara
- Agenda
 /*Justiça????????*/

#### Modelagem de Atores

Visão geral (entidades)

*user_account*: pessoas do sistema (roles: admin, adv).
*client*: fichas de clientes.
*event_topic*: catálogo de tópicos de agenda (Reunião, Audiência…).
*availability_slot*: vagas abertas/fechadas na agenda do advogado.
*calendar_event*: compromissos (podem usar uma vaga).
*reminder*: lembretes de eventos (para pop-up, e-mail etc.).
*audit_log*: trilha de auditoria (o admin consulta).

**Padrões de tipos:**

IDs: UUID v4 em TEXT
Datas/horas: TEXT (ISO-8601 UTC, ex. 2025-09-08T21:00:00Z)
Booleano: INTEGER (0/1)
JSON: TEXT (validado na aplicação)

## USER_ACCOUNT

##### Administrador

- Criação de User e acesso ao registro de logs

*id* TEXT (UUID) [PK]
*name* TEXT
*email* TEXT
*email_norm* TEXT UNIQUE (lower/trim para login/busca)
*password_hash* TEXT
*role* TEXT ('admin'|'advogado') — Faz a verificação
*is_active* INTEGER (0/1, default 1)
*created_at* TEXT (ISO-8601)
*updated_at* TEXT (ISO-8601)
*deleted_at* TEXT (nullable)

##### Índices: (is_active), (email_norm)

#### User (Advogado)

- Acesso apenas a própria agenda
- Cria/Fecha vagas na agenda
- Cria compromissos na agenda baseado em tópicos:
    *Reunião
    *Audiência
    *Visita
    *Datas Proximas
- Recebe avisos pop-up(na area de notificação do computador) como lembretes de prazos de clientes e compromissos pessoais
- Cria/Edita/Inativa ficha de cliente, preenchendo todos os campos necessários

*id* TEXT (UUID) [PK]
*name* TEXT
*oab* TEXT
*email* TEXT
*email_norm* TEXT UNIQUE (lower/trim para login/busca)
*password_hash* TEXT
*role* TEXT ('admin'|'advogado') — CHECK
*is_active* INTEGER (0/1, default 1( 1 = True, Advogado em Função | 0 = False, ID Inativo no sistema))
*created_at* TEXT (ISO-8601)(Trocar pra UTC 03:00)
*updated_at* TEXT (ISO-8601)(Trocar pra UTC 03:00)
*deleted_at* TEXT (nullable)
*Índices: (is_active), (email_norm)*

#### Cliente

*id* TEXT (UUID) [PK]
*full_name* TEXT
*birth_date* TEXT
*rg_number* TEXT
*ctps_number* TEXT
*cnis_number* TEXT
*cpf_number* TEXT (CPF/CNPJ sem máscara)
*email* TEXT
*senha_gov* TEXT [pedir_credencial]
*email_norm* TEXT (opcional UNIQUE)
*phone_e164* TEXT (ex. +5532999999999)
*address_json* TEXT (rua/cidade/UF/CEP em JSON)
*notes* TEXT (Observações)
Inativação:
*is_active* INTEGER (0/1, default 1)
*inactivated_at* TEXT
*inactivated_reason* TEXT
Trilha:
*created_at, updated_at, deleted_at* TEXT
Índices: *(is_active), (full_name), (cpf_number)*

<!--event_topic (catálogo)

code TEXT PK (ex.: REUNIAO, AUDIENCIA, VISITA, DATAS_PROXIMAS)

label TEXT-->

*Alternativa: guardar o tópico direto em calendar_event.topic_code com CHECK (sem tabela).*

#### Agenda

*availability_slot* (vagas da agenda)
*id* TEXT (UUID) PK
*owner_user_id* TEXT → [FK] *user_account.id*
*starts_at* TEXT (ISO-8601)
*ends_at* TEXT (ISO-8601)
*capacity* INTEGER (default 1)
*is_open* INTEGER (0/1, default 1)
Trilha: *created_at, updated_at, deleted_at* TEXT;

Índices: (owner_user_id, starts_at).

calendar_event (compromissos)

id TEXT (UUID) PK

owner_user_id TEXT → FK user_account.id

client_id TEXT (nullable) → FK client.id

topic_code TEXT → FK event_topic.code (ou CHECK)

slot_id TEXT (nullable) → FK availability_slot.id

title TEXT

description TEXT

location TEXT

starts_at TEXT (ISO-8601)

ends_at TEXT (nullable)

status TEXT CHECK ('scheduled'|'done'|'canceled') default 'scheduled'

Trilha: created_at, updated_at, deleted_at TEXT; version INTEGER

Índices: (owner_user_id, starts_at), (client_id), (slot_id).

reminder (lembretes)

id TEXT (UUID) PK

event_id TEXT → FK calendar_event.id

fire_at TEXT (quando disparar)

channel TEXT CHECK ('popup'|'email'|'sms'|'webhook')

message TEXT

Resultado: delivered_at TEXT (nullable), is_dismissed INTEGER (0/1)

Trilha: created_at, updated_at, version INTEGER

Índices: (fire_at), (event_id).

audit_log (admin)

id INTEGER PK AUTOINCREMENT

actor_user_id TEXT (nullable) → FK user_account.id

action TEXT (ex.: CREATE|UPDATE|DELETE|LOGIN)

entity_table TEXT (ex.: client|calendar_event|availability_slot)

entity_id TEXT (UUID da linha afetada)

payload_json TEXT (snapshot resumido)

occurred_at TEXT (ISO-8601)

Índices: (occurred_at), (entity_table, entity_id).
