FROM python:3.11-alpine

RUN apk add --no-cache samba samba-common tzdata && \
    rm -rf /var/cache/apk/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && rm requirements.txt

COPY /app .

ENV DOMAIN_USERNAME=""
ENV DOMAIN_PASSWORD=""
ENV TZ="Europe/Moscow"

CMD ["python", "main.py"]
