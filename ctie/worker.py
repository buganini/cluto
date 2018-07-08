import threading
import multiprocessing

class WorkerDispatcher():
    class Worker(threading.Thread):
        def __init__(self, dispatcher):
            threading.Thread.__init__(self)
            self.dispatcher = dispatcher
            self.go = True

        def stop(self):
            self.go = False

        def run(self):
            while self.dispatcher.core is None:
                with self.dispatcher.mutex:
                    self.dispatcher.cond.wait()

            while self.go:
                done = False

                with self.dispatcher.mutex:
                    try:
                        job = self.dispatcher.fg_todo.pop(0)
                    except:
                        job = None

                if job is None:
                    try:
                        job = self.dispatcher.bg_todo.pop(0)
                    except:
                        job = None

                if job:
                    job()
                    done = True

                if not done:
                    with self.dispatcher.mutex:
                        self.dispatcher.cond.wait()

    def __init__(self, core):
        self.fg_todo = []
        self.bg_todo = []
        self.core = core
        self.mutex = threading.Lock()
        self.cond = threading.Condition(self.mutex)
        self.worker = []
        for i in range(multiprocessing.cpu_count() - 1):
            self.worker.append(self.Worker(self))
        for w in self.worker:
            w.start()

    def reset(self):
        self.mutex.acquire()
        self.fg_todo = []
        self.bg_todo = []
        self.mutex.release()
        with self.mutex:
            self.cond.notify_all()

    def stop(self):
        for w in self.worker:
            w.stop()
        with self.mutex:
            self.cond.notify_all()

    def addFgJob(self, job):
        self.mutex.acquire()
        self.fg_todo.append(job)
        self.mutex.release()
        with self.mutex:
            self.cond.notify_all()

    def addFgJobs(self, jobs):
        self.mutex.acquire()
        self.fg_todo.extend(jobs)
        self.mutex.release()
        with self.mutex:
            self.cond.notify_all()

    def addBgJob(self, job):
        self.mutex.acquire()
        self.bg_todo.append(job)
        self.mutex.release()
        with self.mutex:
            self.cond.notify_all()

    def addBgJobs(self, jobs):
        self.mutex.acquire()
        self.bg_todo.extend(jobs)
        self.mutex.release()
        with self.mutex:
            self.cond.notify_all()