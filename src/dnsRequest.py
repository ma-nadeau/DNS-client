from random import randint


class dnsRequest:
    # Note that the UDP packets are encoded in big-endian (network byte order)

    def __init__(self, domain_name, q_type):
        self.ID = randint(0,2**16-1)
        self.domain_name = domain_name
        self.q_type = q_type
    
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
        print(header)

        return header

    def perform_QNAME_encoding(self):

        # Check if labels are less than 63 Octets long
        if len(self.domain_name.replace('.', '')) > 63:
            raise ValueError('Domain name too long')

        # Split domain name at '.' -> www.mcgill.ca = ['www', 'mcgill', 'ca')
        labels = self.domain_name.split('.')
        q_name = b''

        for label in labels:
            # Get the length of the label
            len_label = len(label)
            # add the length + the label ascii encoding
            q_name += len_label.to_bytes() + label.encode('ascii')

        # Terminates with zero-length octet
        q_name += b'\x00'
        return q_name


    def getQuestion(self) -> bytes:

        question = b''
        # Get the ecnoding for QNAME
        question += self.perform_QNAME_encoding()

        # Define query types
        query_types = {
            "A": 0x0001,  # Type-A query (host address)
            "NS": 0x0002,  # Type-NS query (name server)
            "MX": 0x000f  # Type-MX query (mail server)
        }
        # Add the encoding for the query type to question (i,e, QTYPE)
        if self.q_type not in query_types:
            raise ValueError('Invalid q_type')
        else:
            question += query_types[self.q_type].to_bytes(2)
        # For our project, QCLASS is always 0x0001
        question += (0x0001).to_bytes(2)
        return question