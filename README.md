# Task Planner

Проект разделен на два независимых слоя:

- `backend/` - Django + DRF API (один бэкенд для всего приложения).
- `frontend/` - Vue 3 + Vite клиент, работающий только через API.

## Структура

- `backend/manage.py`
- `backend/taskplanner/` - настройки и роутинг Django
- `backend/tasks/` - бизнес-логика и API endpoints
- `frontend/src/` - интерфейс

## Запуск backend

```bash
cd backend
python manage.py migrate
python manage.py runserver
```

API доступно на `http://localhost:8000/api/`.

## Запуск frontend

```bash
cd frontend
npm install
npm run dev
```

По умолчанию фронт отправляет запросы в `http://localhost:8000/api`.
При необходимости можно переопределить URL через `frontend/.env`:

```env
VITE_API_BASE_URL=http://localhost:8000/api
```