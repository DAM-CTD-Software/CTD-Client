Overview
----
CTD-Client uses tabs to display different pieces of information to the user.

How to measure
-----
.. important:: The CTD-Client comes with sensible default, but some things need to be configured before using it first time. So have a look at :ref:`configure` to set up for measurement.
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
Here, you can see number of water bottles that are set up and can assign depth
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


Stopwatch
^^^^

Measurement and Processing start/stop bottoms
^^^


How to process
----

.. _configure:
How to configure
-----
