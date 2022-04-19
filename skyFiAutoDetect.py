import socket


#####
# Python class to auto respond to a search for a SkyFi device. This has only been tested using SkySafari.
# 
# Basic operation is listening for a UDP request on port 4031
# The request will be in the form "skyfi:<name>?", where <name> is the SkyFi search name
# If the name matches this instance (passed in as localName), this response is "skyfi:<name>@<ipaddress>"
#
#
#
#
# Thread usage:
# import threading
# from skyFiAutoDetect import skyFiAutoDetect
#
# skyFiName = "example"
#
# ssad = skyFiAutoDetect()
# ssadThread = threading.Thread(target=ssad.listenForSkyFiAutoDetect, args=(skyFiName,))
# ssadThread.start()
#
#
#
# Note that the localIP address can be specified, if auto detection of local IP is not desired:
# ssadThread = threading.Thread(target=ssad.listenForSkyFiAutoDetect, args=(skyFiName,"192.168.1.24"))
#
#####


class skyFiAutoDetect:
    localPort   = 4031
    bufferSize  = 128

    def __init__(self):
        pass

    # from: https://stackoverflow.com/a/28950776/8338986
    def get_ip(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0)
        try:
            # doesn't even have to be reachable
            s.connect(('10.255.255.255', 1))
            IP = s.getsockname()[0]
        except Exception:
            IP = '127.0.0.1'
        finally:
            s.close()
        return IP


    def listenForSkyFiAutoDetect(self, localName, localIP = None):
        listenIP = "0.0.0.0"

        if (localIP == None):
            localIP = self.get_ip()

        msgFromServer = "skyfi:" + localName + "@" + localIP
        responseToSend = str.encode(msgFromServer) 

        # Create a datagram socket
        UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

        # Bind to all local addresses
        UDPServerSocket.bind((listenIP, self.localPort))

        print("SkyFi autoresponding to " + localName + " from " + localIP)

        # Listen for incoming datagrams
        while(True):
            bytesAddressPair = UDPServerSocket.recvfrom(self.bufferSize)
            request = bytesAddressPair[0].decode("utf-8")
            address = bytesAddressPair[1]

            # The request will come in the form "skyfi:<name>?", where <name> is the search name, entered from the SkySafari interface
            if (request.startswith("skyfi:")):
                parts = request.split(':');
                searchName = parts[1].split('?')[0];

                # if this server is the one that the client is looking for, respond
                if (searchName == localName or searchName == localName + '?'):
                    print("Received SkyFi device search request")
                    # The response is in the format "skyfi:<name>@<ipaddress>"
                    UDPServerSocket.sendto(responseToSend, address)



