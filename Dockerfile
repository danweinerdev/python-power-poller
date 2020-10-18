FROM python:3.8-alpine

COPY ["requirements.txt", "/srv/"]
RUN python3 -m pip install -r /srv/requirements.txt

COPY ["commands", "/srv/commands/"]
COPY ["tplink", "/srv/tplink/"]
COPY ["cli.py", "/srv/"]

ENTRYPOINT ["python3", "/srv/cli.py"]
CMD ["run", "-o", "--loglevel=INFO", "/etc/monitor.conf"]
