

class event:
    def __init__(self, evtime, evtype, eventity, pkt=None):
        self.evtime = evtime  # event time
        self.evtype = evtype  # event type code
        self.eventity = eventity  # entity where event occurs it can be either a or b
        self.pkt = pkt  # ptr to packet (if any) assoc w/ this event
        self.prev = None
        self.next = None

    def print_self(self):
        print("Event time:{} , type: {} entity: {}\n".format(self.evtime, self.evtype, self.eventity))