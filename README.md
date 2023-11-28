# *Прототип проекта молодежной программы финтех форума Finopolis 2023 "Система умной лояльности"*

# Описание проекта
 "Система умной лояльности" - это инновационный продукт, который сочетает в себе искусственный интеллект для прогнозирования релевантных пользователю персональных кэшбеков и современный метод оплаты с использованием биометрии.  


# Backend:

## Стек технологий (API):
-Python
-Fastapi
-SQLAlchemy
-PostgreSQL
-Docker/Docker-Compose

## Запуск API
1. Переименовать файл в корне .env.local в .env  и при необходимости отредактировать переменные
2. Переименовать файл в папке mock_server .env.local в .env  и при необходимости отредактировать переменные
3. Запустить Docker-Compose:
```
docker compose up -d
```


Все, API доступно по адресу: 127.0.0.1
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
