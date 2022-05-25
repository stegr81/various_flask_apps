# Multiple Flask applications offering various pointless services.
A Flask application designed to offer a variety of sevices hosted from a central front page:

1. A tracker for the International Space Station which gives the current location and pasover points for the user. The user location is obtained through IP geolocation so will not be accurate if the user is accessing with a VPN. The accuracy may be off if connecting via GSM infrastructure using hotspot or on a GSM capable smart device.

2.  As the application was made during COVID lockdown, initially functionality included analysis of a data set, allowing the user to produce various graphs. Access via the Flask has been removed due to loss of the data source, though the code base remains - Python and HTML.
