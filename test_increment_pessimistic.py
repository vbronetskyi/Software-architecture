from hazelcast import HazelcastClient
import time

client = HazelcastClient()
my_map = client.get_map("shared-counter").blocking()

# without put_if_absent — counter created previusly = 0

start = time.time()
for _ in range(10_000):
    try:
        my_map.lock("counter")  # lock key
        value = my_map.get("counter")
        value += 1
        my_map.put("counter", value)
    finally:
        my_map.unlock("counter")  # unlovk
end = time.time()

final_value = my_map.get("counter")
print(f"[Pessimistic] Finished in {end - start:.2f}s. Final counter: {final_value}")

client.shutdown()
