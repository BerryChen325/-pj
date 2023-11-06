from pj2.simulator import sim
from pj2.simulator import to_layer_three
from pj2.event_list import evl
from pj2.packet import *
from pj2.circular_buffer import circular_buffer

class A:
    def __init__(self):
        # go back n, the initialization of A
        # Initialize the initial sequence number to 0.
        # You need to initialize the circular buffer, using "circular_buffer(max)". max is the number of the packets that the buffer can hold
        # You can set the estimated_rtt to be 30, which is used as a parameter when you call start_timer

        self.seq = 0    # 下一个要发送的包的编号
        self.estimated_rtt = 30
        self.max_buffer_size = 50   # 自己加的，buffer的最大容量
        self.N = 8  # 自己加的，窗口大小N
        self.c_b = circular_buffer(self.max_buffer_size, self.N)
        return

    def A_output(self, m):
        # go back n, A_output
        # If the buffer is full, just drop the packet
        # Construct the packet based on the message. Make sure that the sequence number is correct
        # Send the packet and save it to the circular buffer using "push()" of circular_buffer
        # Set the timer using "evl.start_timer(entity, time)", and the time should be set to estimated_rtt. Make sure that there is only one timer started in the event list
        
        if self.c_b.isfull():
            print("A: Buffer is full, dropping packet.")
            return

        pkt = packet(seqnum=self.seq, acknum=0, payload=m)
        self.c_b.push(pkt)
                
        # 如果pkt加入后在window内，则立刻发出；否则因为窗口限制，不能发出
        # 在pkt加入buffer以前，window中是没有unsent_pkt的，所以下面的pkt_sent要么是None，要么是刚加入的pkt
        pkt_sent = self.c_b.next_unsent_pkt_in_window()
        if pkt_sent:
            send_pkt("A", pkt_sent)
            # self.c_b.update_next_unsent()
            # print("\tA buffer: head={},tail={},next_unsent={}".format(self.c_b.read, self.c_b.write, self.c_b.next_unsent))
        else:
            print("A窗口满了，pkt没有发出: seqnum={}".format(pkt.seqnum))
        print("\tA buffer: head={},tail={},next_unsent={}".format(self.c_b.read, self.c_b.write, self.c_b.next_unsent))

        # 如果计时器未启动，说明在pkt之前没有已发送未ACK的包，说明pkt一定发出了且一定是第一个已发送未ACK的包，
        # 此时需要启动计时器
        # 而如果计时器已经启动，则pkt就算发出了也不是第一个已发送未ACK的包，所以跟计时器没有关系，
        # 此时不应该调整计时器
        if evl.timer_isnot_running():
            evl.start_timer("A", self.estimated_rtt)

        # Update the sequence number
        self.seq = (self.seq + 1) % self.max_buffer_size

    def A_input(self, pkt):
        # go back n, A_input
        # Verify that the packet is not corrupted
        # Update the circular buffer according to the acknowledgement number using "pop()"

        if pkt.checksum == pkt.get_checksum():
            acknum = pkt.acknum
            print("A: ACK received: acknum={}".format(acknum))

            # 关于收到ACK后如何处理（计时器是否重启？未ACK的包是否重传？窗口中新来的未发送的包是否发送？）：
            # 这里就按照pj任务文档里那个链接[https://www.cnblogs.com/crazyshanshan/p/16046562.html]的说法来做，
            # 链接文章里没说明的地方我就自己发挥了
            # 实际上关于收到ACK如何处理，那个链接、谢希仁的计算机网络书、chatgpt的说法都不相同。

            # 这里我的处理方案是：
            # 只要这个ACK导致窗口移动，就重启计时器；
            # 只要窗口中出现了新的包，就发送出去；
            # 已发送未ACK的包并不重传

            if not self.c_b.isempty() and self.c_b.top().seqnum <= acknum:
                # 说明有包会被pop出去，即窗口会移动。此时重启计时器
                evl.remove_timer()
                evl.start_timer("A", self.estimated_rtt)
            # 把已ACK的包都pop出去
            while not self.c_b.isempty() and self.c_b.top().seqnum <= acknum:
                self.c_b.pop()
            # 这里处理一下特殊情况：buffer已经被清空。此时应该把计时器停掉
            if self.c_b.isempty() and (not evl.timer_isnot_running()):
                evl.remove_timer()

            # 把window中新的包发送出去
            pkt_sent = self.c_b.next_unsent_pkt_in_window()
            while pkt_sent:
                send_pkt("A", pkt_sent)
                # self.c_b.update_next_unsent()
                pkt_sent = self.c_b.next_unsent_pkt_in_window()
                
            print("\tA buffer: head={},tail={},next_unsent={}".format(self.c_b.read, self.c_b.write, self.c_b.next_unsent))

        else:
            print("A: ACK checksum error: acknum={}".format(pkt.acknum))

    # 超时，则整个window中的包全部重传
    def A_timerinterrupt(self):
        # go back n, A_timerinterrupt
        # Read all the sent packet that it is not acknowledged using "read_all()" of the circular buffer and resend them
        # If you need to resend packets, set a timer after that

        print("A超时重传")
        # unacked_packets = self.c_b.read_all()
        unacked_packets = self.c_b.read_window()

        for pkt in unacked_packets:
            # to_layer_three("A", pkt)
            send_pkt("A", pkt)

        # 如果有unacked packets，要启动计时器
        # （注意因为只有一个计时器，而这个函数是超时处理函数，所以此时已经没有计时器在运行了，所以不是重启计时器而是启动计时器）
        if unacked_packets:
            evl.start_timer("A", self.estimated_rtt)


a = A()
