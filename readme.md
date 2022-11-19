# piDSC

This project was inspired directly by astrokeith's excellent [eFinder](https://astrokeith.com/equipment/efinder/) project. This repo was forked from Chris Horne, the original author (see https://bitbucket.org/ckhorne_dev/pidsc). This project is intended only for non-commercial use.

piDSC is combination of a RaspberryPi 4 and a camera, to be mounted to a telescope. The pi constantly takes pictures through the camera of the night sky, and using the [astrometry.net](http://astrometry.net/doc/readme.html) package, determines the current RA/DEC that the telescope is pointing towards, and reports this to SkySafari or other planetarium software via the LX200 protocol.

The difficulty in this project is aquiring and platesolving quickly enough for this to be usable. With a RaspberryPi 4B and an ASI120mm-s and 50mm f/1.4 lens, the process to aquire and platesolving an image takes approx 1.5 seconds.

## Installation

[To be written] The main items are the zwo image library and the astrometry.net build (difficult).

## Configuration

All the current configuration is in the top of the files (mostly pidsc.py and platesolver.py), and should be changed to a config file at some point.

## Run

Run using `python3 pidsc.py`

While on the same WiFi network as the pi, use SkySafari to connect. The code responds to the SkyFi autodetect, so the IP is not needed. Port is still 4030.

## Development

Run using 'python3 pidsc.py -h' to see all options available.

## Limitations / todo

* The config options (including the SkyFi name) is all embedded in the code and should be moved
* There's currently no easy way to align the camera with the telescope. I typically plug the camera into a computer and set using [FireCapture](http://www.firecapture.de/) or similar software so the camera's center matches the eyepiece center
* The code does nothing to host a WiFi network, which doesn't work in the field.

