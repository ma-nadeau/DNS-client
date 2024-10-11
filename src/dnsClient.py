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
        exit()
    
    userRequest = dnsRequest(userDnsQuery.domainName, userDnsQuery.recordType)
        
    try:
        dnsSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        dnsSocket.settimeout(userDnsQuery.timeout)

        # Printing to STDOUT a summary of query
        userDnsQuery.print_summarize_query()

        dnsSocket.sendto(
            userRequest.get_encoded_request(),
            (getServerIPV4(userDnsQuery.serverIPV4), userDnsQuery.port),
        )


        retries = 0
        start_time = time.time()

        while retries <= userDnsQuery.maxRetries:
            try:
                serverResponse, serverAddress = dnsSocket.recvfrom(2048)
            except socket.timeout:
                retries += 1
                continue
            
            # Ignore packets receives from servers other than the one queried
            # Or with IDs different than the one sent
            if serverAddress[0] != getServerIPV4(userDnsQuery.serverIPV4)\
            or int.from_bytes(serverResponse[:2]) != userRequest.ID:
                continue

            end_time = time.time()
            dnsSocket.close()
            responseTime = round(end_time - start_time, 5)
            try:
                print(f"Response received after {responseTime} seconds ({retries} retries)")
                userDnsResponse = dnsResponse(serverResponse)
                userDnsResponse.print_response_content()
            except dnsResponseParsingError as error:
                print("ERROR\tUnexpected response: " + error.value)
            except Exception as error:
                print(str(error))
            break
        if retries > userDnsQuery.maxRetries:
            print(f"ERROR\tMaximum number of retries {userDnsQuery.maxRetries} exceeded")

    except Exception as error:
        print(f'ERROR\t{str(error)}')

# For when the program is invoked from the command line (stdin)
if __name__ == "__main__":
    main()
