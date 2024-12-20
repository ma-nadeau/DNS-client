from dnsCommonTypes import *
from typing import NamedTuple


class dnsQuery:
    # Program utilization reminder
    utilisation = """ The input should have the following format:
    python dnsClient.py [-t timeout] [-r max-retries] [-p port] [-mx | -ns] @serverIPV4 domainName"""

    def __init__(
        self,
        serverIPV4: IPV4,
        domainName: str,
        timeout: int = 5,
        maxRetries: int = 3,
        port: int = 53,
        recordType: recordType = recordType.A,
    ):
        self.serverIPV4 = serverIPV4
        self.domainName = domainName
        self.timeout = timeout
        self.maxRetries = maxRetries
        self.port = port
        self.recordType = recordType

    @classmethod
    def parseArguments(cls, argv: list[str]):
        # Check that argument length is not out of range
        if not 2 <= len(argv) <= 9:
            raise dnsQueryParsingError(
                "The number of arguments passed is out of range\n" + cls.utilisation
            )

        domainName = argv.pop()
        dnsQuery.validate_domain_name(domainName)

        # Parse IPV4 and validate
        serverIPV4 = argv.pop()
        if serverIPV4[0] != "@":
            raise dnsQueryParsingError("There is a missing '@' symbol for the serverIPV4 argument.\n" + cls.utilisation)
        serverIPV4 = dnsQuery.parseIPV4(serverIPV4[1:])

        optionalArgs = cls.parseOptionalArguments(argv)

        return dnsQuery(serverIPV4, domainName, **optionalArgs)

    @classmethod
    def parseOptionalArguments(cls, argv: list[str]) -> dict:
        optionalArgs = {}
        while len(argv) > 0:
            switch = argv.pop(0)
            availableSwitches = ["-t", "-r", "-p", "-mx", "-ns"]
            # Input validation
            if switch not in availableSwitches:
                raise dnsQueryParsingError(cls.utilisation)
            if switch in availableSwitches[:2] and (len(argv) < 1 or not argv[0].isdigit() or int(argv[0]) < 0):
                raise dnsQueryParsingError("The timeout and max-retries values must be a non-negative integer.")
            if switch == "-p" and (len(argv) < 1 or not argv[0].isdigit() or not 0 <= int(argv[0]) <= 65535):
                raise dnsQueryParsingError("The port number must be a non-negative integer no greater than 65535.")

            match (switch):
                case "-t":
                    if optionalArgs.get("timeout"):
                        raise dnsQueryParsingError(cls.utilisation)
                    optionalArgs["timeout"] = int(argv.pop(0))
                case "-r":
                    if optionalArgs.get("maxRetries"):
                        raise dnsQueryParsingError(cls.utilisation)
                    optionalArgs["maxRetries"] = int(argv.pop(0))
                case "-p":
                    if optionalArgs.get("port"):
                        raise dnsQueryParsingError(cls.utilisation)
                    optionalArgs["port"] = int(argv.pop(0))
                case "-mx" | "-ns":
                    if optionalArgs.get("recordType"):
                        raise dnsQueryParsingError(cls.utilisation)
                    optionalArgs["recordType"] = (
                        recordType.MX if switch == "-mx" else recordType.NS
                    )
                case _:
                    raise dnsQueryParsingError(cls.utilisation)
        return optionalArgs

    @staticmethod
    def parseIPV4(IPV4String: str) -> IPV4:
        format = """The format for the IPv4 address is a.b.c.d where a, b, c, and d are integers in the range [0,255] (inclusive)."""
        IPV4List = IPV4String.split(".")

        if len(IPV4List) != 4 or not all(
            e.isdigit() and 0 <= int(e) <= 255 for e in IPV4List
        ):
            raise dnsQueryParsingError(format)

        IPV4List = [int(e) for e in IPV4List]
        return IPV4(*IPV4List)
    
    @staticmethod
    def validate_domain_name(domain_name: str):
        labels = domain_name.split(".")
        for label in labels:
            if len(label) > 63:
                raise dnsQueryParsingError("The length of labels can't exceed 63 octets.")

    def __repr__(self):
        return f"[serverIPV4:{getServerIPV4(self.serverIPV4)}, domainName:{self.domainName}, timeout:{self.timeout}, maxRetries:{self.maxRetries}, port:{self.port}, recordType:{self.recordType.name}]"

    def print_summarize_query(self):
        print(f"DnsClient sending request for {self.domainName}")
        print(f"Server: {getServerIPV4(self.serverIPV4)}")
        print(f"Request type: {self.recordType.name}")

class dnsQueryParsingError(Exception):
    def __init__(self, value : str) -> None:
        self.value = value
