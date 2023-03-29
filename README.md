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

# Установка бота на сервере
Для установки бота на сервер необходимо на сервере в терминале выполнить команду для копирования репозитория:
```
git@github.com:popkovaleks/fish_sell_bot.git
```

Создать файл .env с переменными окружения:
- `DATABASE_PASSWORD` - пароль к бд redis
- `DATABASE_HOST` - адрес бд redis
- `DATABASE_PORT` - порт бд redis
- `TELEGRAM_TOKEN` - токен телеграм бота

Установить python3 и в директории проекта создать вирутальное окружение:
```
python3 -m virtualenv venv
```

Запустить виртуальное окружение:
```
source venv/bin/activate
```

Установить необходимые библиотеки:
```
pip3 install -r requirements.txt
```

В директории /etc/systemd/system на сервере создать файл *.service для настройки службы для работы бота со следующим содержанием:
```
[Service]
ExecStart=/<путь до директории с проектами>/fish_sell_bot/venv/bin/python3  /<путь до директории с проектами>/fish_sell_bot/tg_bot.py
Restart=always

[Install]
WantedBy=default.target
```

После этого запустить службу командой:
```
systemctl start <имя службы>.service
```

Проверить статус:
```
systemctl status <имя службы>.service
```
