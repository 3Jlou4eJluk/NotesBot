FROM python:3.9

WORKDIR /app


# Копируем
COPY ./src .
COPY ./requirments.txt .


RUN pip3 install -r /app/requirments.txt

RUN pip3 install uvicorn

EXPOSE 8000
EXPOSE 5000

CMD ["uvicorn", "ml_server:ml_api", "--host", "0.0.0.0", "--port", "8000"]
