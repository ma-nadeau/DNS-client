from dnsCommonTypes import *
from typing import NamedTuple
from typing import Tuple


class dnsHeader(NamedTuple):
    QR: int
    OPCODE: int
    AA: int
    TC: int
    RA: int
    RCODE: int
    QDCOUNT: int
    ANCOUNT: int
    NSCOUNT: int
    ARCOUNT: int


class MX_record(NamedTuple):
    PREFERENCE: int
    EXCHANGE: str


class dnsAnswer(NamedTuple):
    NAME: str
    TYPE: recordType
    CLASS: int
    TTL: int
    RDLENGTH: int
    RDATA: IPV4 | str | MX_record


class dnsResponse:
    def __init__(self, message: bytes):
        self._message = message
        self.ID = dnsResponse.parseID(self.message)
        self.error = ""
        self.parseMessage(self.message)

    @property
    def message(self) -> bytes:
        return self._message

    @staticmethod
    def parseID(message: bytes) -> int:
        return int.from_bytes(message[:2])
    
    def parseMessage(self, message: bytes):
        # Get header information
        self.header = self.parse_header(message[:12])

        # Skip question section if there is any
        offset = 0
        for i in range(self.header.QDCOUNT):
            name_offset = dnsResponse.parse_name(message[12 + offset:], message)[1]
            offset += name_offset + 4
        
        # Answer section parsing
        answer_section_start = 12 + offset
        answer_section = message[answer_section_start:]
        try:
            self.answers, authority_section = dnsResponse.parse_answer_section(
                answer_section, self.header.ANCOUNT, message
            )
        except dnsResponseParsingError as error:
            self.answers = error.partial_answers
            self.error += error.value
            return

        # Authority section parsing (ignored)
        additonal_section = dnsResponse.parse_answer_section(authority_section, self.header.NSCOUNT, message)[1]

        # Additional section parsing
        try:
            self.additonal_answers = dnsResponse.parse_answer_section(additonal_section, self.header.ARCOUNT, message)[0]
        except dnsResponseParsingError as error:
            self.additonal_answers = error.partial_answers
            self.error += error.value

    def parse_header(self, header: bytes) -> dnsHeader:
        QR = get_bit(header[2], 7) 
        if QR == 0:
            raise dnsResponseParsingError("QR is set to 0, indicating a query for a response expected message.")
        OPCODE = get_range_bit(header[2], 3, 6)
        AA = get_bit(header[2], 2)
        TC = get_bit(header[2], 1)
        RA = get_bit(header[3], 7)
        if RA == 0:
            self.error += "ERROR\tRecursion is not supported by the queried server.\n"
        RCODE = get_range_bit(header[3], 0, 3)
        match RCODE:
            case 1:
                raise dnsResponseParsingError("Format Error\tName server was unable to interpret the query")
            case 2:
                raise dnsResponseParsingError("Server Failure\tName server was unable to process this query due to a problem with the name server")
            case 3:
                raise Exception("NOTFOUND")
            case 4:
                raise dnsResponseParsingError("Not Implemented\tName server does not support the requested kind of query")
            case 5:
                raise dnsResponseParsingError("Refused\tName server refuses to perfom the requested operation for policy reasons")
        QDCOUNT = int.from_bytes(header[4:6])
        ANCOUNT = int.from_bytes(header[6:8])
        NSCOUNT = int.from_bytes(header[8:10])
        ARCOUNT = int.from_bytes(header[10:12])
        return dnsHeader(QR, OPCODE, AA, TC, RA, RCODE, QDCOUNT, ANCOUNT, NSCOUNT, ARCOUNT)

    @staticmethod
    def parse_answer_section(
        answer_section: bytes, ANCOUNT: int, message: bytes
    ) -> Tuple[list[dnsAnswer], bytes]:
        unparsed_answer_section = answer_section
        answers = []
        
        for i in range(ANCOUNT):
            NAME, idx = dnsResponse.parse_name(unparsed_answer_section, message)
            unparsed_answer_section = unparsed_answer_section[idx:]
            # Update unparsed section variable
            try:
                TYPE = recordType.from_value(int.from_bytes(unparsed_answer_section[0:2]))
            except ValueError as error:
                raise dnsResponseParsingError(str(error), answers)
            CLASS = int.from_bytes(unparsed_answer_section[2:4])
            if CLASS != 1:
                raise dnsResponseParsingError("Class field did not have the expected value of 0x0001", answers)
            TTL = int.from_bytes(unparsed_answer_section[4:8])
            RDLENGTH = int.from_bytes(unparsed_answer_section[8:10])
            RDATA = dnsResponse.parse_RDATA(
                unparsed_answer_section[10 : 10 + RDLENGTH], TYPE, message
            )
            unparsed_answer_section = unparsed_answer_section[10 + RDLENGTH:]
            answers.append(dnsAnswer(NAME, TYPE, CLASS, TTL, RDLENGTH, RDATA))
        return answers, unparsed_answer_section

    @staticmethod
    def parse_name(answer: bytes, message) -> Tuple[str, int]:
        idx = 0
        labels = []

        # Loop over the labels
        while answer[idx] != 0:
            # Pointer case
            if check_pointer(answer[idx]):
                offset = get_pointer_value(answer[idx : idx + 2])
                offset_domain_name = dnsResponse.parse_name(message[offset:], message)[0]
                labels.append(offset_domain_name)
                idx += 1  # Skip half the Pointer
                break

            label_length = answer[idx]
            idx += 1  # Skip over label length byte
            label = answer[idx : idx + label_length].decode("L1")
            labels.append(label)
            idx += label_length
        idx += 1  # To skip over the terminating character or the other half of the pointer
        return (".".join(labels), idx)

    @staticmethod
    def parse_RDATA(
        answer: bytes, record_type: recordType, message
    ) -> IPV4 | str | MX_record:
        match record_type:
            case recordType.A:
                return IPV4(answer[0], answer[1], answer[2], answer[3])
            case recordType.NS | recordType.CNAME:
                return dnsResponse.parse_name(answer, message)[0]
            case recordType.MX:
                return MX_record(
                    int.from_bytes(answer[:2]),
                    dnsResponse.parse_name(answer[2:], message)[0],
                )

    def print_response_content(self) -> None:
        if self.header.ANCOUNT > 0:
            print(f"***Answer Section ({self.header.ANCOUNT} records)***")
            self.format_answer_section()
        if self.header.ARCOUNT > 0:
            print(f"***Additional Section ({self.header.ARCOUNT} records) ***")
            self.format_answer_section(True)
        if self.header.ANCOUNT < 1 and self.header.ARCOUNT < 1:
            raise Exception("NOTFOUND")
        if self.error:  # This is mostly for the RA error that wouldn't be raised until now
            raise dnsResponseParsingError(self.error)

    def format_answer_section(self, is_additional_section : bool = False):
        answer_authority = 'auth' if self.header.AA else 'nonauth'
        if is_additional_section:
            answers = self.additonal_answers
        else:
            answers = self.answers
        
        # Loop over answers
        for answer in answers:
            match answer.TYPE:
                case recordType.A:
                    print(f'IP\t{getServerIPV4(answer.RDATA)}\t{answer.TTL}\t{answer_authority}')
                case recordType.CNAME:
                    print(f'CNAME\t{answer.RDATA}\t{answer.TTL}\t{answer_authority}')
                case recordType.MX:
                    print(f'MX\t{answer.RDATA.EXCHANGE}\t{answer.RDATA.PREFERENCE}\t{answer.TTL}\t{answer_authority}')
                case recordType.NS:
                    print(f'NS\t{answer.RDATA}\t{answer.TTL}\t{answer_authority}')
        
        # Raise suspended error if needed
        if len(answers) != (self.header.ARCOUNT if is_additional_section else self.header.ANCOUNT) and self.error:
            raise dnsResponseParsingError(self.error)

# Helper functions
def get_bit(byte: int, position: int) -> int:
    return (byte >> position) & 1


def get_range_bit(byte: int, start_index: int, end_index: int) -> int:
    return (byte >> start_index) & (2 ** (end_index - start_index + 1) - 1)


def check_pointer(byte: int) -> bool:
    # check that it starts with 0b11000000
    return (byte & 0xc0) == 0xc0


def get_pointer_value(pointer: int) -> int:
    return int.from_bytes(pointer) & 0x3FFF

class dnsResponseParsingError(Exception):
    def __init__(self, value : str, partial_answers = None) -> None:
        self.value = value
        self.partial_answers = partial_answers
