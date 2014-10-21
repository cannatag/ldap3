from ldap3 import Server, Connection, STRATEGY_REUSABLE_PARALLEL
from multiprocessing import Process, JoinableQueue, current_process, Lock
from time import sleep
class P(Process):
    def __init__(self, original_connection, queue):
        Process.__init__(self)
        #self.daemon = True
        # self.active_connection = reusable_connection
        self.original_connection = original_connection
        self.q = queue
        print(current_process(), 'init')

    def run(self):
        print(current_process(), 'start')
        while True:
            e = self.q.get()
            if e == 'STOP':
                print(current_process(), 'exiting')
                self.q.task_done()
                break
            print(current_process(), 'get', e)
            self.q.task_done()

if __name__ == '__main__':
    s = Server('edir1')
    s.lock = Lock()
    c = Connection(s, 'cn=admin,o=services', 'password', client_strategy=STRATEGY_REUSABLE_PARALLEL)
    q = JoinableQueue()
    p1 = P(c, q)
    p2 = P(c, q)
    p1.start()
    p2.start()
    sleep(1)
    print(current_process(), 'put', 1)
    q.put('1')
    #c.bind()
    print(current_process(), c)
    sleep(1)
    q.put(2)
    print(current_process(), 'put', 2)
    sleep(1)
    q.put('STOP')
    q.put('STOP')
    p1.join()
    p2.join()
    q.join()


