from hazelcast import HazelcastClient
from threading import Thread
import time

def producer(queue):
    try:
        print("Producer started.")
        for i in range(1, 101):  # writingf values from 1 to 100
            queue.put(i)
            print(f"Produced: {i}")
            time.sleep(0.1)
        queue.put("END")  # send an end signal to consumers sasdf\
    except Exception as e:
        print(f"Producer error: {str(e)}")

def consumer(queue, consumer_id):
    try:
        print(f"Consumer {consumer_id} started.")
        while True:
            item = queue.take()
            if item == "END":  # check for end signal
                queue.put("END")  #pass the end signal back for other consumers
                break
            print(f"Consumer {consumer_id} consumed: {item}")
            time.sleep(0.2)  #  processing time simulate
    except Exception as e:
        print(f"Consumer {consumer_id} error: {str(e)}")

def main():
    client = HazelcastClient()
    queue = client.get_queue("bounded-queue").blocking()
    
    producer_thread = Thread(target=producer, args=(queue,))
    consumer_thread_1 = Thread(target=consumer, args=(queue, 1))
    consumer_thread_2 = Thread(target=consumer, args=(queue, 2))
    
    producer_thread.start()
    consumer_thread_1.start()
    consumer_thread_2.start()
    
    producer_thread.join()
    consumer_thread_1.join()
    consumer_thread_2.join()

    client.shutdown()

if __name__ == "__main__":
    main()
