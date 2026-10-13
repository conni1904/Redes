class CongestionControl:
    def __init__(self, mss: int):
        self.current_state = 0 # 0 es estado de slow start y 1 es congestion avoidance
        self.mss = mss
        self.cwnd = mss
        self.ssthresh = None
        self.primer_timeout = False #si no ha tenido su primer timeout es false en slow start

    def get_cwnd(self):
        return self.cwnd

    def get_MSS_in_cwnd(self):
        return self.get_cwnd()//self.mss #REVISAR

    def event_ack_received(self):
        if self.current_state == 0: #si estamos en slow start
            self.cwnd  += self.mss
            if self.ssthresh !=None and self.cwnd >= self.ssthresh:
                self.current_state = 1
                self.primer_timeout = False
        else:
            self.cwnd += (1/self.get_MSS_in_cwnd())

    def event_timeout(self):
        if self.current_state == 0:
            if self.primer_timeout == False:
                self.primer_timeout = True
                self.ssthresh = self.cwnd / 2
            self.cwnd = self.mss
        else:
            self.current_state = 0
            self.cwnd = self.mss
            self.ssthresh = self.cwnd / 2

    def is_state_slow_start(self):
        return (self.current_state == 0)

    def is_state_congestion_avoidance(self):
        return self.current_state == 1


    def get_ssthresh(self):
        return self.ssthresh
