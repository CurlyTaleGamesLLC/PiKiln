import time
import threading

# https://www.geeksforgeeks.org/python-different-ways-to-kill-a-thread/

def sleeper():
    for x in range(30):
        print(x)
        # print("thread %d sleeps for 30 seconds" % i)
        time.sleep(1)
        global stop_threads 
        if stop_threads: 
            print("thread %d woke up" % x)
            break
  
stop_threads = False
t1 = threading.Thread(target = sleeper) 
t1.start() 
time.sleep(5)
stop_threads = True
t1.join() 
print('thread killed') 