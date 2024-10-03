FROM python:3.10-alpine as base

WORKDIR /src

RUN set -eu && \
    apk update && \
    apk upgrade

RUN pip install -U pip setuptools uwsgi-tools

COPY docker-entrypoint.sh /
RUN set -uex && \
    chmod +x /docker-entrypoint.sh


ENTRYPOINT [ "/docker-entrypoint.sh"]

FROM base as builder
RUN pip install -U wheel

COPY requirements-dev.txt /wheels/


RUN pip install -r /wheels/requirements-dev.txt

RUN apk add gcc musl-dev python3-dev curl-dev linux-headers

COPY requirements.txt /wheels/
RUN pip wheel -r /wheels/requirements.txt --wheel-dir=/wheels

RUN pip install --no-index --no-cache-dir -f /wheels \
        -r /wheels/requirements.txt

# required for healthchecks
RUN pip install uwsgi_tools


COPY src /src

FROM base as release
COPY --from=builder /wheels /wheels
COPY --from=builder /src /src
ENV PYTHONUNBUFFERED 1

RUN pip install --no-index --no-cache-dir -f /wheels \
        -r /wheels/requirements.txt && \
    rm -rf /wheels /root/.cache /var/cache/apk/*
