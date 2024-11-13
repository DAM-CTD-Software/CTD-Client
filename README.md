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
- saves relevant usage data for continuous operation

## Installation and configuration
The CTD-Client is its own python package and can therefore be installed like
any other package, using package managers like poetry or pip. The only caveat
is that is does not reside on Pypi, only on a local repository inside the
CTD-Software organization. In order to install this package (and all other
software in this organization) you need to configure your package manager of
choice, so that it knows where to look for the custom dependencies.
To generate an .exe to distribute to ships, a .spec file is shared that can be used with pyinstaller.

## Release plan
### fix misc bugs during EMB cruises
### v2
- implement seamless addition of other ctd devices
- add GUI to customise processing
