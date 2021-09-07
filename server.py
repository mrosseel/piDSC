#!/usr/bin/env python

# Adapted from https://github.com/peterjc/longsight/blob/master/telescope_server.py

import socket
import os
import sys

server_name = '192.168.1.213'
server_port = 4030

#Turn on for lots of logging...
debug = True

# ================
# Main Server Code
# ================

# https://github.com/avarakin/DSC/blob/main/src/sensor_bno055.cpp

# sensor.euler
# alt: ori.z() * 180 / PI * 100
# az: -ori.x() * 180 / PI * 100



# https://github.com/adafruit/Adafruit_CircuitPython_BNO055
# print(sensor.temperature)
# print(sensor.euler)
# print(sensor.gravity)

#quaternion angles to euler angles
# float yaw   = atan2(2.0f * (q[1] * q[2] + q[0] * q[3]), q[0] * q[0] + q[1] * q[1] - q[2] * q[2] - q[3] * q[3]);
# float pitch = -asin(2.0f * (q[1] * q[3] - q[0] * q[2]));
# float roll = atan2(2.0f * (q[0] * q[1] + q[2] * q[3]), q[0] * q[0] - q[1] * q[1] - q[2] * q[2] + q[3] * q[3]);


def return_none(value=None):
    """Dummy command implementation returning nothing."""
    return None

def meade_lx200_cmd_CM_sync():
    """For the :CM# command, Synchronizes the telescope's position with the currently selected database object's coordinates.
    Returns:
    LX200's - a "#" terminated string with the name of the object that was synced.
    Autostars & LX200GPS - At static string: "M31 EX GAL MAG 3.5 SZ178.0'#"
    """
    return "M31 EX GAL MAG 3.5 SZ178.0'#"
    
def meade_lx200_cmd_GD_get_dec():
    return "+04*54'43#"

def meade_lx200_cmd_GR_get_ra():
    """For the :GR# command, Get Telescope RA
    Returns: HH:MM.T# or HH:MM:SS#
    Depending which precision is set for the telescope
    """
    return "06:33:21#";    


# Processing ':Sr06:38:57#'
def meade_lx200_cmd_Sr_set_target_ra(value):
    """For the commands :SrHH:MM.T# or :SrHH:MM:SS#
    Set target object RA to HH:MM.T or HH:MM:SS depending on the current precision setting.
    Returns: 0 - Invalid, 1 - Valid
    Stellarium breaks the specification and sends things like ':Sr 20:39:38#'
    with an extra space.
    """
    #global target_ra
    try:
        # target_ra = parse_hhmm(value.strip()) # Remove any space added by Stellarium
        # The extra space sent by Stellarium v0.12.4 has been fixed:
        # https://bugs.launchpad.net/stellarium/+bug/1272960
        #sys.stderr.write("Parsed right-ascension :Sr%s# command as %0.5f radians\n" % (value, target_ra))
        return "1"
    except Exception as err:
        #sys.stderr.write("Error parsing right-ascension :Sr%s# command: %s\n" % (value, err))
        return "0"

# Processing ':Sd+16*22:50#'
def meade_lx200_cmd_Sd_set_target_de(value):
    """For the command :SdsDD*MM# or :SdsDD*MM:SS#
    Set target object declination to sDD*MM or sDD*MM:SS depending on the current precision setting
    Returns: 1 - Dec Accepted, 0 - Dec invalid
    Stellarium breaks this specification and sends things like ':Sd +15\xdf54:44#'
    with an extra space, and the wrong characters. Apparently chr(223) is the
    degrees symbol on some character sets.
    """
    #global target_dec
    try:
        #target_dec = parse_sddmm(value.strip()) # Remove any space added by Stellarium
        # The extra space sent by Stellarium v0.12.4 has been fixed:
        # https://bugs.launchpad.net/stellarium/+bug/1272960 
        #sys.stderr.write("Parsed declination :Sd%s# command as %0.5f radians\n" % (value, target_dec))
        return "1"
    except Exception as err:
        #sys.stderr.write("Error parsing declination :Sd%s# command: %s\n" % (value, err))
        return "0"

command_map = {
    #Meade LX200 commands:
    ":CM": meade_lx200_cmd_CM_sync,
    ":GD": meade_lx200_cmd_GD_get_dec,
    ":GR": meade_lx200_cmd_GR_get_ra,
    ":Me": return_none, #start moving East
    ":Mn": return_none, #start moving North
    ":Ms": return_none, #start moving South
    ":Mw": return_none, #start moving West
    # ":MS": meade_lx200_cmd_MS_move_to_target,
    ":Q": return_none, #abort all current slewing
    ":Qe": return_none, #abort slew East
    ":Qn": return_none, #abort slew North
    ":Qs": return_none, #abort slew South
    ":Qw": return_none, #abort slew West
    ":RC": return_none, #set slew rate to centering (2nd slowest)
    ":RG": return_none, #set slew rate to guiding (slowest)
    ":RM": return_none, #set slew rate to find (2nd fastest)
    ":RS": return_none, #set Slew rate to max (fastest)
    ":Sd": meade_lx200_cmd_Sd_set_target_de,
    ":Sr": meade_lx200_cmd_Sr_set_target_ra,
    # ":St": meade_lx200_cmd_St_set_latitude,
    # ":Sg": meade_lx200_cmd_Sg_set_longitude,
    ":Sw": return_none, #set max slew rate
    # ":SG": meade_lx200_cmd_SG_set_local_timezone,
    # ":SL": meade_lx200_cmd_SL_set_local_time,
    # ":SC": meade_lx200_cmd_SC_set_local_date,
    # ":U":  meade_lx200_cmd_U_precision_toggle,
}

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = (server_name, server_port)
sys.stderr.write("Starting up on %s port %s\n" % server_address)
sock.bind(server_address)
sock.listen(1)

while True:
    # SkySafari v4.0.1 continously opens and closed the connection,
    # while Stellarium via socat opens it and keeps it open using:
    # $ ./socat GOPEN:/dev/ptyp0,ignoreeof TCP:raspberrypi8:4030
    # (probably socat which is maintaining the link)
    #sys.stdout.write("waiting for a connection\n")
    connection, client_address = sock.accept()
    data = ""
    try:
        #sys.stdout.write("Client connected: %s, %s\n" % client_address)
        while True:
            data += connection.recv(16)
            if not data:
            #     imu.update()
                 break
            if debug:
                sys.stdout.write("Processing %r\n" % data)
            #For stacked commands like ":RS#:GD#",
            #but also lone NexStar ones like "e"
            while data:
                while data[0:1] == "#":
                    #Stellarium seems to send '#:GR#' and '#:GD#'
                    #(perhaps to explicitly close and prior command?)
                    #sys.stderr.write("Problem in data: %r - dropping leading #\n" % data)
                    data = data[1:]
                if not data:
                    break
                if "#" in data:
                    raw_cmd = data[:data.index("#")]
                    #sys.stderr.write("%r --> %r as command\n" % (data, raw_cmd))
                    data = data[len(raw_cmd)+1:]
                    cmd, value = raw_cmd[:3], raw_cmd[3:]
                else:
                    #This will break on complex NexStar commands,
                    #but don't care - Meade LX200 is the prority.
                    raw_cmd = data
                    cmd = raw_cmd[:3]
                    value = raw_cmd[3:]
                    data = ""
                if not cmd:
                    sys.stderr.write("Eh? No command?\n")
                elif cmd in command_map:
                    print("mapping command")
                    if value:
                        if debug:
                            sys.stdout.write("Command %r, argument %r\n" % (cmd, value))
                        resp = command_map[cmd](value)
                    else:
                        resp = command_map[cmd]()
                    if resp:
                        if debug:
                            sys.stdout.write("Command %r, sending %r\n" % (cmd, resp))
                        connection.sendall(resp)
                    else:
                        if debug:
                            sys.stdout.write("Command %r, no response\n" % cmd)
                else:
                    sys.stderr.write("Unknown command %r, from %r (data %r)\n" % (cmd, raw_cmd, data))
    finally:
        connection.close()
