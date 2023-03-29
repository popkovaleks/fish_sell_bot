# Пример работы бота
Пример работы бота [тут](https://t.me/fish_sell_bot).

# Установка
Для запуска достаточно создать env файл с параметрами:
- `DATABASE_PASSWORD` - пароль к бд redis
- `DATABASE_HOST` - адрес бд redis
- `DATABASE_PORT` - порт бд redis
- `TELEGRAM_TOKEN` - токен телеграм бота

## Токен telegram-бота
Для создания телеграм бота напишите боту [BotFather](https://t.me/BotFather), там вы создадите бота, и вам будет выдан токен бота.

## Запуск
После заполнения файла env можно запускать бота командой 
 ```
 python3 tg_bot.py
 ```
