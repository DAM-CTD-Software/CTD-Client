# Intro

The CTD-Client is a program that supports the measurement of CTD-data with
Sea-Bird CTDs. Calls Sea-Birds measuring software, Seasave, with certain
parameters and alters its configuration file prior to measurements. This way,
a variety of functions can be achieved:

- primarily tags data files with metadata from the ship information system
  available on german research vessels (DSHIP)
- allows for programmed bottle closing time configuration
- can run processing scripts using Sea-Bird processing modules and
  custom ones, via [the ctd-processing python package.](https://ctd-software.pages.io-warnemuende.de/processing/index.html)
- supports Near-Real-Time distribution of CTD data via email
- saves relevant usage data for continuous operation

## Metadata injection

Using DSHIP, or a comparable ship information system whose data can be
retrieved via simple TCP/IP-calls, all kinds of ship metadata can be saved
to the Sea-Bird custom header. This way, all data files, from raw .hex data,
to .btl or .cnv data files will feature the metadata information.
Additionally, other metadata, like a continuous bottle number for a whole
cruise, can be put into the metadata header. The file name of the data file
will also be build from different pieces of metadata.

## Programmable bottle closing

If the automatic firing of water bottles is wanted, for example when using
free-flow bottles, those can be programmed inside the CTD-Client. The
software can also adjust for hardware-specific time delays between firing
individual bottles.

## Processing

Processing raw data after measurements is also supported. The different
processing steps to run can be configured in a separate tab, while the
execution will be a single bottom press on the main page. That way, the data
can be easily processed in seconds after a successful measurement. The
configuration window does also feature a very intuitive alteration of
processing workflows, allowing for quick and constant playing around with
the data.

## Near-Real-Time data distribution

All acquired data can automatically send to different stakeholders or other
interested parties. The distribution protocol is email and can be set to
sending daily to a specific time or after each processing workflow.
