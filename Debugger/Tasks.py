
import threading

class ThreadedTaskHandler:

    thread_timeout = 10

    def __init__(self, limit_threads=3):
        self.queue = []
        self.cond = threading.Condition()
        self.running_threads = 0
        self.idle_threads = 0
        self.limit_threads = limit_threads

    def addTask(self, task):
        '''
        task is a callable object which will be executed in another
        thread.
        '''
        self.cond.acquire()
        try:
            self.queue.append(task)
            if self.idle_threads < 1:
                if self.limit_threads < 1 or (self.running_threads
                                              < self.limit_threads):
                    t = threading.Thread(target=self.clientThread)
                    t.setDaemon(1)
                    self.running_threads = self.running_threads + 1
                    t.start()
            self.cond.notify()
        finally:
            self.cond.release()

    def clientThread(self):
        try:
            exitLoop = 0
            while not exitLoop:
                self.cond.acquire()
                try:
                    if len(self.queue) < 1:
                        self.idle_threads = self.idle_threads + 1
                        self.cond.wait(self.thread_timeout)
                        # XXX Can't tell whether actually timed out
                        # our not, therefore idle_threads is managed
                        # is a less than ideal way.
                        self.idle_threads = self.idle_threads - 1
                        if len(self.queue) < 1:
                            # Timed out.
                            exitLoop = 1
                    if not exitLoop:
                        task = self.queue[0]
                        del self.queue[0]
                finally:
                    self.cond.release()

                if not exitLoop:
                    try:
                        task()
                    except SystemExit:
                        exitLoop = 1
                    except:
                        # task ought to do its own error handling,
                        # but sometimes it won't.
                        import traceback
                        traceback.print_exc()
        finally:
            self.running_threads = self.running_threads - 1

if __name__ == '__main__':
    # Self-test.
    import time
    class PrintTask:
        def __init__(self, s):
            self.s = s
        def __call__(self):
            print self.s
    tth = ThreadedTaskHandler()
    for n in range(20):
        tth.addTask(PrintTask(n))
    time.sleep(1)
