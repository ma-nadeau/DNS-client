from dnsCommonTypes import *
from typing import NamedTuple


class dnsHeader(NamedTuple):
    QR: int
    OPCODE: int
    AA: int
    TC: int
    RA: int
    RCODE: int
    QDCOUNT: int
    ANCOUNT: int


class MX_record(NamedTuple):
    PREFERENCE: int
    EXCHANGE: str


class dnsAnswer(NamedTuple):
    NAME: tuple
    TYPE: recordType
    # TODO: ask what QCODE is. It doesn't appear in question packet description
    CLASS: int
    TTL: int
    RDLENGTH: int
    RDATA: IPV4 | str | MX_record


class dnsResponse:
    def __init__(self, message: bytes):
        self.message = message
        self.ID = dnsResponse.parseID(self.message)
        self.parseMessage(message)

    @staticmethod
    def parseID(message: bytes) -> int:
        return int.from_bytes(message[:2])

    def parseMessage(self, message: bytes):
        import pdb

        pdb.set_trace()
        self.header = dnsResponse.parse_header(message[:12])
        answer_section_start = 12 + self.header.QDCOUNT
        answer_section_end = answer_section_start + self.header.ANCOUNT
        answer_section = message[answer_section_start:answer_section_end]
        self.answers = dnsResponse.parseAnswerSection(
            answer_section, self.header.ANCOUNT
        )

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
        # TODO: Ask prof if we care about Additional Records section
        # TODO: Ask prof if repsonse message has any values/records in the question section
        return dnsHeader(QR, OPCODE, AA, TC, RA, RCODE, QDCOUNT, ANCOUNT)

    @staticmethod
    def parseAnswerSection(answer_section: bytes, ANCOUNT: int) -> NamedTuple:
        import pdb

        pdb.set_trace()
        unparsed_answer_section = answer_section
        answers = []
        for i in range(ANCOUNT):
            NAME, idx = dnsResponse.parseName(unparsed_answer_section)
            unparsed_answer_section = unparsed_answer_section[
                idx:
            ]  # Update unparsed section variable
            TYPE = recordType(int.from_bytes(unparsed_answer_section[:2]))
            CLASS = int.from_bytes(unparsed_answer_section[2:4])
            TTL = int.from_bytes(unparsed_answer_section[4:8])
            RDLENGTH = int.from_bytes(unparsed_answer_section[8:10])
            RDATA = dnsResponse.parse_RDATA(
                unparsed_answer_section[10 : 10 + RDLENGTH], TYPE
            )
            answers.append(dnsAnswer(NAME, TYPE, CLASS, TTL, RDLENGTH, RDATA))
        return answers

    @staticmethod
    def extract_value_at_pointer(answer: bytes, pointer_offset: int) -> list[str]:
        labels = []
        while answer[pointer_offset] != 0:
            label_length = answer[pointer_offset]
            pointer_offset += 1  # Skip over label length byte
            label = answer[pointer_offset : pointer_offset + label_length].decode(
                "ascii"
            )
            labels.append(label)
            pointer_offset += label_length
        return labels

    @staticmethod
    def parseName(answer: bytes):
        import pdb

        pdb.set_trace()
        idx = 0
        labels = []
        # TODO: fix loop condition, it seems that every domain name in the answer terminates with a 0
        while answer[idx] != 0:
            if check_pointer(answer[idx], idx):
                offset = get_pointer_value(answer[idx : idx + 2])
                offset_labels = dnsResponse.extract_value_at_pointer(answer, offset)
                labels.extend(offset_labels)
                idx += 2
            else:
                label_length = answer[idx]
                idx += 1  # Skip over label length byte
                label = answer[idx : idx + label_length].decode("ascii")
                labels.append(label)
                idx += label_length
        idx += 1  # To skip the null character
        return (".".join(labels), idx)

    @staticmethod
    def parse_RDATA(answer: bytes, record_type: recordType) -> IPV4 | str | MX_record:
        match (recordType):
            case recordType.A:
                return IPV4(answer[0], answer[1], answer[2], answer[3])
            case recordType.NS | recordType.CNAME:
                # TODO: Does the name of the alias also have the same format as QNAME?
                return dnsResponse.parseName(answer)
            case recordType.MX:
                return MX_record(
                    int.from_bytes(answer[:2]), dnsResponse.parseName(answer[2:])
                )


# Helper functions
def get_bit(byte: int, position: int) -> int:
    return (byte >> position) & 1


def get_range_bit(byte: int, start_index: int, end_index: int) -> int:
    return (byte >> start_index) & (2 ** (end_index - start_index + 1) - 1)


def check_pointer(byte: bytes) -> bool:
    # check that it starts with 0b11000000
    return (byte & 0b11000000) == 0b11000000


def get_pointer_value(pointer: bytes) -> int:
    return pointer & 0b0011111111111111
