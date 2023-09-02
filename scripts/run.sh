#!/bin/bash

cd ..
source app/telegram_bot/src/telegram_bot_venv/bin/activate
export NOTES_BOT_ML_API_LINK = "127.0.0.1:8000/ml_api"
python3 app/telegram_bot/src/telegram_bot.py &


source app/ml_server/src/ml_server_venv/bin/activate
uvicorn app/ml_server/src/ml_server:ml_api --host 127.0.0.1 --port 8000
