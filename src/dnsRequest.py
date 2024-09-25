from random import randint

class dnsRequest:
    # Note that the UDP packets are encoded in big-endian (network byte order)

    def __init__(self):
        self.ID = randint(0,2**16-1)
    
    def getHeader(self) -> bytes:
        header = b''
        header += self.ID.to_bytes(2)  #Add the ID at the very top of the header
        # Adding the second line of the header which specifies 
        # QR = 0, Opcode = 0000, AA = 0, TC = 0, RD = 1, RA = 0, Z = 000, RCODE = 0000 (in order)
        header += (0b0000000100000000).to_bytes(2)
        # Adding the third line of the header which specifies 
        # QDCOUNT = 0x0001 always in our case
        header += b'\x00\x01'
        # Finally, ANCOUNT, NSCOUNT, and ARCOUNT are all 0x0000 because this is a request message
        header += 6*b'\x00'

        return header
