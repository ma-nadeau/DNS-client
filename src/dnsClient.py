""" Python program that implements a DNS client software """

import sys
from dnsQuery import dnsQuery
from dnsResponse import dnsResponse
from dnsRequest import dnsRequest
import socket

def main():
    userDnsQuery = dnsQuery.parseArguments(sys.argv[1:])
    userRequest = dnsRequest(userDnsQuery.domainName, userDnsQuery.recordType)

    dnsSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    dnsSocket.sendto(userRequest.get_encoded_request(),(userDnsQuery.getServerIPV4(), userDnsQuery.port))
    serverResponse, serverAddress = dnsSocket.recvfrom(2048)

    # Might want to make sure here that serverAddress is the correct address

    userDnsResponse = dnsResponse(serverResponse)
    # Might want to check here that the ID is the same as the ID of the dnsQuery
    print(userDnsResponse.answers[0].RDATA)

    dnsSocket.close()
    print(dnsQuery.parseArguments(sys.argv[1:]))

# For when the program is invoked from the command line (stdin)
if __name__ == "__main__":
    main()
