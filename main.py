import random

class Node(object):
    __init__(self, latency, jitter, window_size, start_time, first_induced_delay):
        self.latency = latency
        self.jitter = jitter
        self.window_size = window_size
        self.sent_time = start_time
        self.should_rec_time = start_time + latency
        self.current_time = start_time
        self.next_induced_delay = first_induced_delay

    def rec_message(self, message, next_induced_delay):
        log('recieved message',message,'at',self.current_time)
        log('should have recieved message at',self.should_rec_time)
        if abs(self.current_time-self.should_rec_time) <= self.window_size:
            log('message authenticated')
            self.next_induced_delay = message['next_delay']
        else:
            log('message could not be authenticated')


    def handle_dropped_packet(self):
        log('should have recieved message by',self.should_rec_time+self.window_size)


    def update(self):
        self.current_time += 1
        if self.current_time > self.should_rec_time + self.window_size:
            self.handle_dropped_packet()


    def calculate_send_delay(self, other, induced_delay):
        self.sent_time = self.current_time
        return random.gauss(self.latency, self.jitter**0.5) + induced_delay


    def gen_new_delay(self):
        pass


    def send_message(self, other, message, induced_delay):
        #message['delay_used'] = self.next_induced_delay
        self.next_induced_delay = self.get_new_delay()
        message['next_delay'] = self.next_induced_delay
        other.rec_message(message)
