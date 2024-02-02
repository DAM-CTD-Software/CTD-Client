# CTD-Client

Very first draft of my own CTD-Client. Supports the general functionalities, but
is still mostly untested and undocumented.
Should in general support these key use-cases:
- start Seasave.exe with the correct command line arguments
- fetches DSHIP information and writes those to the respective place in the
  Seasave psa
- allow for bottle closing time configuration by the user and the correct
    internal data processing of this information
- support a configurable processing

## installation/configuration

- needs a fairly new python version of 3.11.4 or newer
- when your local python packaging tool is setup according to this
[Guide](https://git.io-warnemuende.de/CTD-Software/Ueberblick/src/branch/master/installation.md),
you can just run `pip install ctdclient` or `poetry add --source gitea ctdclient`,
respectively.
- if not, you can clone the repository and install the project with its
dependencies manually
- launching the GUI can be achieved by `python -m src.ctdclient.controller`

## Outlook
- heavy refactoring
- serious work on design, at the moment its just functional
- documentation
- real-live application on EMB in February
