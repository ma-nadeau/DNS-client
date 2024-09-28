""" Python program that implements a DNS client software """

import sys
from dnsQuery import dnsQuery
from dnsResponse import dnsResponse
from dnsRequest import dnsRequest
import socket
import time


def main():
    # import pdb

    # pdb.set_trace()

    try:
        userDnsQuery = dnsQuery.parseArguments(sys.argv[1:])
        userRequest = dnsRequest(userDnsQuery.domainName, userDnsQuery.recordType)

        dnsSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        dnsSocket.sendto(
            userRequest.get_encoded_request(),
            (userDnsQuery.getServerIPV4(), userDnsQuery.port),
        )

        dnsSocket.settimeout(userDnsQuery.timeout)
        # Printing to STDOUT a summary of query
        # dnsQuery.print_query_summary()
        userDnsQuery.print_summarize_query()
        start_time = time.time()
        response_received = False
        retries = 0

        while retries < userDnsQuery.maxRetries and not response_received:
            try:
                serverResponse, serverAddress = dnsSocket.recvfrom(2048)
                response_received = True
                dnsSocket.close()
                end_time = time.time()
                responseTime = end_time - start_time
                print(
                    f"Response recceived after {responseTime} seconds ({retries}) retries"
                )
                userDnsResponse = dnsResponse(serverResponse)
                print(userDnsResponse)
                userDnsResponse.print_response_content()
            except socket.timeout:
                retries += 1
                print("FUCK")
        # Might want to make sure here that serverAddress is the correct address

        # Might want to check here that the ID is the same as the ID of the dnsQuery

        print(dnsQuery.parseArguments(sys.argv[1:]))

    except KeyboardInterrupt:
        print("TESTING!!!!")


# For when the program is invoked from the command line (stdin)
if __name__ == "__main__":
    main()
