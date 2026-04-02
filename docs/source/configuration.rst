Configuration
=============

The settings of the CTD-Client are stored inside C:/user/USERNAME/AppData/Local/ctdclient/ctdclient .
All configuration can be done via the GUI of the software. If you still want to
check on the individual config files, you will find them via the path above.
The possible configuration files found here are:

- the main config file, ctdclient.toml

- the processing config files, prefixed with "proc\_"

- the nrt config files, prefixed with "nrt\_"


How to configure
----------------

The main configuration file looks like this:

.. literalinclude:: ../../src/ctdclient/resources/templates/ctdclient.toml
   :language: toml
   :caption: ctdclient.toml

In general, this section is divided into two parts: the 'basic' configuration
tab, that allows to edit settings concerning the measurement, for example to
set paths to the Seasave.psa or the XMLCON. And the 'expert' part, that allows
the setting of low-level options, like the update server or the activation of
debug mode.

Basic settings
^^^^^

Lets you define the basic file paths the software needs in order to interact
with Sea-Birds measurement software, 'Seasave'. 

**seasave psa**: the configuration file of the Seasave software

**output directory**: the path were the raw data files will be stored at

**xmlcon**: the instruments configuration file

**number of bottles**: the number of water bottles currently installed on the CTD rosette

**operators**: the names of the different CTD operators of this cruise. These will be available for selection in the dropdown on the main page.

Expert settings
^^^^^^
.. warning:: This configuration should only be made by people who have a good
   knowledge of the Seasave software stack and the different file types that
   Sea-Bird is using.

base
""""

**seasave exe**: the path to the seasave executable

**processing exes**: the path to the seasave processing modules

**downcast option**: whether to display the option, to close bottles automatically during downcast. Will be always true otherwise.

**generate processing fingerprint**: save the processing workflow file used for processing inside the given directory. If none given, no fingerprint will be saved.

**file type dir**: save all files used/created during the processing workflow in individual directories inside the given directory. If none given, no files will be saved (additionally to the usual file saving done).

**debugging**: toggles debugging mode, that displays more (debugging) information

**scaling**: lets the user define a scaling factor of the GUI

**minimum bottle difference**: sets a minimum pressure difference that individual bottles will be separated to, when put to the same depth value. Prevents slow hardware from not closing both bottles in time. Can be set to 0 if unwanted.

dship parameters
""""""""""""""""

Here, you can define the different DSHIP variables to use for polling values
from.

email config
""""""""""""

Lets you set the settings of a local email server, that can be used for sending
emails inside the CTD-Client. Near-Real-Time data distribution, debugging info
sending and general email requests can be used via a local email server.
