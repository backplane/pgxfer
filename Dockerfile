FROM python:3-slim
LABEL maintainer="Backplane BV <backplane@users.noreply.github.com>"

ARG DEBIAN_FRONTEND=noninteractive
ARG AG="apt-get -yq --no-install-recommends"
RUN set -eux; \
  $AG update; \
  $AG upgrade; \
  $AG install \
	postgresql-client-15 \
  ; \
  $AG autoremove; \
  $AG clean; \
  rm -rf \
    /var/cache/debconf/*-old \
    /var/lib/apt/lists/* \
    /var/lib/dpkg/*-old \
  ;

COPY requirements.txt /
RUN pip install -r /requirements.txt

COPY /src/pgxfer /app/pgxfer

ENV PYTHONPATH="/app"
ENTRYPOINT [ "/usr/local/bin/python", "-m", "pgxfer" ]
