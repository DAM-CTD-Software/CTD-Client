# CTD-Client

A simple tool that supports the measurement of CTD-data.
In this first version, it is mainly a rewrite of Toralfs excellent CTD-Client,
that should directly replace it. With a very similar look and feel, switching
to this Client should be easy. With subsequent releases, this tool will
grow into a way more sophisticated peace of software. Planned features and a
rough timeline are given below.
For now, the key features are:

- fetches DSHIP information and writes them to a designated metadata header
- starts Seasave.exe with the correct command line arguments
- allows for bottle closing time configuration by the user and the correct
    internal data processing of this information
- supports Near-Real-Time distribution of CTD data via email
- saves relevant usage data for continuous operation

For a more detailed description check out the
[online documentation]("https://ctd-software.pages.io-warnemuende.de/CTD-Client/usage.html").

## Release plan

### v1.7

- test and improve Near-Real-Time publications

### v2

- implement seamless addition of other ctd devices
- add GUI to customise processing
