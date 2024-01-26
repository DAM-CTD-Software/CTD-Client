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
- needs seabirdfilehandler and seabird_processing from this git organization
cloned into the same parent directory than this project sits in
- easiest way of getting started would be by using poetry
- then, a basic `poetry install` should suffice
- to run the GUI, call `poetry run python -m src.mig.backend.controller`
- feel then free to open an Issue in this repository when finding a bug
- in general, do not expect anything to work out-of-the-box at the moment
- and expect a lot of changes, so pull often

## Outlook
- heavy refactoring
- serious work on design, at the moment its just functional
- documentation
- real-live application on EMB in February
