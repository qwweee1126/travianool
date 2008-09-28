import threading, time

class MyThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.count = 0
    
    def run(self):
        print 'hello threading'
        time.sleep(10)
    
if __name__ == '__main__':
    t = MyThread()
    t.start()
    print 'main'
    print threading.activeCount()