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
    # TODO: ask what QCODE is. It doesn't appear in question packet description
    CLASS: int
    TTL: int
    RDLENGTH: int
    RDATA: IPV4 | str | MX_record


class dnsResponse:
    def __init__(self, message: bytes):
        self._message = message
        self.ID = dnsResponse.parseID(self.message)
        self.parseMessage(self.message)

    @property
    def message(self) -> bytes:
        return self._message

    @staticmethod
    def parseID(message: bytes) -> int:
        return int.from_bytes(message[:2])
    
    def parseMessage(self, message: bytes):
        # Get header information
        self.header = dnsResponse.parse_header(message[:12])

        # Skip question section if there is any
        offset = 0
        for i in range(self.header.QDCOUNT):
            name_offset = dnsResponse.parse_name(message[12 + offset:], message)[1]
            offset += name_offset + 4
        
        # Answer section parsing
        answer_section_start = 12 + offset
        answer_section = message[answer_section_start:]
        self.answers, authority_section = dnsResponse.parse_answer_section(
            answer_section, self.header.ANCOUNT, message
        )

        # Authority section parsing (ignored)
        additonal_section = dnsResponse.parse_answer_section(authority_section, self.header.NSCOUNT, message)[1]

        # Additional section parsing
        self.additonal_answers = dnsResponse.parse_answer_section(additonal_section, self.header.ARCOUNT, message)[0]

    @staticmethod
    def parse_header(header: bytes) -> dnsHeader:
        QR = get_bit(header[2], 0)
        OPCODE = get_range_bit(header[2], 1, 4)
        AA = get_bit(header[2], 5)
        TC = get_bit(header[2], 6)
        RA = get_bit(header[3], 0)
        RCODE = get_range_bit(header[3], 4, 7)
        QDCOUNT = int.from_bytes(header[4:6])
        ANCOUNT = int.from_bytes(header[6:8])
        NSCOUNT = int.from_bytes(header[8:10])
        ARCOUNT = int.from_bytes(header[10:12])
        # TODO: Ask prof if repsonse message has any values/records in the question section
        return dnsHeader(QR, OPCODE, AA, TC, RA, RCODE, QDCOUNT, ANCOUNT, NSCOUNT, ARCOUNT)

    @staticmethod
    def parse_answer_section(
        answer_section: bytes, ANCOUNT: int, message: bytes
    ) -> Tuple[list[dnsAnswer], bytes]:
        unparsed_answer_section = answer_section
        answers = []
        # TODO: Add
        for i in range(ANCOUNT):
            NAME, idx = dnsResponse.parse_name(unparsed_answer_section, message)
            unparsed_answer_section = unparsed_answer_section[idx:]
            # Update unparsed section variable
            TYPE = recordType.from_value(int.from_bytes(unparsed_answer_section[0:2]))
            CLASS = int.from_bytes(unparsed_answer_section[2:4])
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
                # TODO: Does the name of the alias also have the same format as QNAME?
                return dnsResponse.parse_name(answer, message)[0]
            case recordType.MX:
                return MX_record(
                    int.from_bytes(answer[:2]),
                    dnsResponse.parse_name(answer[2:], message)[0],
                )

    # TODO: add alias and authority, what are they???
    def print_response_content(self) -> None:
        if self.header.ANCOUNT > 0:
            print(f"***Answer Section ({self.header.ANCOUNT} records)***")
            self.format_answer_section()
        if self.header.ARCOUNT > 0:
            print(f"***Additional Section ({self.header.ANCOUNT} records) ***")
            self.format_answer_section(True)
        if self.header.ANCOUNT < 1 and self.header.ARCOUNT < 1:
            print("NOTFOUND")
        # TODO:
        # if self.additional < 1 :
        #   print("NOTFOUND")
        # for ad in self.additional:
        #
        #

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
