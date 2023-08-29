# finodays

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
Также API можно протестировать по адресу: http://80.78.241.76/docs