# Task Planner

Проект разделен на два независимых слоя:

- `backend/` - Django + DRF API (один бэкенд для всего приложения).
- `frontend/` - Vue 3 + Vite клиент, работающий только через API.

## Структура

- `backend/manage.py`
- `backend/taskplanner/` - настройки и роутинг Django
- `backend/tasks/` - бизнес-логика и API endpoints
- `frontend/src/` - интерфейс

## Запуск через Docker

Нужны [Docker](https://docs.docker.com/get-docker/) и Docker Compose v2.

### Только ПК (localhost)

1. Терминал в **корне репозитория**.
2. По желанию: `docker.env.example` → `.env` (или без `.env` — в compose уже есть разумные значения по умолчанию).
3. `docker compose up --build` → **http://localhost:3000**, API **http://localhost:8000/api**.

### ПК + телефон в одной Wi‑Fi сети

С телефона Django должен принимать запросы с заголовком `Host: ВАШ_IP` — для этого в переменных должен быть ваш IPv4. Проще всего:

**Windows (PowerShell)**, из корня репозитория — коротко (обязательно **`.\`** — иначе команда «не найдена»):

```powershell
.\docker-lan.cmd
```

То же, что `.\scripts\docker-up-lan.ps1`. Аргументы: `.\docker-lan.cmd down` и т.д. В **cmd.exe** можно написать просто `docker-lan.cmd`, если вы уже в каталоге проекта.

Скрипт создаёт **`.env.lan`** (в `.gitignore`) с определённым автоматически IPv4 и запускает `docker compose --env-file .env.lan up --build`. В консоли будет URL вида **http://192.168.x.x:3000** — откройте его на телефоне.

**Linux / WSL / Git Bash:**

```bash
bash scripts/docker-up-lan.sh
```

Ручной вариант без скриптов: скопируйте **`lan-access.env.example`** в **`.env`**, подставьте IP, затем `docker compose up --build`.

При старте контейнера `backend` выполняется `migrate`. Остановка: `Ctrl+C` или `docker compose down`. Логи API: `docker compose logs -f backend`.

Если с телефона не открывается — проверьте брандмауэр Windows (входящие TCP **3000** и **8000** для частной сети).

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

## Доступ с телефона или другого ПК (одна Wi‑Fi сеть)

1. Узнайте **IPv4** ПК в разделе **«Беспроводная сеть»** (`ipconfig`), например `192.168.0.106`.

2. **Без Docker** — в двух терминалах на ПК:

```powershell
cd backend
$env:DJANGO_ALLOWED_HOSTS="localhost,127.0.0.1,192.168.0.106"
python manage.py runserver 0.0.0.0:8000
```

```powershell
cd frontend
Copy-Item env.lan.example .env.local
# Отредактируйте .env.local: подставьте свой IP вместо 192.168.0.106
npm run dev
```

Vite слушает `0.0.0.0:3000`. На другом устройстве откройте `http://192.168.0.106:3000`.

3. **Docker + телефон** — предпочтительно **`.\scripts\docker-up-lan.ps1`** (см. «Запуск через Docker»). Или вручную: **`lan-access.env.example`** → **`.env`**, свой IP, `docker compose up --build`.

4. Разрешите входящие на порты **3000** и **8000** в брандмауэре Windows при необходимости.