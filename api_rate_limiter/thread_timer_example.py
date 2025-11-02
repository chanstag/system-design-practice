import threading
import time

def repeat_with_timer(func, interval):
    def run():
        func()
        timer = threading.Timer(interval, run)
        timer.daemon = True
        timer.start()
        return timer
    return run()

def fun():
   print("hello world!")

timer = repeat_with_timer(fun, 5)

time.sleep(20)

timer.cancel()

time.sleep(20)