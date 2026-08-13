"""Tracking, frequency coordination and monitoring for the HamSCI WSPRSonde network.

Two things live here today:

* :mod:`wsprsonde.stations` and ``data/wsprsonde_stations.csv`` -- the curated
  record of which WSPRSonde is where, on what frequency.
* :mod:`wsprsonde.wsprdaemon` -- a read-only client for the WsprDaemon spot
  archive, used to check what is actually on the air.

``python -m wsprsonde.build_locations`` joins the two and writes the product in
``products/``, which is what ``polar-psws`` overlays on its station maps.
"""

__all__ = ["build_locations", "maidenhead", "stations", "wsprdaemon"]
