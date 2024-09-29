""" Python program that implements a DNS client software """

import sys
from dnsQuery import dnsQuery
from dnsResponse import dnsResponse
from dnsRequest import dnsRequest
from dnsCommonTypes import getServerIPV4
import socket
import time


def main():
    userDnsQuery = dnsQuery.parseArguments(sys.argv[1:])
    userRequest = dnsRequest(userDnsQuery.domainName, userDnsQuery.recordType)

    dnsSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    dnsSocket.sendto(
        userRequest.get_encoded_request(),
        (getServerIPV4(userDnsQuery.serverIPV4), userDnsQuery.port),
    )

    dnsSocket.settimeout(userDnsQuery.timeout)

    # Printing to STDOUT a summary of query
    userDnsQuery.print_summarize_query()

    retries = 0
    start_time = time.time()

    while retries < userDnsQuery.maxRetries:
        try:
            serverResponse, serverAddress = dnsSocket.recvfrom(2048)
            end_time = time.time()
            dnsSocket.close()
            responseTime = end_time - start_time
            print(
                f"Response received after {responseTime} seconds ({retries}) retries)"
            )
            userDnsResponse = dnsResponse(serverResponse)
            userDnsResponse.print_response_content()
            break
        except socket.timeout:
            retries += 1
    # Might want to make sure here that serverAddress is the correct address

    # Might want to check here that the ID is the same as the ID of the dnsQuery

    # print(dnsQuery.parseArguments(sys.argv[1:]))


# For when the program is invoked from the command line (stdin)
if __name__ == "__main__":
    main()
