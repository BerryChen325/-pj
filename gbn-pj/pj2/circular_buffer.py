class circular_buffer:
    def __init__(self,max_buffer,window_size):
        self.read=0     # buffer的头
        self.write=0    # buffer的尾
        self.max= max_buffer
        self.N=window_size
        self.count=0
        self.buffer=[]
        self.next_unsent = 0    # 加的，记录第一个未发送过的pkt的位置。next_unsent==(head+N)%max表示窗口里没有未发送的包
        for i in range(max_buffer):
            self.buffer.append(None)

    def push(self,pkt):
        if(self.count==max):
            return -1
        else:
            self.buffer[self.write]=pkt

        self.write=(self.write+1)% self.max
        self.count=self.count+1
        # 不需要更新next_unsent，原因是：
        # 只要window中出现了未发送的包（无论是因为layer5来了新的包还是因为收到ACK发生窗口滑动），
        # 一定会立即处理把window中的包全部发出去。【不妨称这操作为“及时处理”】
        # 所以发生push之前，unsent始终处于window中最后一个包的后一个位置上
        # 如果这个位置仍然在window中，则新的pkt恰好加在它的位置上，在“及时处理”以前，unsent确实应该在这个位置
        # 如果这个位置在window之外（window后面的一个位置），则新加入pkt之后这个位置还是第一个未发送的包的位置
        

    def pop(self):
        if(self.count==0):
            return -1

        temp=self.buffer[self.read]
        self.read=(self.read+1)%self.max
        self.count=self.count-1
        # 既然pop一定是这个包已经被ACK了，所以不影响next_unsent，不用更新

    def read_all(self):
        temp=[]
        read=self.read
        for i in range(self.count):
            temp.append(self.buffer[read])
            read=(read+1)%self.max
        return temp

    def isfull(self):
        if(self.count==self.max):
            return True
        else:
            return False
        
    # 自己加的
    def isempty(self):
        if self.count == 0:
            return True
        return False
    
    def top(self):
        if(self.count != 0):
            return self.buffer[self.read]
    
    # 返回window中第一个未发送的pkt，并更新next_unsent位置【因为返回的pkt一定会被A发送出去（layer5发来新包或收到ACK）】
    def next_unsent_pkt_in_window(self):
        if self.window_has_unsent():
            temp = self.buffer[self.next_unsent]
            # print("[next_unsent_pkt_in_window: next_unsent={}]".format(self.next_unsent))
            self.next_unsent = (self.next_unsent+1) % self.max
            return temp
        else:
            # print("[next_unsent_pkt_in_window: next_unsent={}]".format(self.next_unsent))
            return None
    
    def window_has_unsent(self):
        # print("[window_has_unsent: next_unsent={}]".format(self.next_unsent))
        for i in range(min(self.N, (self.write-self.read+self.max)%self.max)):
            if self.read + i % self.max == self.next_unsent:
                return True
        return False

    # 返回window中所有pkt，并更新next_unsent位置【因为返回的列表中所有pkt都会被A发送出去（超时重传）】
    def read_window(self):
        temp=[]
        read=self.read
        for i in range(min(self.N, (self.write-self.read+self.max)%self.max)):
            temp.append(self.buffer[read])
            read=(read+1)%self.max
        self.next_unsent = read     # 其实似乎不用更新，因为temp里的所有pkt一定都是已经发送过的（因为所有出现新包的情况都会被“及时处理”）
        return temp
