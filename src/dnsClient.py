""" Python program that implements a DNS client software """

import sys
from dnsQuery import dnsQuery
import socket

# For when the program is invoked from the command line (stdin)
if __name__ == "__main__":
    userDnsQuery = dnsQuery.parseArguments(sys.argv[1:])
    dnsSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    dnsSocket.sendto("message".encode(),(userDnsQuery.getServerIPV4(), userDnsQuery.port))
    serverResponse, serverAddress = dnsSocket.recvfrom(2048)

    dnsSocket.close()
    print(dnsQuery.parseArguments(sys.argv[1:]))
