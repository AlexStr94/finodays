# *FINODAYS*
#

# Backend:

## Стек технологий (API):
-Python
-Fastapi
-SQLAlchemy
-PostgreSQL
-Docker/Docker-Compose

## Запуск API
1. Переименовать файл .env.local в .env  и при необходимости отредактировать переменные
2. Запустить Docker-Compose:
```
docker compose up -d
```
3. Открыть контейнер бекенда:
```
docker exec -it backend bash
```
4. накатить миграции бд внутри контейнера:
```
alembic upgrade head
```

Все, API доступно по адресу: 127.0.0.1
Также API можно протестировать по адресу: http://127.0.0.1/docs
#

# ML: 
Подробную информацию по файлам, связанным с ml частью смотреть notebooks/README.md

# Frontend: 

## Запуск терминала
```console
cd frontend/terminal_fino
npm install
npm run start
```

## Запуск приложения
```console
cd frontend/app_center_invest
npm install
npx expo start
```
Также в frontend/app_center_invest вы можете найти установочный файл под android - application.aab