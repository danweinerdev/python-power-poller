# TPLink Smart Devices

This is a python3 library for interfacing with the TP-Link smart home components.

After searching around I found a lot of JavaScript libraries, but no fully functioning Python versions and so this was based mostly around taking the bare functionality of the most popular JavaScriipt versions and converting them to standard python classes.

The CLI is the primary tool for interfacing with the devices but you are free to use the library alone if need be.

## Design

The library was designed for another tool I built which sends data to InfluxDB for display in grafana. The CLI is used for manipulating the individual devices and configuring them for use on my network.
