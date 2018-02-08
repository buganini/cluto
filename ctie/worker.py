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
                        item = self.dispatcher.todo_item.pop(0)
                    except:
                        item = None
                    print("Todo:", len(self.dispatcher.todo_item))

                if item:
                    item.prepare()
                    self.dispatcher.todo_item.extend(item.children)
                    done = True

                if not done:
                    with self.dispatcher.mutex:
                        self.dispatcher.cond.wait()

    def __init__(self, core):
        self.todo_item = []
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
        self.todo_item = []
        self.mutex.release()
        with self.mutex:
            self.cond.notify_all()

    def stop(self):
        for w in self.worker:
            w.stop()
        with self.mutex:
            self.cond.notify_all()

    def addItem(self, item):
        self.mutex.acquire()
        self.todo_item.append(item)
        self.mutex.release()
        with self.mutex:
            self.cond.notify_all()
