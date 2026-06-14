# Beatris Backend

## 1. Что это за проект

Beatris Backend — серверная часть веб-приложения медицинского центра Beatris.

Проект реализует REST API для следующих задач:

- вывод информации о клинике;
- регистрация и авторизация пользователей;
- работа с ролями пациента, врача и администратора;
- просмотр услуг и специалистов;
- онлайн-запись на приём;
- расчёт свободных слотов по расписанию специалиста;
- каталог товаров;
- избранное;
- корзина;
- оформление заказов;
- создание оплаты через временную payment-заглушку;
- рекомендации врача пациенту;
- административное управление данными.

Это не абстрактный каркас FastAPI, а текущая серверная реализация проекта Beatris, собранная вокруг схемы `SQL_Beatrice_simple.sql` и OpenAPI-контракта.

## 2. Текущий этап

На данный момент backend уже собран и покрывает основные модули проекта.

| Часть проекта | Состояние |
| --- | --- |
| SQL-схема | подготовлена в `SQL_Beatrice_simple.sql` |
| SQLAlchemy-модели | реализованы в `app/models.py` |
| Pydantic-схемы | реализованы в `app/schemas.py` |
| Репозитории БД | реализованы в `app/repositories.py` |
| Сериализация SQL -> JSON | реализована в `app/serializers.py` |
| JWT-аутентификация | реализована в `app/core/security.py` |
| API-маршруты | реализованы в `app/api/routers/` |
| Alembic | настроен, есть начальная миграция |
| Seed-данные | подготовлены в `app/seed.py` |
| Текущая задача | запуск проекта и проверка через Swagger |

Frontend как отдельный этап ещё не начинался. В корне проекта есть временные файлы `admin.html`, `admin.css`, `admin.js`, которые отдаются через FastAPI, но основной фокус сейчас остаётся на backend.

## 3. Технологии

Серверная часть разработана на Python с использованием FastAPI. Для описания структур запросов и ответов используется Pydantic. Взаимодействие с базой данных выполняется через SQLAlchemy ORM. Управление изменениями структуры базы данных реализовано с помощью Alembic.

| Назначение | Используется |
| --- | --- |
| Backend framework | FastAPI |
| ASGI server | Uvicorn |
| Валидация данных | Pydantic |
| ORM | SQLAlchemy |
| Миграции | Alembic |
| База данных | MySQL |
| MySQL-драйвер | PyMySQL |
| Конфигурация | `.env`, `python-dotenv` |
| Авторизация | JWT access token + refresh token |
| Хеширование паролей | PBKDF2-SHA256 |

## 4. Структура проекта

```text
.
├── alembic/
│   ├── versions/
│   │   └── 20260511_0001_initial_simple_schema.py
│   ├── env.py
│   └── script.py.mako
├── app/
│   ├── api/
│   │   ├── deps.py
│   │   └── routers/
│   │       ├── admin.py
│   │       ├── appointments.py
│   │       ├── auth.py
│   │       ├── cart.py
│   │       ├── clinic.py
│   │       ├── doctor.py
│   │       ├── health.py
│   │       ├── orders.py
│   │       ├── products.py
│   │       ├── recommendations.py
│   │       ├── reviews.py
│   │       ├── services.py
│   │       ├── specialists.py
│   │       ├── users.py
│   │       └── wishlist.py
│   ├── core/
│   │   ├── config.py
│   │   ├── database.py
│   │   └── security.py
│   ├── appointment_slots.py
│   ├── main.py
│   ├── models.py
│   ├── migration_guards.py
│   ├── repositories.py
│   ├── schemas.py
│   ├── serializers.py
│   └── seed.py
├── .dockerignore
├── alembic.ini
├── admin-config.js
├── admin.css
├── admin.html
├── admin.js
├── Dockerfile
├── README.md
├── requirements.txt
└── SQL_Beatrice_simple.sql
```

Назначение ключевых файлов:

| Файл | Роль в проекте |
| --- | --- |
| `app/main.py` | создаёт FastAPI-приложение и подключает общий router |
| `app/api/routers/__init__.py` | собирает все маршруты под префиксом `/api/v1` |
| `app/api/deps.py` | зависимости для БД, текущего пользователя, ролей admin/doctor |
| `app/models.py` | описание таблиц БД через SQLAlchemy |
| `app/schemas.py` | Pydantic-модели запросов и ответов |
| `app/repositories.py` | вся основная работа с БД |
| `app/serializers.py` | преобразование SQLAlchemy-объектов в camelCase JSON |
| `app/appointment_slots.py` | расчёт свободных интервалов записи |
| `app/seed.py` | тестовые данные для локального запуска |
| `app/core/security.py` | пароли, access token, refresh token |
| `app/core/database.py` | engine и session SQLAlchemy |

## 5. База данных

Текущая схема базы данных описана в:

```text
SQL_Beatrice_simple.sql
```

В SQLAlchemy-моделях сейчас описаны 18 таблиц:

| Таблица | Назначение |
| --- | --- |
| `clinic_info` | основная информация о медицинском центре |
| `users` | пациенты, врачи и администраторы |
| `refresh_tokens` | refresh-токены пользователей |
| `service_categories` | категории услуг |
| `services` | услуги клиники |
| `specialists` | специалисты медицинского центра |
| `specialist_services` | связь специалистов с услугами |
| `appointments` | записи на приём |
| `doctor_schedule` | расписание специалистов |
| `product_categories` | категории товаров |
| `products` | товары |
| `wishlist_items` | избранные товары пользователя |
| `cart_items` | позиции корзины |
| `orders` | заказы |
| `order_items` | позиции заказа |
| `payments` | оплаты заказов |
| `recommendations` | рекомендации врача |
| `reviews` | отзывы |

Основные принципы схемы:

- идентификаторы сущностей хранятся как UUID-строки;
- поля таблиц записаны в `snake_case`;
- ответы API возвращаются в `camelCase`;
- связи между сущностями оформлены внешними ключами;
- связи многие-ко-многим вынесены в отдельные таблицы;
- цены и суммы хранятся как `DECIMAL(10,2)`.

## 6. Роли и права

В проекте используются три роли:

| Роль | Возможности |
| --- | --- |
| `patient` | профиль, запись на приём, избранное, корзина, заказы, просмотр своих рекомендаций |
| `doctor` | просмотр своего расписания, просмотр своих записей, создание рекомендаций |
| `admin` | управление пользователями, услугами, специалистами, расписанием, товарами, заказами и записями |

Проверка ролей находится в `app/api/deps.py`.

Администратор для локальной проверки создаётся через `app/seed.py`:

```test
phone: +77000000000
password: admin12345
```

## 7. Авторизация

Авторизация реализована в модуле `app/api/routers/auth.py`.

Маршруты:

| Метод | Путь | Назначение |
| --- | --- | --- |
| `POST` | `/api/v1/auth/register` | регистрация пользователя |
| `POST` | `/api/v1/auth/login` | вход пользователя |
| `POST` | `/api/v1/auth/refresh` | обновление access token |
| `POST` | `/api/v1/auth/logout` | выход пользователя |
| `GET` | `/api/v1/auth/me` | получение текущего пользователя |

После входа клиент получает access token и использует его в заголовке:

```text
Authorization: Bearer <access_token>
```

Refresh token сохраняется в cookie и хранится в базе в виде хеша.

## 8. Пользовательские API-модули

Все основные маршруты подключаются с префиксом:

```text
/api/v1
```

### Клиника

| Метод | Путь | Назначение |
| --- | --- | --- |
| `GET` | `/api/v1/clinic-info` | получить информацию о клинике |

### Услуги

| Метод | Путь | Назначение |
| --- | --- | --- |
| `GET` | `/api/v1/service-categories` | получить категории услуг |
| `GET` | `/api/v1/services` | получить список услуг |
| `GET` | `/api/v1/services/{slug}` | получить услугу по slug |

### Специалисты

| Метод | Путь | Назначение |
| --- | --- | --- |
| `GET` | `/api/v1/specialists` | получить список специалистов |
| `GET` | `/api/v1/specialists/{id}` | получить специалиста по id |

### Записи на приём

| Метод | Путь | Назначение |
| --- | --- | --- |
| `GET` | `/api/v1/appointments/my` | получить свои записи |
| `GET` | `/api/v1/appointments/available-slots` | получить свободные слоты |
| `POST` | `/api/v1/appointments` | создать запись |
| `PATCH` | `/api/v1/appointments/{id}/cancel` | отменить свою запись |

### Товары

| Метод | Путь | Назначение |
| --- | --- | --- |
| `GET` | `/api/v1/product-categories` | получить категории товаров |
| `GET` | `/api/v1/products` | получить список товаров |
| `GET` | `/api/v1/products/{slug}` | получить товар по slug |

### Профиль

| Метод | Путь | Назначение |
| --- | --- | --- |
| `GET` | `/api/v1/users/me` | получить профиль |
| `PATCH` | `/api/v1/users/me` | обновить профиль |

### Избранное

| Метод | Путь | Назначение |
| --- | --- | --- |
| `GET` | `/api/v1/wishlist` | получить избранное |
| `POST` | `/api/v1/wishlist/items` | добавить товар в избранное |
| `DELETE` | `/api/v1/wishlist/items/{productId}` | удалить товар из избранного |

### Корзина

| Метод | Путь | Назначение |
| --- | --- | --- |
| `GET` | `/api/v1/cart` | получить корзину |
| `POST` | `/api/v1/cart/items` | добавить товар в корзину |
| `PATCH` | `/api/v1/cart/items/{itemId}` | изменить количество |
| `DELETE` | `/api/v1/cart/items/{itemId}` | удалить позицию |

### Заказы

| Метод | Путь | Назначение |
| --- | --- | --- |
| `POST` | `/api/v1/orders` | создать заказ из корзины |
| `GET` | `/api/v1/orders/my` | получить свои заказы |
| `GET` | `/api/v1/orders/{id}` | получить заказ по id |
| `POST` | `/api/v1/orders/{id}/payment` | создать оплату заказа |

### Рекомендации

| Метод | Путь | Назначение |
| --- | --- | --- |
| `GET` | `/api/v1/recommendations/my` | получить свои рекомендации |
| `POST` | `/api/v1/recommendations` | создать рекомендацию пациенту |

### Кабинет врача

| Метод | Путь | Назначение |
| --- | --- | --- |
| `GET` | `/api/v1/doctor/schedule` | получить расписание текущего врача |
| `GET` | `/api/v1/doctor/appointments` | получить записи текущего врача |

## 9. Административные API-модули

Все маршруты админки находятся в `app/api/routers/admin.py` и доступны только роли `admin`.

Основные группы:

| Группа | Маршруты |
| --- | --- |
| Клиника | `PATCH /api/v1/admin/clinic-info` |
| Пользователи | `GET/POST /api/v1/admin/users`, `GET/PATCH/DELETE /api/v1/admin/users/{id}` |
| Специалисты | `GET/POST /api/v1/admin/specialists`, `GET/PATCH/DELETE /api/v1/admin/specialists/{id}` |
| Расписание | `GET/POST /api/v1/admin/doctor-schedule`, `GET/PATCH/DELETE /api/v1/admin/doctor-schedule/{id}` |
| Заказы | `GET /api/v1/admin/orders`, `GET /api/v1/admin/orders/{id}`, `PATCH /api/v1/admin/orders/{id}` |
| Рекомендации | `GET/POST /api/v1/admin/recommendations`, `GET/PATCH/DELETE /api/v1/admin/recommendations/{id}` |
| Товары | `GET/POST /api/v1/admin/products`, `GET/PATCH/DELETE /api/v1/admin/products/{id}` |
| Услуги | `GET/POST /api/v1/admin/services`, `GET/PATCH/DELETE /api/v1/admin/services/{id}` |
| Записи | `GET /api/v1/admin/appointments`, `PATCH /api/v1/admin/appointments/{id}` |

Удаление справочников сделано как мягкое отключение:

- услуга: `services.is_active = false`;
- специалист: `specialists.is_active = false`;
- товар: `products.is_active = false`;
- расписание: `doctor_schedule.is_available = false`.

## 10. Онлайн-запись

Логика записи реализована в:

```text
app/api/routers/appointments.py
app/appointment_slots.py
app/repositories.py
```

При расчёте свободных слотов backend учитывает:

- выбранного специалиста;
- выбранную услугу;
- дату;
- длительность услуги;
- расписание специалиста;
- уже занятые записи;
- отменённые записи не блокируют слот.

Типовой сценарий:

1. Получить услугу через `/api/v1/services`.
2. Получить специалиста через `/api/v1/specialists`.
3. Запросить свободные слоты через `/api/v1/appointments/available-slots`.
4. Создать запись через `POST /api/v1/appointments`.

## 11. Заказы и оплата

Корзина и заказы реализованы через таблицы:

- `cart_items`;
- `orders`;
- `order_items`;
- `payments`.

Типовой сценарий:

1. Пользователь добавляет товар в корзину.
2. Backend сохраняет цену и subtotal в `cart_items`.
3. При создании заказа позиции корзины переносятся в `order_items`.
4. В заказе фиксируются получатель, телефон, адрес доставки и итоговая сумма.
5. Через `/api/v1/orders/{id}/payment` создаётся запись оплаты.

Текущая оплата — временная заглушка, а не интеграция с реальным платёжным провайдером.

### 11.1. Механика: товар не «переносится», а копируется

Карточка товара не перемещается из раздела товаров в заказы — при оформлении создаётся её
**снимок (копия)** в таблице `order_items`. По каждой позиции корзины в `order_items`
записываются `product_title`, `product_slug`, `price`, `quantity`, `subtotal`, после чего
корзина очищается (строки `cart_items` удаляются).

Снимок нужен для того, чтобы при изменении, переименовании или удалении товара в заказе
сохранились данные на момент покупки. FK `order_items.product_id` стоит `ON DELETE SET NULL`,
поэтому удаление товара не ломает заказ.

Сборка заказа из корзины — `app/repositories.py::create_order_from_cart`.

### 11.2. Пошаговый сценарий покупки со стороны пользователя (через Swagger)

Полный путь: **регистрация → каталог → корзина → оформление → (оплата) → заказ виден администратору.**
Все запросы выполняются на `http://127.0.0.1:8000/docs`.

1. **Регистрация покупателя** — `POST /api/v1/auth/register` (роль `patient` присваивается
   автоматически). В ответе скопировать `accessToken`.

   ```json
   {
     "fullName": "Тест Покупатель",
     "phone": "+77011112233",
     "password": "test12345",
     "email": "buyer@beatris.kz"
   }
   ```

2. **Авторизация в Swagger** — кнопка **Authorize**, вставить `accessToken`. Дальнейшие
   запросы идут от имени этого пациента.

3. **Получить id товара** — `GET /api/v1/products`, скопировать `id` нужного товара
   (именно `id`, а не `slug` — корзине нужен `id`).

4. **Добавить товар в корзину** — `POST /api/v1/cart/items`.

   ```json
   {
     "productId": "<id_из_шага_3>",
     "quantity": 1
   }
   ```

5. **Оформить заказ** — `POST /api/v1/orders` (пустая корзина → `400 Cart is empty`).

   ```json
   {
     "paymentMethod": "card_online",
     "deliveryMethod": "courier",
     "deliveryAddress": "г. Атырау, ул. Абая, 10",
     "recipientName": "Тест Покупатель",
     "recipientPhone": "+77011112233",
     "comment": "тестовый заказ"
   }
   ```

   Успех → заказ со статусом `created` / оплатой `pending`, корзина очищена. В ответе придёт
   человекочитаемый `orderNumber` формата `BT-ГГММДД-NNN`.

6. **(Необязательно) Оплата-заглушка** — `POST /api/v1/orders/{id}/payment`,
   возвращает фейковый `paymentUrl`.

7. **Проверка в админке** — раздел «Заказы»: новый заказ на месте, статус меняется
   выпадающим списком в колонке «Действие».

### 11.3. Статусы заказа

| Поле | Значения |
| --- | --- |
| `order_status` | `created` · `paid` · `processing` · `delivered` · `cancelled` |
| `payment_status` | `pending` · `paid` · `failed` · `refunded` |

В HTML-админке для `order_status = processing` показывается русская подпись «В отправке»
(код-значение в БД и API остаётся `processing` — литералы статусов фиксированы OpenAPI-контрактом).
Заказы не удаляются как CRUD-действие — управление идёт только сменой статуса.

### 11.4. Номер заказа и способы оплаты/доставки

Помимо технического UUID (`id`), у заказа есть человекочитаемый **`order_number`** —
формат `BT-ГГММДД-NNN` (префикс `BT`, дата, порядковый за день, напр. `BT-260605-001`).
Поле уникально, генерируется при создании заказа и используется для поиска/отображения
в админке (`GET /api/v1/admin/orders?search=BT-26...`).

Также заказ хранит два бизнес-поля, выбираемых и клиентом, и админом при создании:

| Поле | Значения |
| --- | --- |
| `payment_method` | `card_online` (картой онлайн) · `cash_on_delivery` (наличными при получении) |
| `delivery_method` | `courier` (курьер) · `pickup` (самовывоз) |

> `payment_method` — это *способ* оплаты, не путать с `payment_status` (*состояние* оплаты).
> Схема добавлена миграцией `20260605_0001`. Поля выходят за рамки `openapi.yaml` (by design).

## 12. Рекомендации врача

Рекомендации хранятся в таблице `recommendations`.

К рекомендации можно прикреплять товары через таблицу `recommendation_products`.

Рекомендацию может создать:

- врач через `/api/v1/recommendations`;
- администратор через `/api/v1/admin/recommendations`.

Пациент получает свои рекомендации через:

```text
GET /api/v1/recommendations/my
```

### Гостевой (первичный) пациент

Рекомендацию можно создать и для первичного пациента без аккаунта. Для этого `recommendations.patient_id` сделан необязательным (миграция `20260527_0001`), а `patientId` в `CreateRecommendationRequest` — необязательным полем. В этом случае «личность» пациента берётся из привязанной записи на приём (`appointment.patient_name` / `patient_phone`), и ответ содержит `patientName` / `patientPhone`, а `patientId` приходит `null`.

Это намеренное расхождение с `openapi.yaml` (там `patientId` обязателен). Полный список таких расхождений по полям — в `AGENTS.md`, раздел 6.

## 13. Настройка `.env`

Пример настроек находится в `.env.example`:

```text
DATABASE_URL=mysql+pymysql://beatris:beatris@127.0.0.1:3306/beatris?charset=utf8mb4
SECRET_KEY=change-me-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
REFRESH_COOKIE_SECURE=false
```

Для локального запуска нужно указать данные своей MySQL-базы в `DATABASE_URL`.

Формат:

```text
mysql+pymysql://<login>:<password>@<host>:<port>/<database>?charset=utf8mb4
```

## 14. Установка зависимостей

Создать виртуальное окружение:

```powershell
python -m venv .venv
```

Активировать окружение:

```powershell
.\.venv\Scripts\Activate.ps1
```

Установить зависимости:

```powershell
pip install -r requirements.txt
```

Если PowerShell не видит `alembic.exe`, сначала проверить, что зависимости установлены именно в `.venv`.

## 15. Миграции

Проверить текущую миграцию:

```powershell
.\.venv\Scripts\alembic.exe current
```

Проверить head:

```powershell
.\.venv\Scripts\alembic.exe heads
```

Применить миграции:

```powershell
.\.venv\Scripts\alembic.exe upgrade head
```

Текущая миграция:

```text
20260511_0001_initial_simple_schema.py
```

Базу данных не нужно создавать заново, если она уже существует.

## 16. Seed-данные

Заполнить базу тестовыми данными:

```powershell
.\.venv\Scripts\python.exe -m app.seed
```

Seed добавляет:

- информацию о клинике Beatris;
- администратора;
- 3 категории услуг;
- 3 услуги;
- 2 специалистов;
- 4 связи специалист-услуга;
- 2 расписания специалистов;
- 1 тестовую запись.

## 17. Запуск

Запустить backend:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

После запуска открыть:

| Адрес | Назначение |
| --- | --- |
| `http://127.0.0.1:8000/docs` | Swagger UI |
| `http://127.0.0.1:8000/redoc` | ReDoc |
| `http://127.0.0.1:8000/openapi.json` | OpenAPI JSON |
| `http://127.0.0.1:8000/admin.html` | временная HTML-админка |

## 18. Проверка после запуска

Минимальный порядок ручной проверки:

1. Запустить backend.
2. Открыть Swagger: `http://127.0.0.1:8000/docs`.
3. Выполнить `POST /api/v1/auth/login` под администратором.
4. Вставить access token в Swagger Authorize.
5. Проверить `GET /api/v1/auth/me`.
6. Проверить `GET /api/v1/services`.
7. Проверить `GET /api/v1/specialists`.
8. Проверить `GET /api/v1/appointments/available-slots`.
9. Создать запись через `POST /api/v1/appointments`.
10. Проверить админский список записей через `GET /api/v1/admin/appointments`.

Проверить синтаксис Python-кода:

```powershell
.\.venv\Scripts\python.exe -m compileall app alembic
```

## 19. Что важно не перепутать

- `routers` лежит внутри `app/api`, потому что это HTTP-слой API.
- `deps.py` нужен для общих зависимостей FastAPI: БД, текущий пользователь, роли.
- Админ входит через обычный `/auth/login`, отдельного входа для админа нет.
- `SQL_Beatrice_simple.sql` — текущая рабочая SQL-схема.
- `SQL_Beatrice_aligned.sql` и другие SQL-файлы не должны становиться источником истины без отдельного решения.
- Если база уже существует, не нужно создавать её заново.
- Frontend пока не является основным этапом.

## 20. Краткая формулировка для пояснительной записки

Серверная часть веб-приложения медицинского центра Beatris разработана на языке Python с использованием фреймворка FastAPI. Приложение реализует REST API для авторизации пользователей, работы с каталогом услуг и специалистов, онлайн-записи на приём, оформления заказов, рекомендаций врача и административного управления данными.

Для описания структур входящих и исходящих данных используется библиотека Pydantic. Взаимодействие с базой данных MySQL выполняется с помощью ORM-библиотеки SQLAlchemy, что позволяет описывать таблицы базы данных в виде Python-классов и работать с ними на уровне объектов. Управление изменениями структуры базы данных реализовано с использованием Alembic.
