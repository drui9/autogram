FROM python:3.12-alpine

RUN apk update && apk add gcc musl-dev python3-dev libffi-dev openssl-dev cargo make
RUN addgroup -S autogram && adduser -S autogram -G autogram

USER autogram
WORKDIR /home/autogram

COPY . .
RUN pip install .

CMD ["python3", "start.py"]
