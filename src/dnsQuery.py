from enum import Enum
from typing import NamedTuple

class recordType(Enum):
    A = 1
    MX = 2
    NS = 3

class IPV4(NamedTuple):
    a : int
    b : int
    c : int
    d : int

class dnsQuery:
    # Program utilization reminder
    utilisation = """ The input should have the following format:
    [-t timeout] [-r max-retries] [-p port] [-mx | -ns] @serverIPV4 domainName"""

    def __init__(self, serverIPV4 : IPV4, domainName : str, timeout : int = 5, maxRetries : int = 3, port : int = 53, recordType : recordType = recordType.A):
        self.serverIPV4 = serverIPV4
        self.domainName = domainName
        self.timeout = timeout
        self.maxRetries = maxRetries
        self.port = port
        self.recordType = recordType
    
    def __repr__(self):
        return f'[serverIPV4:{self.getServerIPV4()}, domainName:{self.domainName}, timeout:{self.timeout}, maxRetries:{self.maxRetries}, port:{self.port}, recordType:{self.recordType.name}]'

    def getServerIPV4(self):
        return ".".join(str(e) for e in list(self.serverIPV4))

    @classmethod
    def parseArguments(cls, argv : list[str]):
        # Check that argument length is not out of range
        if not 2 <= len(argv) <= 9:
            raise ValueError("The number of arguments passed is out of range\n" + cls.utilisation)
        
        domainName = argv.pop()

        # Parse IPV4 and validate
        serverIPV4 = argv.pop()
        if serverIPV4[0] != "@":
            print(serverIPV4[0])
            raise ValueError(cls.utilisation)
        serverIPV4 = dnsQuery.parseIPV4(serverIPV4[1:])

        optionalArgs = cls.parseOptionalArguments(argv)

        return dnsQuery(serverIPV4, domainName, **optionalArgs)
        
    @classmethod
    def parseOptionalArguments(cls, argv : list[str]) -> dict:
        optionalArgs = {}
        while(len(argv) > 0):
            switch = argv.pop(0)
            availableSwitches = ["-t", "-r", "-p", "-mx", "-ns"]
            # Input validation
            if switch not in availableSwitches \
            or (switch in availableSwitches[:3] and (len(argv) < 1 or not argv[0].isdigit() or int(argv[0]) < 0)):
                raise ValueError(cls.utilisation)
            
            match(switch):
                case "-t":
                    if optionalArgs.get("timeout"):
                        raise ValueError(cls.utilisation)
                    optionalArgs["timeout"] = int(argv.pop(0))
                case "-r":
                    if optionalArgs.get("maxRetries"):
                        raise ValueError(cls.utilisation)
                    optionalArgs["maxRetries"] = int(argv.pop(0))
                case "-p":
                    if optionalArgs.get("port"):
                        raise ValueError(cls.utilisation)
                    optionalArgs["port"] = int(argv.pop(0))
                case "-mx" | "-ns":
                    if optionalArgs.get("recordType"):
                        raise ValueError(cls.utilisation)
                    optionalArgs["recordType"] = recordType.MX if switch == "-mx" else recordType.NS
        return optionalArgs
            

    @staticmethod
    def parseIPV4(IPV4String : str) -> IPV4:
        format = """The format for the IPv4 address is a.b.c.d where a, b, c, and d are integers in the range [0,255] (inclusive)."""
        IPV4List = IPV4String.split('.')

        if len(IPV4List) != 4 or not all(e.isdigit() and 0 <= int(e) <= 255 for e in IPV4List):
            raise ValueError(format)
        
        IPV4List = [int(e) for e in IPV4List]
        return IPV4(*IPV4List)
        