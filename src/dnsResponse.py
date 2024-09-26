from dnsCommonTypes import *
from typing import NamedTuple

class dnsHeader(NamedTuple):
    QR : int
    OPCODE : int
    AA : int
    TC : int
    RA : int
    RCODE : int
    QDCOUNT : int
    ANCOUNT : int

class MX_record(NamedTuple):
    PREFERENCE : 
    EXCHANGE : 

class dnsAnswer(NamedTuple):
    NAME : tuple
    TYPE : recordType
    #TODO: ask what QCODE is. It doesn't appear in question packet description
    CLASS : int
    TTL : int
    RDLENGTH : int
    RDATA : tuple | IPV4 | MX_record


class dnsResponse:
    def __init__(self, message : bytes):
        self.message = message
        self.ID = dnsResponse.parseID(self.message)
    
    @staticmethod
    def parseID(message : bytes) -> int:
        return int.from_bytes(message[:2])

    def parseMessage(self, message : bytes):
        header = self.dnsparseHeader(message[:12])
        answer_section_start = 12 + header.QDCOUNT
        answer_section_end = answer_section_start + header.ANCOUNT
        answer_section = message[answer_section_start:answer_section_end]
        
        return True
    
    def parseHeader(self, header : bytes) -> NamedTuple:
        if hasattr(self, 'header'):
            return self.header
        
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
        self.header = dnsHeader(QR, OPCODE, AA, TC, RA, RCODE, QDCOUNT, ANCOUNT)
        return self.header

    def parseAnswerSection(self, answerSection : bytes, ANCOUNT : int) -> NamedTuple:
        for i in range(ANCOUNT):
            parseName(answerSection)
            
        pass

    def parseName(answer : bytes):
        i = 0
        labels = []
        while(answer[i] != 0):
            label_length = answer[i]
            i += 1 # Skip over label length byte
            label = answer[i:i+label_length].decode('ascii')
            labels.append(label)
            i += label_length
        return tuple(labels)

# Helper functions
def get_bit(byte : int, position: int) -> int:
    return (byte >> position) & 1
    
def get_range_bit(byte : int, start_index: int, end_index: int) -> int:
    return (byte >> start_index) & (2 ** (end_index - start_index + 1) - 1)
        