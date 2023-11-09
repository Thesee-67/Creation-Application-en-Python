import time
def task(i):
    print(f"Task {i} starts")
    time.sleep(1)
    print(f"Task {i} ends")

if __name__ == '__main__':
    start = time.perf_counter()

    task(1)

    task(2)

    end = time.perf_counter()

    print(f"Tasks ended in {round(end - start, 2)} second(s)")

import threading
import time
def task(i):
    print(f"Task {i} starts")
    time.sleep(1)
    print(f"Task {i} ends")

start = time.perf_counter()

t1 = threading.Thread(target=task, args=[1]) # création de la thread
t1.start() # je démarre la thread
t1.join() # j'attends la fin de la thread
end = time.perf_counter()

print(f"Tasks ended in {round(end - start, 2)} second(s)")

T = []
for i in range(100):
 T.append(threading.Thread(target=task, args=[i]))
for i in range(len(T)):
 T[i].start()
for i in range(len(T)):
 T[i].join()

 def task(i):
    print(f"Task {i} starts for {i+1} second(s)")
    time.sleep(i+1)
    print(f"Task {i} ends")

T = []

for i in range(100):
    T.append(threading.Thread(target=task, args=[i]))
for i in range(len(T)):
    T[i].start()
for i in range(len(T)):
    T[i].join()
