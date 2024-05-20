FROM python:3.12

WORKDIR /app

COPY requirements.txt .
COPY src src

RUN pip install --no-cache-dir -r requirements.txt

CMD [ "python", "./src/main.py" ]