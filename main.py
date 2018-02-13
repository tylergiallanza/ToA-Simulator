import random

def log(*outputs):
    print(outputs)

class Node(object):
    def __init__(self, name, latency, jitter, window_size, start_time, first_induced_delay, delay_mod, delay_bias):
        self.name = name
        self.latency = latency
        self.jitter = jitter
        self.window_size = window_size
        self.current_time = start_time
        self.incoming_delay = first_induced_delay
        self.outgoing_delay = first_induced_delay
        self.should_rec_time = start_time + latency + first_induced_delay
        self.m = delay_mod
        self.n = delay_bias
        self.partner = None
        self.next_send_time = None

    def rec_message(self, message):
        log(self.name,'recieved message',message,'at',self.current_time)
        log(self.name,'should have recieved message at',self.should_rec_time)
        if abs(self.current_time-self.should_rec_time) <= self.window_size:
            log('message authenticated')
            self.outgoing_delay = message['next_delay']
            self.start_send()
        else:
            log('message could not be authenticated')
            #TODO


    def handle_dropped_packet(self):
        #TODO
        log('should have recieved message by',self.should_rec_time+self.window_size)


    def update(self):
        self.current_time += 1
        if self.current_time > self.should_rec_time + self.window_size:
            self.handle_dropped_packet()
        if self.current_time == self.next_send_time:
            message={'text':'this is a test message'}
            self.send_message(self.partner,message)


    def add_partner(self, other):
        self.partner = other


    def start_send(self):
        self.next_send_time = self.current_time + self.calculate_send_delay()


    def calculate_send_delay(self):
        self.incoming_delay = self.gen_new_delay()
        self.should_rec_time = self.current_time + 2*self.latency + self.outgoing_delay + self.incoming_delay
        return int(random.gauss(self.latency, self.jitter**0.5)) + self.outgoing_delay


    def gen_new_delay(self):
        return random.randint(0,self.m)+self.n


    def send_message(self, other, message):
        message['next_delay'] = self.incoming_delay
        other.rec_message(message)

def run_simulation(latency, jitter, window_size, first_delay, delay_mod, delay_bias, max_time):
    alice = Node('alice',latency, jitter, window_size, 0, first_delay, delay_mod, delay_bias)
    bob = Node('bob',latency, jitter, window_size, 0, first_delay, delay_mod, delay_bias)

    alice.add_partner(bob)
    bob.add_partner(alice)

    alice.start_send()

    t = 0
    while t <= max_time:
        alice.update()
        bob.update()
        t+= 1


l = 1000
j = 10
ws = 20
fd = 100
dm = 100
db = 50
mt = 10000
run_simulation(l,j,ws,fd,dm,db,mt)
#TODO add trudy
