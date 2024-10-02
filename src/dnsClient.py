""" Python program that implements a DNS client software """

import sys
from dnsQuery import dnsQuery, dnsQueryParsingError
from dnsResponse import dnsResponse, dnsResponseParsingError
from dnsRequest import dnsRequest
from dnsCommonTypes import getServerIPV4
import socket
import time


def main():
    try:
        userDnsQuery = dnsQuery.parseArguments(sys.argv[1:])
    except dnsQueryParsingError as error:
        print("ERROR\tIncorrect input syntax: " + error.value)
    
    userRequest = dnsRequest(userDnsQuery.domainName, userDnsQuery.recordType)
        
    try:
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

        while retries <= userDnsQuery.maxRetries:
            try:
                serverResponse, serverAddress = dnsSocket.recvfrom(2048)
            except socket.timeout:
                retries += 1
                continue
            end_time = time.time()
            dnsSocket.close()
            responseTime = end_time - start_time
            try:
                userDnsResponse = dnsResponse(serverResponse)
                print(f"Response received after {responseTime} seconds ({retries}) retries)")
                userDnsResponse.print_response_content()
            except dnsResponseParsingError as error:
                print("ERROR\tUnexpected response: " + error.value)
            except Exception as error:
                print(error)
            break
        if retries > userDnsQuery.maxRetries:
            print(f"ERROR\tMaximum number of retries {userDnsQuery.maxRetries} exceeded")
            
        # Might want to make sure here that serverAddress is the correct address

        # Might want to check here that the ID is the same as the ID of the dnsQuery

        # print(dnsQuery.parseArguments(sys.argv[1:]))
    except Exception as error:
        print("ERROR\t" + error)

# For when the program is invoked from the command line (stdin)
if __name__ == "__main__":
    main()
