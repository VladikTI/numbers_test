#!/bin/bash

exec flask run &
exec python3 /code/main.py &
exec python3 /code/bot.py
# запускаем скрипты
