FROM python:3.9-alpine

RUN apk update
RUN apk add build-base
RUN apk add mariadb-connector-c-dev
RUN apk add postgresql-dev

WORKDIR /usr/src/app

COPY dbcc.py .
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "dbcc.py", "-h"]
ENTRYPOINT ["python", "dbcc.py"]
