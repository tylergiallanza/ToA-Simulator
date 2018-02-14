import random

def log(*outputs):
    '''
    with open('log','a') as f:
        f.write(','.join(map(str,outputs)))
        f.write('\n')
    '''
    #print(outputs)
    pass

num_authed = 0
num_unauthed = 0
num_dropped = 0
num_intrusion = 0
num_intrusion_resolved = 0
num_intrusion_detected = 0
num_dropped_recovered = 0

def log_authed(authed):
    global num_authed
    global num_unauthed
    if authed:
        num_authed += 1
    else:
        num_unauthed += 1

def log_dropped():
    global num_dropped
    num_dropped += 1

def log_intrusion_resolved():
    global num_intrusion_resolved
    num_intrusion_resolved += 1

def log_real_intrusion():
    global num_intrusion_detected
    num_intrusion_detected += 1

def log_dropped_recovered():
    global num_dropped_recovered
    num_dropped_recovered += 1


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
        self.detected_intrusion = False
        self.intrusion_resolved = True
        self.real_intrusion = False
        self.detected_drop = False
        self.drop_resolved = False
        self.message_hash = 'legitimate'
        self.sending_hash = self.message_hash

    def rec_message(self, message):
        log(self.name,'recieved message',message,'at',self.current_time)
        log(self.name,'should have recieved message at',self.should_rec_time)
        if abs(self.current_time-self.should_rec_time) <= self.window_size:
            log('message authenticated by',self.name)
            log_authed(True)
            
            #Check if the partner got an intrusion
            if message['intrusion']:
                #This would actually be hash checking
                if message['hash'] == self.message_hash:
                    log(self.name,'verified last message')
                    self.intrusion_resolved = True
                    log_intrusion_resolved()
                else:
                    log(self.name,'detected intrusion')
                    self.intrusion_resolved = False
                    self.real_intrusion = True
                    log_real_intrusion()
            if message['intrusion_resolved']:
                self.detected_intrusion = False
                self.intrusion_resolved = True

            if message['dropped']:
                #"Resend" the last message

                self.drop_resolved = True
                log_dropped_recovered()
            if message['drop_resolved']:
                self.detected_drop = False
                self.drop_resolved = True

            self.outgoing_delay = message['next_delay']
        else:
            log('message could not be authenticated by ',self.name)
            log_authed(False)
            self.detected_intrusion = True
            self.intrusion_resolved = False
            self.outgoing_delay = message['next_delay']
            self.sending_hash = message['hash']
            #TODO: I think this is why it's not detecting all intrusions
        self.start_send()


    def handle_dropped_packet(self):
        log('dropped: should have recieved message by',self.should_rec_time+self.window_size)
        self.detected_drop = True
        self.drop_resolved = False
        log_dropped()


    def update(self):
        self.current_time += 1
        if (not self.detected_drop) and self.current_time > self.should_rec_time + self.window_size:
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
        self.should_rec_time = self.current_time + 2* self.latency + self.outgoing_delay + self.incoming_delay
        send_time = int(round(random.gauss(self.latency, self.jitter**0.5))) 
        return send_time + self.outgoing_delay


    def gen_new_delay(self):
        return random.randint(0,self.m)+self.n


    def send_message(self, other, message):
        message['next_delay'] = self.incoming_delay
        message['intrusion'] = self.detected_intrusion
        message['intrusion_resolved'] = self.intrusion_resolved
        message['real_intrusion'] = self.real_intrusion
        message['dropped'] = self.detected_drop
        message['drop_resolved'] = self.drop_resolved
        message['hash'] = self.sending_hash
        self.sending_hash = self.message_hash

        #Keep going if there's a real intrusion
        self.real_intrusion = False

        other.rec_message(message)
        self.start_send()

def run_simulation(latency, jitter, window_size, first_delay, delay_mod, delay_bias, max_time, intrusion_prob):
    alice = Node('alice',latency, jitter, window_size, 0, first_delay, delay_mod, delay_bias)
    bob = Node('bob',latency, jitter, window_size, 0, first_delay, delay_mod, delay_bias)

    alice.add_partner(bob)
    bob.add_partner(alice)

    alice.start_send()

    t = 0
    #while t <= max_time:
    global num_intrusion
    global num_authed
    while num_authed < 10000:
        if t % 200000 == 0:
            print(num_authed)
            pass
        alice.update()
        bob.update()
        if random.random() <= intrusion_prob:
            num_intrusion += 1
            trudy_msg = {
                'text':'This is a message from trudy',
                'next_delay':500,
                'intrusion':False,
                'intrusion_resolved':True,
                'real_intrusion':False,
                'dropped':False,
                'drop_resolved':True,
                'hash':'illegitimate'
            }
            if random.random() <= 0.5:
                #alice.rec_message(trudy_msg)
                pass
            else:
                #bob.rec_message(trudy_msg)
                pass
        t+= 1


l = 1000
j = 30
ws = 20
#fd = 1000
#dm = 1000
#db = 500
fd = 100
dm = 100
db = 50
mt = 10000000
intrusion_prob = 0.01
run_simulation(l,j,ws,fd,dm,db,mt,intrusion_prob/l)
print('authed not_authed fixed dropped recovered intrusions intrusions_detected')
print(num_authed,num_unauthed,num_intrusion_resolved,num_dropped,num_dropped_recovered,num_intrusion,num_intrusion_detected)
print('%n',100-num_unauthed/(num_authed+num_unauthed)*100)
print('%auth fixed',num_intrusion_resolved/(num_unauthed)*100)
print('%dropped recovered',num_dropped_recovered/(num_dropped)*100)
print('%intruded',100-num_intrusion_detected/num_intrusion*100)
