FROM ubuntu:16.04

MAINTAINER Brian Masney <masneyb@onstation.org>

RUN apt-get update && \
    apt-get dist-upgrade -y && \
    apt-get install --no-install-recommends -y python-psycopg2 python-django \
            python-imaging python-dateutil python-gdal python-pylint-django \
            texlive texlive-latex-extra python2.7 zip mapserver-bin \
            ttf-freefont make unzip postgresql-client && \
    rm -rf /usr/share/doc && \
    (rm /var/lib/apt/lists/* || true) && \
    apt-get clean

EXPOSE 8003

VOLUME ["/usr/local/cavedbmanager-data", "/usr/local/postgis-data-importer/"]

COPY . /usr/local/cavedbmanager

WORKDIR /usr/local/cavedbmanager
#ENTRYPOINT ["make", "runRemote"]
