# from pj2.simulator import to_layer_five
from pj2.packet import send_ack, send_data


class B:
    def __init__(self):
        # go back n, the initialization of B
        # The state only need to maintain the information of expected sequence number of packet
        self.seqnum = 0     # B下一个应该收到的seqnum
        return

    def B_output(self, m):
        return

    def B_input(self, pkt):
        # go back n, B_input
        # You need to verify the checksum to make sure that packet isn't corrupted
        # If the packet is either corrupted or not the expected one
        # If the packet is the right one, you need to pass to the fifth layer using "to_layer_five(entity,payload)"
        # Send acknowledgement using "send_ack(entity, seq)" based on the correctness of received packet
        # If the packet is the correct one, in the last step, you need to update its state ( update the expected sequence number)

        # print("B收到pkt：seqnum={}".format(pkt.seqnum))
        if pkt.checksum == pkt.get_checksum() and pkt.seqnum == self.seqnum:
            # Packet is not corrupted and is the expected one
            # to_layer_five("B", pkt)
            print("B收到pkt: seqnum={}".format(pkt.seqnum))
            send_data("B", pkt)
            send_ack("B", self.seqnum)
            self.seqnum = pkt.seqnum + 1
            # print("//B.seqnum = {}".format(self.seqnum))
        else:
            # Packet is corrupted or not the expected one, send an ACK for the last correctly received packet
            if pkt.checksum != pkt.get_checksum():
                print("B收到pkt但checksum error: seqnum={}".format(pkt.seqnum))
            else:
                print("B收到pkt: seqnum={}".format(pkt.seqnum))
            send_ack("B", self.seqnum - 1)
        
    def B_timerinterrupt(self):
        return


b = B()
