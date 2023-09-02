#!/bin/bash

# Переходим на уровень выше
cd ..
current_dir=$(pwd)

# Переходим в папку с исходным кодом телеграм-бота и запускаем его
cd app/telegram_bot/src/
# Активируем виртуальное окружение телеграм-бота
source telegram_bot_venv/bin/activate
export NOTES_BOT_ML_API_LINK="http://127.0.0.1:8000/ml_api"

python3 telegram_bot.py &

# Возвращаемся к исходному рабочему каталогу
cd "$current_dir"

# Переходим в папку с исходным кодом ML-сервера и активируем его виртуальное окружение
cd app/ml_server/src/
source ml_server_venv/bin/activate
# Запускаем ML-сервер с указанными параметрами
uvicorn ml_server:ml_api --host 127.0.0.1 --port 8000