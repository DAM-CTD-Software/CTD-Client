Installation
============

The CTD-Client is distributed as windows executable (.exe). You can find the latest version
`here
<https://git.io-warnemuende.de/CTD-Software/CTD-Client/releases/latest>`_.
You do not need anything else and can put the .exe file anywhere you want to,
but it is recommended to use a default path, like C:/Programs. To update the
software, just replace the exe with a more recent one. You can get notified
about new versions by subscribing to this rss feed:
https://git.io-warnemuende.de/CTD-Software/CTD-Client/releases.rss

Configuration
=============

The settings of the CTD-Client are stored inside C:/user/USERNAME/AppData/Local/ctdclient/ctdclient .
The main configuration file is called ctdclient.toml and looks like this:

.. literalinclude:: ../../resources/templates/ctdclient.toml
   :language: toml
   :caption: ctdclient.toml

All configuration can be done via the GUI of the software.
