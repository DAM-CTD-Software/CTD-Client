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
- is able to seamlessly switch between different CTD devices, like Scanfish
- saves relevant usage data for continuous operation

## Installation and configuration
The CTD-Client is its own python package and can therefore be installed like
any other package, using package managers like poetry or pip. The only caveat
is that is does not reside on Pypi, only on a local repository inside the
CTD-Software organization. In order to install this package (and all other
software in this organization) you need to configure your package manager of
choice, so that it knows where to look for the Client. This can be done using
this
[Guide](https://git.io-warnemuende.de/CTD-Software/Ueberblick/src/branch/master/installation.md),
which will then allow you to just run `pip install ctdclient` or
`poetry add --source gitea ctdclient`, respectively. You can of course also
just clone the repository and install the project with its dependencies
manually. Note that a very recent python version of **>=3.12** is necessary to
run this tool. Launching the GUI can be achieved by running
`python -m src.ctdclient.controller`. To generate a executable for any platform,
[pyinstaller](https://pyinstaller.org/en/stable/index.html) has been used. For
the official program, that is being used on the EMB, the windows .spec file can
be found in this repository.

## Release plan
### v1.1.0
- backend refactoring:
- fully implement MVC by introducing a model class
- move psa from config to model
- clear separation of concerns: one class or method should do one thing, and
one thing only. Dshipcaller e.g. should only retrieve dship data. It should
not build metadata headers or write configs.
- separate individual view classes into their own files
- documentation catch up

### v1.2.0
- own scanfish tab

### v1.3.0
- integrate my own python-internal processing

### v1.4.0
- guided field calibration in extra tab

## general outlook
- the final real-live test happens on EMB340 from 2024-04-25 to 2024-05-16
- then the software will be tested on MSM129 from 2024-05-26 to 2024-06-05
- after that, the CTD-Client should be ready to be installed on all 4 major
German research vessels, to allow for a consistent measuring process with a
fixed metadata header inclusion and a standardized data processing.
