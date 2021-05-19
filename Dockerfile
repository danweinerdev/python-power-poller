FROM python:3.8-alpine

COPY ["requirements.txt", "/srv/"]
RUN python3 -m pip install -r /srv/requirements.txt

COPY ["commands/", "/srv/commands/"]
COPY ["tplink/", "/srv/tplink/"]
COPY ["cli.py", "/srv/"]

RUN set -ex; \
    adduser --home=/srv --shell=/bin/false \
        --disabled-password --no-create-home monitor; \
    chmod 640 -R /srv/**.py; \
    chown monitor:monitor -R \
        /srv/commands \
        /srv/tplink \
        /srv/cli.py;

USER monitor
WORKDIR /srv

ENTRYPOINT ["python3", "/srv/cli.py"]
CMD ["run", "-o", "--loglevel=INFO", "/etc/monitor.conf"]
