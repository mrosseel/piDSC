i
# IC2 Setup

## Enable I2C in the kernel

`sudo raspi-config`


## Update I2C Baudrate

The BNO85 seems to work best on the Raspberry Pi with an I2C clock frequency of 400kHz. You can make that change by adding this line to your /boot/config.txt file:


`dtparam=i2c_arm=on`

`dtparam=i2s=on`

`dtparam=spi=on`

`dtparam=i2c_arm_baudrate=400000`

## Update Pi and Python

Run the standard updates:

`sudo apt-get update`

`sudo apt-get upgrade`

`sudo apt-get install python3-pip`

`sudo pip3 install --upgrade setuptools`


## Install CircuitPython

[Instructions](https://learn.adafruit.com/circuitpython-on-raspberrypi-linux/installing-circuitpython-on-raspberry-pi)

`cd ~`

`sudo pip3 install --upgrade adafruit-python-shell`

`wget https://raw.githubusercontent.com/adafruit/Raspberry-Pi-Installer-Scripts/master/raspi-blinka.py`

`sudo python3 raspi-blinka.py`

## Verify

To detect that the I2C device can be found on the bus: 

`sudo i2cdetect -y 1` 

There should be at least one position that has the device address.

# BNO085

`sudo pip3 install adafruit-circuitpython-bno08x`


# OLED FeatherWing

## Install 

`sudo pip3 install adafruit-circuitpython-displayio-layout`
`sudo pip3 install adafruit-circuitpython-displayio-sh1107`

## Astropy library

https://docs.astropy.org/

`sudo pip3 install dms2dec`
`sudo pip3 install astropy`
