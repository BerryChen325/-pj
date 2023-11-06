from pj2.msg import *
from pj2.event_list import *
from pj2.event import *

import random
import copy


class simulator:
    def __init__(self):
        self.TRACE = 0  # for my debugging
        self.nsim = 0  # number of messages from 5 to 4 so far
        self.nsimmax = 20#26  # number of msgs to generate, then stop
        self.time = 0.000
        self.lossprob = 0.3#0.9  # probability that a packet is dropped
        self.corruptprob = 0.4#0.6  # probability that one bit is packet is flipped
        self.Lambda = 10  # arrival rate of messages from layer 5
        self.ntolayer3 = 0  # number sent into layer 3
        self.nlost = 0  # number lost in media
        self.ncorrupt = 0  # number corrupted by media

        self.envlist = evl

        self.ntolayer3 = 0
        self.nlost = 0
        self.ncorrupt = 0
        self.time = 0.0  # initialize time to 0.0
        self.generate_next_arrival()  # initialize event list

    def generate_next_arrival(self):
        time = self.time + self.Lambda
        self.envlist.insert(event(time, "FROM_LAYER5", "A"))
        return

    def run(self):
        self.print_args()
        # self.envlist.print_self()
        while (1):
            self.envlist.print_self()
            # print("========")
            env = self.envlist.remove_head()
            if env == None:
                print("simulation end!")
                return
            else:
                #env.print_self()
                self.time = env.evtime

            if self.nsim > self.nsimmax:
                print("simulation end")
                return

            if env.evtype == "FROM_LAYER5":
                ch = chr(97 + self.nsim % 26)
                m = msg(ch)
                self.nsim = self.nsim + 1
                if self.nsim < self.nsimmax:
                    self.generate_next_arrival()
                if env.eventity == "A":
                    from pj2.A import a
                    a.A_output(m)
                else:
                    from pj2.B import b
                    b.B_output(m)

            elif env.evtype == "FROM_LAYER3":
                pkt2give = env.pkt
                if env.eventity == "A":
                    from pj2.A import a
                    a.A_input(pkt2give)
                else:
                    from pj2.B import b
                    b.B_input(pkt2give)

            elif env.evtype == "TIMER_INTERRUPT":
                if env.eventity == "A":
                    a.A_timerinterrupt()
                else:
                    b.B_timerinterrupt()

            else:
                print("!!!!!!!????")
    
    # 加的，用于打印模拟实验的参数
    def print_args(self):
        print("********************************")   # 4*8=32个星号
        print(" Simulation args:")
        print("  nsimmax:\t\t{}".format(self.nsimmax))
        print("  lossprob:\t\t{}".format(self.lossprob))
        print("  corruptprob:\t{}".format(self.corruptprob))
        print("  Lambda:\t\t\t{}".format(self.Lambda))
        print("********************************")   # 4*8=32个星号


def to_layer_three(AorB, pkt):
    log_message = "{}: packet sent: seqnum={}, acknum={}".format(AorB, pkt.seqnum, pkt.acknum)
    if random.uniform(0, 1) < sim.lossprob:
        print(log_message+" [包丢失]")
        return

    packet = copy.deepcopy(pkt)
    # print("{}: pkt sent: acknum={}, seqnum={}".format(AorB, packet.acknum, packet.seqnum))

    if random.uniform(0, 1) < sim.corruptprob:
        if packet.payload!=0:
            packet.payload.data = packet.payload.data[0:-1] + "1"
        else:
            packet.seqnum=-1
        log_message += " [包出错]"
        # print(log_message+" [包出错]")

    q = sim.envlist.head
    lasttime = sim.time
    while q != None:
        if q.eventity == AorB and q.evtype == "FROM_LAYER3":
            lasttime = q.evtime

        q=q.next

    eventime = lasttime + 1 + 9 * random.uniform(0, 1)
    if AorB == "A":
        sim.envlist.insert(event(eventime, "FROM_LAYER3", "B", packet))
    else:
        sim.envlist.insert(event(eventime, "FROM_LAYER3", "A", packet))
    print(log_message)

def to_layer_five(AorB, data):
    # 应当是向layer five传输数据的相关处理（模拟中不考虑这部分）
    return
    # print("{}: data recieved: acknum={}, seqnum={}".format(AorB, pkt.acknum, pkt.seqnum))


sim = simulator()
