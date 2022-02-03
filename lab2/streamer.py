# do not import anything else from loss_socket besides LossyUDP
from lossy_socket import LossyUDP
# do not import anything else from socket except INADDR_ANY
from socket import INADDR_ANY
import struct

class Streamer:
    def __init__(self, dst_ip, dst_port,
                 src_ip=INADDR_ANY, src_port=0):
        """Default values listen on all network interfaces, chooses a random source port,
           and does not introduce any simulated packet loss."""
        self.socket = LossyUDP()
        self.socket.bind((src_ip, src_port))
        self.dst_ip = dst_ip
        self.dst_port = dst_port
        self.sequence_number = 0
        self.max_seqnum = 0
        self.rb = []
    def send(self, data_bytes: bytes) -> None:
        """Note that data_bytes can be larger than one packet."""
        # Your code goes here!  The code below should be changed!

        # for now I'm just sending the raw application-level data in one UDP payload
        #self.socket.sendto(data_bytes, (self.dst_ip, self.dst_port))
        #Hi Steve we think your solution up there is cringe
        #jk we love u
        #split into pieces
        #part 2: remove some from 1472 to be able to add header
        data = [data_bytes[i:i+1470] for i in range(0, len(data_bytes), 1470)]
        for i in data:
            sendable = str(self.sequence_number).encode('utf-8') + i
            self.socket.sendto(sendable, (self.dst_ip, self.dst_port))
            self.sequence_number += 1
            self.max_seqnum += 1
        self.sequence_number = 0
    def recv(self) -> bytes:
        """Blocks (waits) if no data is ready to be read from the connection."""
        # your code goes here!  The code below should be changed!
        
        # this sample code just calls the recvfrom method on the LossySocket
        data, addr = self.socket.recvfrom()
        #take a look at the header we made
        header = data[:3]
        decodedseq = header.decode('utf-8')
        packets = []
        if decodedseq == self.sequence_number:
            nextseqnumfound = True
            while nextseqnumfound and self.sequence_number != self.max_seqnum:
                nextseqnumfound = False
                packets.append(data)
                self.sequence_number += 1
                for i in self.rb:
                    if self.sequence_number == i[:3].decode('utf-8'):
                        nextseqnumfound = True
                        packets.append(i)
                        self.rb.pop(0)
                        self.sequence_number += 1
                    else:
                        break
            if self.sequence_number == self.max_seqnum:
                #this query is done, reset both values
                self.max_seqnum = 0
            #return all packets together
            returnable = packets[0]
            for i in range(1, len(packets), 1):
                #stitch packets together
                returnable += packets[i]
            return returnable
        else:
            self.rb.append(data)
            return b''

    def close(self) -> None:
        """Cleans up. It should block (wait) until the Streamer is done with all
           the necessary ACKs and retransmissions"""
        # your code goes here, especially after you add ACKs and retransmissions.
        pass
