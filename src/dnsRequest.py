from random import randint
from dnsCommonTypes import recordType

class dnsRequest:
    # Note that the UDP packets are encoded in big-endian (network byte order)

    # Labels cannot exceed 63 octets
    MAX_LABEL_SIZE = 63

    def __init__(self, domain_name : str, q_type : recordType):
        self.ID = randint(0,2**16-1)
        self.domain_name = domain_name
        self.q_type = q_type
    
    def get_encoded_request(self):
        header = self.get_header()
        encoded_question = self.get_encoded_question()
        return header + encoded_question
    
    def get_header(self) -> bytes:
        # Return the already computed instance variable if existant
        if hasattr(self, 'header'):
            return self.header
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

        #Update the instance variable
        self.header = header
        return header

    def get_encoded_question(self) -> bytes:
        # Return the already computed instance variable if existant
        if hasattr(self, 'encoded_question'):
            return self.encoded_question

        question = b''
        # Get the ecnoding for QNAME
        question += self.get_QNAME_encoding()

        # Add the encoding for the query type to question (i,e, QTYPE)
        question += self.q_type.value.to_bytes(2)
        # For our project, QCLASS is always 0x0001
        question += (0x0001).to_bytes(2)

        #Update the instance variable
        self.encoded_question = question
        return question

    def get_QNAME_encoding(self):
        # Fetch labels from domain name by splitting at '.' -> www.mcgill.ca = ['www', 'mcgill', 'ca']
        labels = self.domain_name.split('.')

        q_name = b''

        for label in labels:
            # Get the length of the label
            len_label = len(label)
            # Make sure that labels are less than 63 Octets long
            if len(label) > 63:
                raise ValueError(f'Label {label} in doemain name is too long (labels are restricted to {dnsRequest.MAX_LABEL_SIZE} octets max)')
            # add the length + the label ascii encoding
            q_name += len_label.to_bytes() + label.encode('ascii')

        # Terminates with zero-length octet
        q_name += b'\x00'
        return q_name
