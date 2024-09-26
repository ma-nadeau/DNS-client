""" Python program that implements a DNS client software """

import sys
from dnsQuery import dnsQuery
from dnsResponse import dnsResponse
import socket

def main():
    userDnsQuery = dnsQuery.parseArguments(sys.argv[1:])
    dnsSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    dnsSocket.sendto("message".encode(),(userDnsQuery.getServerIPV4(), userDnsQuery.port))
    serverResponse, serverAddress = dnsSocket.recvfrom(2048)

    userDnsResponse = dnsResponse(serverResponse)

    dnsSocket.close()
    print(dnsQuery.parseArguments(sys.argv[1:]))

# For when the program is invoked from the command line (stdin)
if __name__ == "__main__":
    main()
