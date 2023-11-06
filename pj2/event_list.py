from pj2.event import event


class event_list:
    def __init__(self):
        self.head = None

    def insert(self, p):
        # print("event_list.insert: ", end='')
        # p.print_self()
        q = self.head
        if (q == None):  # if head is None
            self.head = p
            self.head.next = None
            self.head.prev = None
        else:
            qold = q
            while (q != None and p.evtime > q.evtime):
                qold = q
                q = q.next

            # now qold.next==q, p.evtime<=q.evtime
            if (q == None):
                qold.next = p
                p.prev = qold
                p.next = None

            else:
                if (q == self.head):
                    p.next = q
                    p.prev = None
                    q.prev = p
                    self.head = p
                else:
                    p.next = q
                    p.prev = q.prev
                    p.prev.next = p
                    q.prev = p

    def print_self(self):
        q = self.head
        print("\n--------------\n| Event List Follows:")
        while (q != None):
            print("|   Event time:{} , type: {} entity: {}".format(q.evtime, q.evtype, q.eventity))
            q = q.next

        print("--------------\n")

    def remove_head(self):
        temp = self.head
        if temp == None:
            return None
        if (self.head.next == None):
            self.head = None
            return temp
        else:
            self.head.next.prev = None
            self.head = self.head.next
            return temp

    def start_timer(self, AorB, time):
        from pj2.simulator import sim
        self.insert(event(sim.time+time, "TIMER_INTERRUPT", AorB))

    def remove_timer(self):
        q = self.head
        # 下面的修改是错的，还是应该用原来的remove_timer
        # 因为发送方只用一个计时器（不是每个pkt有一个计时器），计时器计的是最早的已发送但未ACK的包的时
        while (q.evtype != "TIMER_INTERRUPT"):
            q = q.next

        if q.prev == None:
            self.head = q.next
        elif q.next == None:
            q.prev.next = None
        else:
            q.next.prev = q.prev
            q.prev.next = q.next
        
        # 原先给的remove_timer是错的。超时重传时应该清空原有的所有timer，而不是只清空一个timer
        # （因为重传时是把所有尚未ack的包都重传了，所以所有timer都要更新！）
        # 下面是我修改后的remove_timer，清空所有timer
        # while (q != None):
        #     if (q.evtype == "TIMER_INTERRUPT"):
        #         if q.prev == None:
        #             self.head = q.next
        #         elif q.next == None:
        #             q.prev.next = None
        #         else:
        #             q.next.prev = q.prev
        #             q.prev.next = q.next
        #     q = q.next

    # 加的，判断是否已经有客户端AorB的计时器在工作
    # 因为这里只模拟A到B发包，所以只有A有timer，所以AorB肯定是A，
    # 这里为了方便就不做相应的判断了（也就不作为参数传入函数了）
    # def timer_isnot_running(self, AorB):
    def timer_isnot_running(self):
        q = self.head
        while (q != None and q.evtype != "TIMER_INTERRUPT"):
            q = q.next
        return q == None

evl = event_list()