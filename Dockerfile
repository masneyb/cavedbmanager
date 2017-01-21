FROM ubuntu:16.04

MAINTAINER Brian Masney <masneyb@onstation.org>

RUN apt-get update && \
    apt-get dist-upgrade -y && \
    apt-get install --no-install-recommends -y python-psycopg2 python-django \
            python-imaging python-dateutil python-gdal python-pylint-django \
            texlive texlive-latex-extra python2.7 zip mapserver-bin \
            ttf-freefont make unzip postgresql-client sudo gdal-bin patch \
            shellcheck curl wget ca-certificates && \
    rm -rf /usr/share/doc && \
    (rm /var/lib/apt/lists/* || true) && \
    apt-get clean

RUN curl -L -o /postgis-data-importer.zip https://github.com/masneyb/postgis-data-importer/archive/master.zip && \
    unzip -d /usr/local /postgis-data-importer.zip && \
    mv /usr/local/postgis-data-importer-master /usr/local/postgis-data-importer && \
    rm /postgis-data-importer.zip

VOLUME ["/usr/local/cavedbmanager-data", "/usr/local/postgis-data-importer/download"]

EXPOSE 8000

COPY . /usr/local/cavedbmanager

WORKDIR /usr/local/cavedbmanager
