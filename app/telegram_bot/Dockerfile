FROM python:3.9

WORKDIR /app

COPY ./src .
COPY ./requirments.txt .

RUN pip3 install -r /app/requirments.txt

CMD ["python", "telegram_bot.py"]
