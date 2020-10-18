# TPLink Smart Devices

This is a python3 library for interfacing with the TP-Link smart home components.

After searching around I found a lot of JavaScript libraries, but no fully functioning Python versions and so this was based mostly around taking the bare functionality of the most popular JavaScriipt versions and converting them to standard python classes.

The CLI is the primary tool for interfacing with the devices but you are free to use the library alone if need be.

## Design

The library was designed for another tool I built which sends data to InfluxDB for display in grafana. The CLI is used for manipulating the individual devices and configuring them for use on my network.

## Docker Container

The Docker container is available from:
```text
aprelius/tplink:latest
```

It can be run stand-alone or as any base necessary. Make sure to generate a config file and pass it in as a volume mount.

```shell
docker run -it \
    -v $PWD/config/example.conf:/etc/monitor.conf:ro \
    aprelius/tplink:latest
```

The container entrypoint's to the cli, so you can run any of the commands from there. If you would like to explore the container or change the entrypoint, you can do the following:

```shell
docker run -it \
    --entrypoint sh \
    -v $PWD/config/example.conf:/etc/monitor.conf:ro \
    aprelius/tplink:latest
```
