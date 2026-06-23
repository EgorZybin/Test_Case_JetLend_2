# JetLend Mailing Import

Django-проект для импорта рассылок из XLSX и последующей отправки писем.

Стек: **Python 3.12**, **Django 4.2+**, **PostgreSQL 16**, **Docker Compose**.

## Быстрый старт (Docker)

```bash
cp .env.example .env
docker compose up --build
```

Приложение: http://localhost:8000  
Admin: http://localhost:8000/admin/

Миграции применяются автоматически при старте контейнера `web`.

## Импорт рассылок

Подготовьте XLSX-файл. Первая строка — заголовки:

| Колонка     | Описание                              |
|-------------|---------------------------------------|
| external_id | Уникальный ID записи во внешней системе |
| user_id     | ID пользователя                       |
| email       | Email получателя                      |
| subject     | Тема письма                           |
| message     | Текст письма                          |

Пример файла:

```bash
python scripts/create_sample_xlsx.py
```

Импорт в контейнере:

```bash
docker compose exec web python manage.py import_mailings samples/mailings.sample.xlsx
```

Или одноразовый запуск без поднятого `web`:

```bash
docker compose run --rm web python manage.py import_mailings samples/mailings.sample.xlsx
```

Пример вывода:

```text
Import finished.
Processed rows: 100
Created records: 80
Skipped records: 15
Error rows: 5
```

### Поведение

- `external_id` используется для идемпотентности: повторный импорт той же записи пропускается.
- Пустые строки игнорируются.
- Ошибки валидации и сбои отправки учитываются в `Error rows`.
- Отправка письма симулируется: случайная задержка 5–20 секунд и запись в лог.

## Тесты

```bash
docker compose run --rm web python manage.py test mailings
```

В тестах задержка отправки отключена через `MAILING_SEND_DELAY_RANGE = (0, 0)`.

## Локальная разработка (app на хосте, PostgreSQL из compose)

```bash
cp .env.example .env
docker compose up -d db
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# в .env для локального запуска:
# POSTGRES_HOST=localhost

python manage.py migrate
python manage.py runserver
```

## Структура

```text
build/
  Dockerfile                        # образ приложения
  entrypoint.sh                     # wait-for-postgres + migrate
.env.example                        # шаблон переменных окружения
docker-compose.yaml                 # orchestration (web + db)
mailings/
  models.py                         # MailingRecord
  services/
    email_sender.py                 # send_email()
    import_service.py               # MailingImportService
  management/commands/
    import_mailings.py              # management command
  tests/                            # unit/integration tests
```

## Admin

```bash
docker compose exec web python manage.py createsuperuser
```

Записи доступны в `/admin/mailings/mailingrecord/`.
