# do not import anything else from loss_socket besides LossyUDP
from lossy_socket import LossyUDP
# do not import anything else from socket except INADDR_ANY
from socket import INADDR_ANY
import struct
from concurrent.futures import ThreadPoolExecutor
import time
import hashlib
from threading import Timer

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
        self.rec_num = 0
        self.rb = []
        self.closed = False
        self.ack = False  # 0 is data, 1 is ack
        self.last_sent = 0
        self.waitingtime = 0
        self.finack = False
        self.fin = False
        executor = ThreadPoolExecutor(max_workers=1)
        executor.submit(self.listener)

    def send(self, data_bytes: bytes) -> None:
        """Note that data_bytes can be larger than one packet."""
        # Your code goes here!  The code below should be changed!

        # for now I'm just sending the raw application-level data in one UDP payload
        # self.socket.sendto(data_bytes, (self.dst_ip, self.dst_port))
        # Hi Steve we think your solution up there is cringe
        # jk we love u
        # split into pieces
        # part 2: remove some from 1472 to be able to add header
        data = [data_bytes[i:i + 1452] for i in range(0, len(data_bytes), 1452)]
        for i in data:
            hash = hashlib.md5(self.sequence_number.to_bytes(2,'big') + i).digest()
            sendable = struct.pack('hh', self.sequence_number, 0) + hash + i
            self.socket.sendto(sendable, (self.dst_ip, self.dst_port))
            # need to use lock to lock in self.sequence_number so that it won't resend with wrong sequence number, but don't know how to do that
            Timer(0.1, lambda: self.resend(0.1, self.sequence_number, sendable)).start()
            self.ack = False
            self.last_sent = self.sequence_number
            self.sequence_number += 1
        while not self.ack:
            #print("waiting")
            time.sleep(0.01)
            self.waitingtime += 0.01
            if self.waitingtime > .25:
                #resend the thing
                self.socket.sendto(sendable, (self.dst_ip, self.dst_port))
                self.waitingtime = 0
        # self.sequence_number = 0

    def recv(self) -> bytes:
        """Blocks (waits) if no data is ready to be read from the connection."""
        # your code goes here!  The code below should be changed!

        # this sample code just calls the recvfrom method on the LossySocket
        # data, addr = self.socket.recvfrom()
        # take a look at the header we made
        # print("we got to line 43 lol")
        data, addr = self.socket.recvfrom()

        packets = []

        if self.rb:
            for i in self.rb:
                if self.rec_num == int(struct.unpack('hh', i[:4])[0]):
                    # nextseqnumfound = True
                    packets.append(i[20:])
                    self.rb.remove(i)
                    self.rec_num += 1
            returnable = b''
            for i in range(len(packets)):
                # stitch packets together
                returnable += packets[i]
            return returnable
        else:
            return b''
        # header = data[:2]
        # decodedseq = struct.unpack('h', header)[0]
        # print(decodedseq)
        # packets = []
        # if int(decodedseq) == self.rec_num:
        #     nextseqnumfound = True
        #     packets.append(data[2:])
        #     self.rec_num += 1
        #     while nextseqnumfound and self.rb:
        #         nextseqnumfound = False
        #         for i in self.rb:
        #             if self.rec_num == int(struct.unpack('h', i[:2])[0]):
        #                 nextseqnumfound = True
        #                 packets.append(i[2:])
        #                 self.rb.remove(i)
        #                 self.rec_num += 1
        #     # return all packets together
        #     returnable = b''
        #     for i in range(len(packets)):
        #         # stitch packets together
        #         returnable += packets[i]
        #     return returnable
        # else:
        #     self.rb.append(data)
        #     return b''

    def close(self) -> None:
        """Cleans up. It should block (wait) until the Streamer is done with all
           the necessary ACKs and retransmissions"""
        # your code goes here, especially after you add ACKs and retransmissions.
        hash_data = hashlib.md5(self.sequence_number.to_bytes(2, 'big') + b'2').digest()
        sendable = struct.pack('hh', self.sequence_number, 2) + hash_data
        self.socket.sendto(sendable, (self.dst_ip, self.dst_port))
        self.finack = False
        self.fin = False
        while not self.finack:
            #print("waiting")
            time.sleep(0.01)
            self.waitingtime += 0.01
            if self.waitingtime > .25:
                #resend the thing
                self.socket.sendto(sendable, (self.dst_ip, self.dst_port))
                self.waitingtime = 0

        while not self.fin:
            pass
        #sleep 2 seconds, as is requested
        time.sleep(2)
        self.closed = True
        self.socket.stoprecv()
        pass

    def listener(self):
        while not self.closed:  # a later hint will explain self.closed
            try:
                data, addr = self.socket.recvfrom()
                if len(data) == 0:
                    #do nothing
                    break

                ack = struct.unpack('hh', data[:4])[1]
                sequence = struct.unpack('hh', data[:4])[0]
                hash = data[4:20]
                # store the data in the receive buffer
                # see if ack or data
                #if len(data) < 0:
                #    continue
                if int(ack) == 0 and hash == hashlib.md5(sequence.to_bytes(2,'big') + data[20:]).digest():
                    self.rb.append(data)
                    hash_data = hashlib.md5(sequence.to_bytes(2,'big') + b'1').digest()
                    datapacket = struct.pack('hh', struct.unpack('hh', data[:4])[0], 1) + hash_data
                    self.socket.sendto(datapacket, (self.dst_ip, self.dst_port))
                    self.ack = False
                elif int(ack) == 2 and hash == hashlib.md5(sequence.to_bytes(2, 'big') + b'2').digest():
                    #fin
                    hash_data = hashlib.md5(sequence.to_bytes(2, 'big') + b'3').digest()
                    datapacket = struct.pack('hh', struct.unpack('hh', data[:4])[0], 3) + hash_data
                    self.fin = True
                elif int(ack) == 3 and hash == hashlib.md5(sequence.to_bytes(2, 'big') + b'3').digest():
                    #finack
                    self.finack = True
                elif int(ack) == 1 and hash == hashlib.md5(sequence.to_bytes(2, 'big') + b'1').digest():
                    # ack. store something that can be checked by the main thread
                    if self.last_sent == struct.unpack('hh', data[:4])[0]:
                        self.ack = True


                # ...
            except Exception as e:
                print("listener died!")
                print(e)

    def resend(self, time, sequence, packet):
        print(sequence, self.last_sent)
        if sequence > self.last_sent and not self.closed:
            self.socket.sendto(packet, (self.dst_ip, self.dst_port))
            Timer(time, lambda: self.resend(time, sequence, packet)).start()