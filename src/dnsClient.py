""" Python program that implements a DNS client software """

import sys
from dnsQuery import dnsQuery

# For when the program is invoked from the command line (stdin)
if __name__ == "__main__":
    print(dnsQuery.parseArguments(sys.argv[1:]))

