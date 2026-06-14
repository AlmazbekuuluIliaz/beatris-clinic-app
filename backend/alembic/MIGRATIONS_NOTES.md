# Заметки по миграциям

## Контекст: почему часть миграций сделана идемпотентной

Начальная миграция `20260511_0001_initial_simple_schema` строит схему, **выполняя
файл `SQL_Beatrice_simple.sql`** (см. `_schema_statements()`). Этот SQL-файл — слепок
схемы, в котором уже есть часть колонок и таблиц, исторически добавлявшихся
отдельными инкрементными миграциями.

Из-за этого при запуске «с нуля» (чистая база — например, в Docker-контейнере)
начальная миграция создаёт эти объекты сразу, а более поздние миграции, которые их
добавляют, падают с `Duplicate column` / `Table already exists`. На существующих
(старых) базах это не всплывало: там схема накатывалась постепенно, SQL-файл целиком
никто не проигрывал.

## Что в SQL-снимке уже есть, а чего нет

`SQL_Beatrice_simple.sql` содержит: `service_categories.description`, `image_url`;
`orders.order_number`, `payment_method`, `delivery_method` + `uq_orders_order_number`;
таблицу `reviews` с индексом `ix_reviews_published_sort`.

В нём **нет**: `service_categories.sort_order`; `appointments.patient_contact_*`;
таблицы `appointment_status_history`.

## Какие миграции изменены, а какие оставлены как есть

Защита (idempotent-проверки) добавлена **только** тем миграциям, чьи объекты уже
есть в SQL-снимке и потому конфликтуют на чистой базе:

| Ревизия | Статус | Что обёрнуто проверкой существования |
|---|---|---|
| `20260604_0001` | **изменена** | add column `description`, `image_url` |
| `20260605_0001` | **изменена** | add column `payment_method`, `delivery_method`, `order_number`; unique `uq_orders_order_number`; бэкофилл `order_number` только если колонка добавлялась |
| `20260607_0001` | **изменена** | create table `reviews`; index `ix_reviews_published_sort` |
| `20260606_0001` | оставлена как есть | `sort_order` нет в SQL → проходит последовательно без конфликта |
| `20260609_0001` | оставлена как есть | `patient_contact_*` нет в SQL → проходит без конфликта |
| `20260609_0002` | оставлена как есть | `appointment_status_history` нет в SQL → проходит без конфликта |

**Не изменены также:** `20260511_0001` (начальная), `20260527_0001`.

Логика и порядок миграций не менялись — только добавлены проверки «существует ли
объект» перед его созданием.

## Общий модуль проверок

Чтобы не дублировать проверки по файлам, они вынесены в
[`app/migration_guards.py`](../app/migration_guards.py):

- `has_column(table, column)`
- `has_table(table)`
- `has_index(table, name)`
- `has_unique_constraint(table, name)`
- `has_check_constraint(table, name)`

Модуль `app` импортируется в `alembic/env.py`, поэтому доступен из миграций.
Изменённые миграции импортируют нужные функции из него.
