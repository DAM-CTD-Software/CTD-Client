
Overview
----
.. image:: ../images/main_overview.png

CTD-Client uses tabs to display different pieces of information to the user.
Simply clicking on one entry will let you switch to that tab.

.. image:: ../images/tabs.png

How to measure
-----
.. important:: The CTD-Client comes with sensible defaults, but some things need to be configured before using it first time. So have a look at :ref:`configure` to set up for measurement.
For measurements you can safely stay inside of the tab of the same name. Here,
you can see different areas to interact with:

DSHIP information
^^^^
This panel displays selected DSHIP parameters that can be chosen inside of the
configuration tabs. You cannot interact with these values in any way, they are
solely meant for information. Internally, these values are used for the
metadata header and the file name.

Water bottles
^^^^
.. image:: ../images/bottles.png
Here, you can see the number of water bottles that are set up and can assign depth
values to them. After starting a measurement, these values are used for
automatic bottle firing. You can insert any value you want, but only positive
numbers will be used as bottle closing depths. All other values will be an
internal signal to Seasave, that the CTD Operator plans on closing this bottle.
This information will result in Seasave offering this bottle as next to fire,
if it is the lowest one, seen in cronological order, after all automatic bottles
have been fired. Setting a non numerical value to a bottle can therefore be
used as a reminder for the operator to close this bottle manually under a
certain condition. When arranging the Seasave window(s) and the CTD-Client, one
can also keep an eye on any pieces of information that has been entered here
previous to measurement.

Data file and metadata information
^^^^
.. image:: ../images/info.png
Shows the currently generated file name, the last file name written and allows
selection of operator, which will be used as metadata point inside the .hex
header. Additionally allows to manipulate the 'Cast' number, a basic counter of
all the individual CTD casts conducted during a cruise. The Pos_Alias can also
be overwritten, if the value retrieved from DSHIP or another ship data
provider does not work for this cast or is not wanted.


Stopwatch
^^^^
.. image:: ../images/stopwatch.png
Basic stopwatch that can only be set back to zero upon clicking on the watch
widget. Will count up until infinity. Can be used to track all kinds of CTD
cast specific waiting times. We use it mostly to ensure a constant soaking time
before each cast.

Measurement and Processing start/stop bottoms
^^^^^^^
.. image:: ../images/run_buttons.png
Allows to start a measurement (calling Seasave) or a processing (see below).
After starting either one of these, the respective button changes to a 'cancel'
button. When clicking this, the corresponding process will be killed immediately.


How to process
----
.. image:: ../images/proc.png

Processing a .hex or .cnv file can be done by clicking 'Run Processing' on the
measurement tab. This opens a file selector where the target file to process
can be selected. Whatever script or, when using the processing procedure from https://git.io-warnemuende.de/CTD-Software/processing ,
.toml configuration is selected in the 'processing' tab. At the moment, this
tab only allows to do exactly that, to choose a file that describes your
processing workflow and in the case of a script, takes the target file as a
single argument.


How to use Near-Real-Time Publications
----------

Intro
^^^^^^
A Near-Real-Time Publication (NRT), in the context of this software, is any kind 
of distribution of data. There are to ways of distribution available: simple
copying to a target location and the sending of emails, with the data files
attached. The other important distinguishing factor for a NRT is the trigger,
when to distribute the data files. At the moment, there are two kinds of
triggers: one that waits for a processing routine to finish, and one that runs
daily at a certain time. The first variant sends only the just processed file,
while the other one filters a target data file directory for files that are
from the same day. Both variants additionally allow a geographical filter,
that checks the candidate files coordinates against a polygon of coordinates,
that must be given in any form that geopandas can handle. All the configuration
options for a single NRT are saved in a .toml file. A template can be obtained
from inside the software. A configuration file needs to be prefixed with "nrt_"
and have the .toml extension. The CTD-Client looks for these files in the root
directory of the CTD-Client installation.

Usage
^^^^^^^
.. image:: ../images/nrt.png

To configure and use NRTs you need to open the
'nrt publication' tab. Here, all the necessary information is displayed for
each individual nrt. For each entry, three buttons are provided, that allow
the configuration, activation/deactivation and the direct publication of new
data, according to the settings that have been configured. 

To create a new NRT, click on the 'create new NRT publication' button. This
opens a new window that allows to enter the necessary information. It will be
pre-filled with template information.

.. important:: When creating a new NRT that is going to send emails, make sure
   to test the email settings by setting the 'open_draft' option to true. That
   way, instead of sending the emails directly, the draft will be opened in the system
   email program, to allow reviewing its contents prior to sending.

.. _configure:
How to configure
-----
.. warning:: Configuration should only be made by people who have a good
   knowledge of the Seasave software stack and the different file types that
   Sea-Bird is using.

In general, this section is divided into two parts: the 'basic' configuration
tab, that allows to edit settings concerning the measurement, for example to
set paths to the Seasave.psa or the XMLCON. And the 'expert' part, that allows
the setting of low-level options, like the update server or the activation of
debug mode.

Basic configuration
^^^^^

Expert configuration
^^^^^^
